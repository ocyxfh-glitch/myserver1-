from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

messages = []

@app.route("/")
def home():
    return render_template("index.html")

# Send message
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()

    msg = {
        "text": data["text"],
        "time": datetime.now().strftime("%H:%M:%S")
    }

    messages.append(msg)
    return jsonify({"status": "sent"})

# Get messages
@app.route("/messages")
def get_messages():
    return jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
