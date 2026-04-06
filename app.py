from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

DB = "messages.db"

# Create table
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

# Send message
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    text = data["text"]
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO messages (text, time) VALUES (?, ?)", (text, time))
    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})

# Get messages
@app.route("/messages")
def get_messages():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT text, time FROM messages ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({"text": r[0], "time": r[1]})

    return jsonify(data)

# Render port fix
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
