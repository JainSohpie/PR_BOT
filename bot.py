import os
import threading
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
        json={"conversation_id": CONV_ID, "text": text},
        timeout=5
    )

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"ok": True})
    
    body = request.get_json(silent=True) or {}
    
    # 버튼 클릭 감지
    if body.get("action_name") == "summarize" or body.get("value") == "summarize":
        # 답장은 백그라운드로 (카카오워크 타임아웃 방지)
        threading.Thread(
            target=send_message,
            args=("✅ 버튼 클릭 확인! 연결 성공!",)
        ).start()
    
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run()
