import os
import re
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import requests as http_requests

app = Flask(__name__)

BOT_TOKEN     = os.environ.get("BOT_TOKEN")
CLAUDE_KEY    = os.environ.get("CLAUDE_KEY")

# Microsoft / Teams 설정
MS_TENANT_ID     = os.environ.get("MS_TENANT_ID")
MS_CLIENT_ID     = os.environ.get("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")
# Teams 채널 파일 탭에 연결된 SharePoint 드라이브 정보
# Graph Explorer로 확인: GET /v1.0/teams/{team-id}/channels/{channel-id}/filesFolder
TEAMS_TEAM_ID    = os.environ.get("TEAMS_TEAM_ID")
TEAMS_CHANNEL_ID = os.environ.get("TEAMS_CHANNEL_ID")
SP_SITE_ID       = os.environ.get("SP_SITE_ID")
SP_DRIVE_ID      = os.environ.get("SP_DRIVE_ID")
SP_ITEM_ID       = os.environ.get("SP_ITEM_ID")   # Excel 파일의 driveItem ID
SP_TABLE_NAME    = os.environ.get("SP_TABLE_NAME", "Table1")


# ============================================================
# 기간 기본값: 직전 목~수 자동 계산
# ============================================================
def get_default_date_range():
    today = datetime.now()
    weekday = today.weekday()          # 0=월 … 6=일
    days_since_wed = (weekday - 2) % 7
    if days_since_wed == 0 and today.hour < 18:
        days_since_wed = 7
    end   = today - timedelta(days=days_since_wed)
    start = end   - timedelta(days=6)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')


# ============================================================
# 카톡 txt 날짜 필터링
# ============================================================
def filter_by_date(text, start_date, end_date):
    if not start_date and not end_date:
        return text
    date_pattern = r'-+ (\d{4})년 (\d{1,2})월 (\d{1,2})일.*?-+'
    lines = text.split('\n')
    filtered, include = [], False
    for line in lines:
        m = re.search(date_pattern, line)
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            cur = f"{y:04d}-{mo:02d}-{d:02d}"
            include = True
            if start_date and cur < start_date:
                include = False
            if end_date   and cur > end_date:
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
# Claude API 분석  ★ 개선된 프롬프트
# ============================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data       = request.get_json()
    text       = data.get("text", "")
    start_date = data.get("start_date", "")
    end_date   = data.get("end_date", "")

    if not text.strip():
        return jsonify({"error": "텍스트를 입력해주세요"}), 400
    if not CLAUDE_KEY:
        return jsonify({"error": "CLAUDE_KEY 환경변수가 설정되지 않았습니다"}), 500

    text = filter_by_date(text, start_date, end_date)

    prompt = f"""아래는 홍보그룹 카카오톡 업무방에서 내보내기한 대화 내용입니다.
이 대화에서 부정보도 조치 건을 추출하여 JSON 배열로 반환해주세요.

각 건마다 다음 필드를 추출하세요:

- report_date   : 보도일자 (YYYY-MM-DD, 대화 맥락에서 추정. 없으면 null)
- action_date   : 조치일자 (YYYY-MM-DD, 조치 완료 메시지 기준. 없으면 null)
- media         : 매체명 (예: 한국경제, 머니투데이 등)
- reporter      : 기자명 (없으면 null)

- article_title : ★ 기사 제목 (대화에서 언급된 실제 제목 그대로. 없으면 그럴듯하게 유추해서 작성.
                  반드시 신문기사 제목 형식으로 작성. 예: "포스코이앤씨, 강남 재개발 현장 하자 분쟁 확산")

- issue_summary : ★ 이슈 요약 (article_title과 별개. 어떤 리스크가 있었는지 1줄 요약.
                  예: "재개발 현장 하자 분쟁 관련 부정보도 — 회사 이미지 훼손 우려")

- action_type   : 조치유형 (다음 중 하나만 사용)
                  "비보도조치" | "제목 및 내용수정" | "회사명삭제" | "회사입장반영" | "정정보도요청" | "기타"

- action_detail : ★ 조치 내용 상세 (action_type과 함께 표시될 설명.
                  예: "기사 제목 내 회사명을 '일부 건설사'로 수정 완료"
                       "취재기자와 비보도 협의 완료, 미게재 확인"
                       "정정보도 요청 공문 발송 완료, 기자 확인 중")

- is_non_coverage : 비보도조치 여부 (true/false)

주의사항:
- 앞뒤 맥락으로 이어지는 대화는 하나의 건으로 묶어주세요
- 같은 매체·기자 건은 최종 조치 결과 기준으로 1건으로 정리하세요
- 제목수정·내용수정은 모두 "제목 및 내용수정"으로 통합하세요
- 단순 대화·인사·확인 메시지 등 부정보도 조치와 무관한 내용은 무시하세요
- article_title은 절대 issue_summary와 동일하게 작성하지 마세요 (두 필드는 역할이 다릅니다)

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
        result  = response.json()
        ai_text = result["content"][0]["text"]

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
            "error": "AI 응답을 JSON으로 파싱하지 못했습니다."
        })
    except Exception as e:
        return jsonify({"error": f"분석 중 오류: {str(e)}"}), 500


# ============================================================
# Microsoft Graph 공통: Access Token 발급
# ============================================================
def get_ms_token():
    url = f"https://login.microsoftonline.com/{MS_TENANT_ID}/oauth2/v2.0/token"
    r = http_requests.post(url, data={
        "grant_type":    "client_credentials",
        "client_id":     MS_CLIENT_ID,
        "client_secret": MS_CLIENT_SECRET,
        "scope":         "https://graph.microsoft.com/.default"
    }, timeout=15)
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError(f"Azure AD 인증 실패: {r.text}")
    return token


# ============================================================
# Teams 채널 파일탭 → Excel에 행 추가
# 사전 조건:
#   1) SP_ITEM_ID : Teams 파일탭의 Excel 파일 driveItem ID
#   2) SP_TABLE_NAME : Excel 내 테이블명 (기본 Table1)
#   3) Excel 테이블 컬럼 순서(좌→우):
#      보도일 | 조치일 | 매체 | 기자 | 기사제목 | 이슈요약
#      | 조치유형 | 조치내용상세 | 비보도여부
# ============================================================
@app.route("/save-to-teams", methods=["POST"])
def save_to_teams():
    if not all([MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET, SP_SITE_ID, SP_DRIVE_ID, SP_ITEM_ID]):
        return jsonify({
            "error": (
                "Teams 연동 환경변수가 부족합니다. "
                "MS_TENANT_ID / MS_CLIENT_ID / MS_CLIENT_SECRET / "
                "SP_SITE_ID / SP_DRIVE_ID / SP_ITEM_ID 를 설정해주세요."
            )
        }), 400

    data  = request.get_json()
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "저장할 항목이 없습니다"}), 400

    try:
        token   = get_ms_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json"
        }

        # Teams 파일탭 Excel은 SharePoint Drive에 저장됨
        # Graph API: /sites/{site-id}/drives/{drive-id}/items/{item-id}/workbook/tables/{table}/rows/add
        base_url = (
            f"https://graph.microsoft.com/v1.0"
            f"/sites/{SP_SITE_ID}"
            f"/drives/{SP_DRIVE_ID}"
            f"/items/{SP_ITEM_ID}"
            f"/workbook/tables/{SP_TABLE_NAME}/rows/add"
        )

        saved, errors = 0, []
        for item in items:
            row = {
                "values": [[
                    item.get("report_date",   "") or "",
                    item.get("action_date",   "") or "",
                    item.get("media",         "") or "",
                    item.get("reporter",      "") or "",
                    item.get("article_title", "") or "",   # ★ 기사제목
                    item.get("issue_summary", "") or "",   # ★ 이슈요약 (분리)
                    item.get("action_type",   "") or "",   # ★ 조치유형
                    item.get("action_detail", "") or "",   # ★ 조치내용 상세
                    "Y" if item.get("is_non_coverage") else "N"
                ]]
            }
            r = http_requests.post(base_url, headers=headers, json=row, timeout=15)
            if r.status_code in [200, 201]:
                saved += 1
            else:
                errors.append(f"{item.get('media','?')} — {r.status_code}: {r.text[:120]}")

        return jsonify({
            "success": True,
            "saved":   saved,
            "total":   len(items),
            "errors":  errors
        })

    except Exception as e:
        return jsonify({"error": f"Teams 파일 저장 중 오류: {str(e)}"}), 500


# ============================================================
# (선택) Teams 채널 메시지로 요약 전송
# ============================================================
@app.route("/notify-teams", methods=["POST"])
def notify_teams():
    if not all([MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET, TEAMS_TEAM_ID, TEAMS_CHANNEL_ID]):
        return jsonify({"error": "Teams 알림 환경변수가 부족합니다"}), 400

    data  = request.get_json()
    items = data.get("items", [])
    start = data.get("start_date", "")
    end   = data.get("end_date",   "")

    try:
        token   = get_ms_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json"
        }

        non_cov = sum(1 for i in items if i.get("is_non_coverage"))
        rows_html = "".join(
            f"<tr>"
            f"<td>{i.get('report_date','')}</td>"
            f"<td><b>{i.get('media','')}</b> {i.get('reporter','')} 기자</td>"
            f"<td>{i.get('article_title','')}</td>"
            f"<td>{i.get('action_type','')}</td>"
            f"<td>{i.get('action_detail','')}</td>"
            f"</tr>"
            for i in items
        )

        html_body = f"""
<h2>📊 주간 부정보도 조치 현황 ({start} ~ {end})</h2>
<p>총 <b>{len(items)}건</b> 처리 / 비보도 조치 <b>{non_cov}건</b></p>
<table>
  <tr><th>보도일</th><th>매체/기자</th><th>기사제목</th><th>조치유형</th><th>조치내용</th></tr>
  {rows_html}
</table>
<p><i>포사원 AI 자동 분석</i></p>
"""
        msg_url = (
            f"https://graph.microsoft.com/v1.0"
            f"/teams/{TEAMS_TEAM_ID}/channels/{TEAMS_CHANNEL_ID}/messages"
        )
        r = http_requests.post(msg_url, headers=headers, json={
            "body": {"contentType": "html", "content": html_body}
        }, timeout=15)

        if r.status_code in [200, 201]:
            return jsonify({"success": True, "message": "Teams 채널에 전송 완료"})
        else:
            return jsonify({"error": f"Teams 전송 실패: {r.status_code} {r.text[:200]}"}), 500

    except Exception as e:
        return jsonify({"error": f"Teams 알림 오류: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
