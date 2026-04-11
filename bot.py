import os
import re
import json
import threading
from datetime import datetime, timedelta
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
# 기간 기본값: 직전 목~수 자동 계산
# ============================================================
def get_default_date_range():
    today = datetime.now()
    weekday = today.weekday()  # 0=월 1=화 2=수 3=목 4=금 5=토 6=일
    # 가장 최근 수요일 찾기
    days_since_wed = (weekday - 2) % 7
    if days_since_wed == 0 and today.hour < 18:
        days_since_wed = 7
    end = today - timedelta(days=days_since_wed)
    # 그 전주 목요일
    start = end - timedelta(days=6)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')


# ============================================================
# 카톡 txt 날짜 필터링
# ============================================================
def filter_by_date(text, start_date, end_date):
    if not start_date and not end_date:
        return text

    date_pattern = r'-+ (\d{4})년 (\d{1,2})월 (\d{1,2})일.*?-+'
    lines = text.split('\n')
    filtered = []
    current_date = None
    include = False

    for line in lines:
        match = re.search(date_pattern, line)
        if match:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            current_date = f"{y:04d}-{m:02d}-{d:02d}"
            include = True
            if start_date and current_date < start_date:
                include = False
            if end_date and current_date > end_date:
                include = False

        if include:
            filtered.append(line)

    return '\n'.join(filtered) if filtered else text


# ============================================================
# 메인 대시보드
# ============================================================
@app.route("/")
def dashboard():
    start, end = get_default_date_range()
    return render_template("dashboard.html", default_start=start, default_end=end)


# ============================================================
# Claude API로 텍스트 분석
# ============================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    start_date = data.get("start_date", "")
    end_date = data.get("end_date", "")

    if not text.strip():
        return jsonify({"error": "텍스트를 입력해주세요"}), 400

    if not CLAUDE_KEY:
        return jsonify({"error": "CLAUDE_KEY 환경변수가 설정되지 않았습니다"}), 500

    # 기간 필터링
    text = filter_by_date(text, start_date, end_date)

    prompt = f"""아래는 홍보그룹 카카오톡 업무방에서 내보내기한 대화 내용입니다.
이 대화에서 부정보도 조치 건을 추출하여 JSON 배열로 반환해주세요.

각 건마다 다음 필드를 추출하세요:
- report_date: 보도일자 (YYYY-MM-DD 형식, 대화 맥락에서 추정, 없으면 null)
- action_date: 조치일자 (YYYY-MM-DD 형식, 조치 완료 메시지 기준, 없으면 null)
- media: 매체명 (예: 한국경제, 매일경제, 머니투데이 등)
- reporter: 기자명 (없으면 null)
- title: 기사 제목 (대화에서 언급된 경우 그대로, 없으면 null)
- issue: 이슈 요약 (어떤 내용의 보도/취재인지 1줄 요약)
- action_type: 조치유형 (다음 중 하나만 사용: "비보도조치", "제목 및 내용수정", "회사명삭제", "회사입장반영", "기타")
- action_detail: 조치 상세 내용 (간단히)
- is_non_coverage: 비보도조치 여부 (true/false)

주의사항:
- 카톡 대화는 시간순으로 나열되어 있습니다
- "취재 문의가 왔습니다" → 이후 "비보도 조치했습니다" 처럼 앞뒤 맥락으로 이어지는 대화는 하나의 건으로 묶어주세요
- 같은 매체·기자에 대해 여러 메시지가 있으면 최종 조치 결과를 기준으로 1건으로 정리하세요
- 제목수정, 내용수정은 모두 "제목 및 내용수정"으로 통합 분류하세요
- 단순 대화("확인했습니다", "네 알겠습니다", 인사 등)는 무시하세요
- 부정보도 조치와 무관한 일반 업무 대화도 무시하세요

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
            timeout=60
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
# SharePoint 자동 입력 (Power Automate 경유)
# ============================================================
@app.route("/save-to-sharepoint", methods=["POST"])
def save_to_sharepoint():
    pa_url = os.environ.get("POWER_AUTOMATE_URL")
    if not pa_url:
        return jsonify({
            "error": "POWER_AUTOMATE_URL 환경변수가 설정되지 않았습니다."
        }), 400

    data = request.get_json()
    items = data.get("items", [])

    saved_count = 0
    errors = []

    for item in items:
        try:
            resp = http_requests.post(
                pa_url,
                json={
                    "report_date": item.get("report_date", ""),
                    "media": item.get("media", ""),
                    "reporter": item.get("reporter", ""),
                    "title": item.get("title", ""),
                    "issue": item.get("issue", ""),
                    "action_type": item.get("action_type", ""),
                    "action_detail": item.get("action_detail", ""),
                    "is_non_coverage": item.get("is_non_coverage", False)
                },
                timeout=30
            )
            if resp.status_code in [200, 201, 202]:
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
