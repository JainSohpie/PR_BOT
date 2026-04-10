import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CLAUDE_KEY = os.environ.get("CLAUDE_KEY")
CONV_ID = os.environ.get("CONV_ID", "962674071608677")

def ask_claude(text):
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": CLAUDE_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": "홍보팀 이슈 분류 어시스턴트입니다. 입력된 대화에서 이슈를 추출해 정리해주세요.\n\n【이슈 요약】\n【유형】언론대응 / 내부보고 / 현장이슈 / 기타\n【필요 액션】",
            "messages": [{"role": "user", "content": f"아래 대화에서 이슈를 정리해줘:\n\n{text}"}]
        }
    )
    return res.json()["content"][0]["text"]

def send_message(text):
    requests.post(
        "https://api.kakaowork.com/v1/messages.send",
        headers={
            "Authorization": f"Bearer {BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"conversation_id": CONV_ID, "text": text}
    )

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"ok": True})

    body = request.get_json(silent=True) or {}

    # Request URL - Modal 팝업 응답
    if body.get("action_name") == "이슈 입력하기" or body.get("value") == "open_modal":
        return jsonify({
            "view": {
                "title": "이슈 입력",
                "accept": "분석하기",
                "decline": "취소",
                "blocks": [
                    {
                        "type": "label",
                        "text": "카카오톡/워크 대화 내용을 붙여넣으세요",
                        "markdown": False
                    },
                    {
                        "type": "input",
                        "block_id": "issue_text",
                        "label": "대화 내용",
                        "placeholder": "대화 내용을 여기에 붙여넣으세요...",
                        "required": True
                    }
                ]
            }
        })

    # Callback URL - Modal 제출 처리
    if "actions" in body or "submission" in body:
        submission = body.get("submission", body.get("actions", {}))
        issue_text = submission.get("issue_text", "")

        if issue_text:
            result = ask_claude(issue_text)
            send_message(f"📋 이슈 정리 결과\n\n{result}")

        return jsonify({"ok": True})

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
