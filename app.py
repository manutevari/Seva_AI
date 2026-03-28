import os, logging, requests
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

WA_TOKEN        = os.getenv("WA_TOKEN")
WA_PHONE_ID     = os.getenv("WA_PHONE_ID")
WA_VERIFY_TOKEN = os.getenv("WA_VERIFY_TOKEN")

WA_API_URL = f"https://graph.facebook.com/v25.0/{WA_PHONE_ID}/messages"

def send_wa(to, text):
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(WA_API_URL, json=payload, headers=headers)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

def process(msg):
    if "hi" in msg.lower():
        return "🙏 Welcome to CSC Service Bot"
    return llm.invoke([HumanMessage(content=msg)]).content

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == WA_VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        mobile = msg["from"]
        text = msg["text"]["body"]

        reply = process(text)
        send_wa(mobile, reply)

    except Exception as e:
        log.warning(e)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
