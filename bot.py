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
        json={"conversation_id": CONV_ID, "text": text},
        timeout=3   # ← 추가: 3초 안에 응답 없으면 포기
    )

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"ok": True})
    
    # ⭐ 일단 아무것도 안 하고 즉시 응답만 돌려주기
    return jsonify({"ok": True})
