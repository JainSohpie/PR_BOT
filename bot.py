import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CLAUDE_KEY = os.environ.get("CLAUDE_KEY")
CONV_ID = os.environ.get("CONV_ID", "962674071608677")

buffers = {}

def ask_claude(messages):
    conversation = "\n".join(messages)
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
            "messages": [{"role": "user", "content": f"아래 대화에서 이슈를 정리해줘:\n\n{conversation}"}]
        }
    )
    return res.json()["content"][0]["text"]

def reply(text):
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

    if "challenge" in body:
        return jsonify({"challenge": body["challenge"]})

    if body.get("type") == "message":
        msg = body.get("message", {})
        text = msg.get("text", "")
        sender = msg.get("sender", {}).get("name", "누군가")

        if CONV_ID not in buffers:
            buffers[CONV_ID] = []

        if "정리해줘" in text:
            if buffers[CONV_ID]:
                result = ask_claude(buffers[CONV_ID])
                reply(f"📋 이슈 정리\n\n{result}")
                buffers[CONV_ID] = []
            else:
                reply("아직 쌓인 대화가 없어요.")
        else:
            buffers[CONV_ID].append(f"{sender}: {text}")

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
