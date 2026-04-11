import os
import json
import threading
from flask import Flask, request, jsonify, render_template
import requests as http_requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CLAUDE_KEY = os.environ.get("CLAUDE_KEY")
CONV_ID = os.environ.get("CONV_ID", "962674071608677")

# SharePoint 설정 (나중에 환경변수로 추가)
MS_TENANT_ID = os.environ.get("MS_TENANT_ID")
MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")
SP_SITE_ID = os.environ.get("SP_SITE_ID")
SP_DRIVE_ID = os.environ.get("SP_DRIVE_ID")

# ============================================================
# 메인 대시보드
# ============================================================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# ============================================================
# Claude API로 텍스트 분석
# ============================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "텍스트를 입력해주세요"}), 400

    if not CLAUDE_KEY:
        return jsonify({"error": "CLAUDE_KEY 환경변수가 설정되지 않았습니다"}), 500

    prompt = f"""아래는 홍보그룹 카카오톡 업무방에서 복사한 부정보도 조치 대화 내용입니다.
이 대화에서 부정보도 조치 건을 추출하여 JSON 배열로 반환해주세요.

각 건마다 다음 필드를 추출하세요:
- date: 보도일 또는 조치일 (YYYY-MM-DD 형식, 추정 가능하면 추정, 없으면 null)
- media: 매체명 (예: 한국경제, 매일경제, 머니투데이 등)
- reporter: 기자명 (없으면 null)
- title: 기사 제목 (언급된 경우, 없으면 이슈 요약)
- action_type: 조치유형 (다음 중 하나: "비보도조치", "제목수정", "회사명삭제", "내용수정", "회사입장반영", "기타")
- action_detail: 조치 상세 내용 (간단히)
- is_non_coverage: 비보도조치 여부 (true/false)

반드시 JSON 배열만 반환하세요. 다른 텍스트 없이 순수 JSON만 출력하세요.

카톡 대화 내용:
{text}"""

    try:
        response = http_requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )

        result = response.json()
        ai_text = result["content"][0]["text"]

        # JSON 파싱 (```json 감싸기 제거)
        clean = ai_text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1]
        if clean.endswith("```"):
            clean = clean.rsplit("```", 1)[0]
        clean = clean.strip()

        items = json.loads(clean)

        return jsonify({
            "success": True,
            "items": items,
            "count": len(items),
            "non_coverage_count": sum(1 for i in items if i.get("is_non_coverage"))
        })

    except json.JSONDecodeError:
        return jsonify({
            "success": True,
            "items": [],
            "raw": ai_text,
            "error": "AI 응답을 JSON으로 파싱하지 못했습니다. 원문을 확인해주세요."
        })
    except Exception as e:
        return jsonify({"error": f"분석 중 오류: {str(e)}"}), 500

# ============================================================
# SharePoint 자동 입력
# ============================================================
@app.route("/save-to-sharepoint", methods=["POST"])
def save_to_sharepoint():
    if not all([MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET]):
        return jsonify({
            "error": "SharePoint 연동이 아직 설정되지 않았습니다. MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET 환경변수를 추가해주세요."
        }), 400

    data = request.get_json()
    items = data.get("items", [])

    try:
        # 1. Azure AD 토큰 발급
        token_url = f"https://login.microsoftonline.com/{MS_TENANT_ID}/oauth2/v2.0/token"
        token_resp = http_requests.post(token_url, data={
            "grant_type": "client_credentials",
            "client_id": MS_CLIENT_ID,
            "client_secret": MS_CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default"
        }, timeout=10)
        access_token = token_resp.json().get("access_token")

        if not access_token:
            return jsonify({"error": "Azure AD 인증 실패"}), 500

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        saved_count = 0
        errors = []

        for item in items:
            try:
                # Graph API로 SharePoint 리스트에 행 추가
                # 실제 엔드포인트는 SharePoint 구조에 따라 조정 필요
                graph_url = f"https://graph.microsoft.com/v1.0/sites/{SP_SITE_ID}/drive/items/{SP_DRIVE_ID}/workbook/tables/Table1/rows/add"

                row_data = {
                    "values": [[
                        item.get("date", ""),
                        item.get("media", ""),
                        item.get("reporter", ""),
                        item.get("title", ""),
                        item.get("action_type", ""),
                        item.get("action_detail", ""),
                        "Y" if item.get("is_non_coverage") else "N"
                    ]]
                }

                resp = http_requests.post(graph_url, headers=headers, json=row_data, timeout=10)
                if resp.status_code in [200, 201]:
                    saved_count += 1
                else:
                    errors.append(f"{item.get('media','')}: {resp.status_code}")
            except Exception as e:
                errors.append(f"{item.get('media','')}: {str(e)}")

        return jsonify({
            "success": True,
            "saved": saved_count,
            "total": len(items),
            "errors": errors
        })

    except Exception as e:
        return jsonify({"error": f"SharePoint 저장 중 오류: {str(e)}"}), 500

# ============================================================
# 카카오워크 웹훅 (기존 유지)
# ============================================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"ok": True})
    body = request.get_json(silent=True) or {}
    if body.get("action_name") == "summarize" or body.get("value") == "summarize":
        def send_msg():
            http_requests.post(
                "https://api.kakaowork.com/v1/messages.send",
                headers={"Authorization": f"Bearer {BOT_TOKEN}", "Content-Type": "application/json"},
                json={"conversation_id": CONV_ID, "text": "✅ 버튼 클릭 확인! 연결 성공!"},
                timeout=5
            )
        threading.Thread(target=send_msg).start()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
