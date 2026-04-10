import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CLAUDE_KEY = os.environ.get("CLAUDE_KEY")
CONV_ID = os.environ.get("CONV_ID", "962674071608677")

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

    # 버튼 클릭 테스트
    if body.get("action_name") == "summarize" or body.get("value") == "summarize":
        send_message("✅ 버튼 클릭 확인! 연결 성공!")
        return jsonify({"ok": True})

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
