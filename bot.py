import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CLAUDE_KEY = os.environ.get("CLAUDE_KEY")
CONV_ID = os.environ.get("CONV_ID", "962674071608677")

buffers = {}

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

def send_button_card():
    requests.post(
        "https://api.kakaowork.com/v1/messages.send",
        headers={
            "Authorization": f"Bearer {BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "conversation_id": CONV_ID,
            "text": "이슈를 정리할까요?",
            "blocks": [
                {
                    "type": "text",
                    "text": "📋 *이슈봇*\n대화 내용을 분석해서 이슈를 정리해드립니다.",
                    "markdown": True
                },
                {
                    "type": "button",
                    "text": "이슈 정리하기",
                    "style": "primary",
                    "action_type": "submit_action",
                    "action_name": "summarize",
                    "value": "summarize"
                }
            ]
        }
    )

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"ok": True})

    body = request.get_json(silent=True) or {}

    # Callback URL - 버튼 클릭 처리
    if body.get("action_name") == "summarize" or body.get("value") == "summarize":
        if buffers.get(CONV_ID):
            conversation = "\n".join(buffers[CONV_ID])
            result = ask_claude(conversation)
            send_message(f"📋 이슈 정리 결과\n\n{result}")
            buffers[CONV_ID] = []
        else:
            send_message("아직 쌓인 대화가 없어요. 먼저 대화를 나눠주세요!")
        return jsonify({"ok": True})

    # 일반 메시지 처리
    if body.get("type") == "message":
        msg = body.get("message", {})
        text = msg.get("text", "")
        sender = msg.get("sender", {}).get("name", "누군가")

        if CONV_ID not in buffers:
            buffers[CONV_ID] = []

        buffers[CONV_ID].append(f"{sender}: {text}")

    return jsonify({"ok": True})

@app.route("/send_card", methods=["GET"])
def send_card():
    send_button_card()
    return jsonify({"ok": True, "message": "버튼 카드 전송 완료"})

if __name__ == "__main__":
    app.run()
