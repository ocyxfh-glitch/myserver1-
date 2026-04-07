from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        text TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/all_users")
    return redirect("/login")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return """
    <h2>Register</h2>
    <form method='POST'>
    <input name='username'><br>
    <input name='password' type='password'><br>
    <button>Register</button>
    </form>
    """

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/all_users")
        else:
            return "Invalid login"

    return """
    <h2>Login</h2>
    <form method='POST'>
    <input name='username'><br>
    <input name='password' type='password'><br>
    <button>Login</button>
    </form>
    """

# ---------- USERS ----------
@app.route("/users")
def users():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT username FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([r[0] for r in rows])

@app.route("/all_users")
def all_users():
    return render_template("users.html")

# ---------- SEND REQUEST ----------
@app.route("/send_request", methods=["POST"])
def send_request():
    sender = session.get("user")
    receiver = request.json["to"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO requests (sender, receiver, status) VALUES (?, ?, ?)",
              (sender, receiver, "pending"))
    conn.commit()
    conn.close()

    return jsonify({"status": "request sent"})

# ---------- ACCEPT REQUEST ----------
@app.route("/accept_request", methods=["POST"])
def accept_request():
    me = session.get("user")
    sender = request.json["from"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("UPDATE requests SET status='accepted' WHERE sender=? AND receiver=?",
              (sender, me))
    conn.commit()
    conn.close()

    return jsonify({"status": "accepted"})

# ---------- GET REQUESTS ----------
@app.route("/my_requests")
def my_requests():
    me = session.get("user")

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT sender FROM requests WHERE receiver=? AND status='pending'", (me,))
    rows = c.fetchall()
    conn.close()

    return jsonify([r[0] for r in rows])

# ---------- PRIVATE CHAT ----------
@app.route("/chat/<user>")
def private_chat(user):
    return render_template("private.html", other=user)

# ---------- SEND MESSAGE ----------
@app.route("/send_private", methods=["POST"])
def send_private():
    sender = session.get("user")
    receiver = request.json["to"]
    text = request.json["text"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    # CHECK permission
    c.execute("""
    SELECT * FROM requests 
    WHERE ((sender=? AND receiver=?) OR (sender=? AND receiver=?))
    AND status='accepted'
    """, (sender, receiver, receiver, sender))

    allowed = c.fetchone()

    if not allowed:
        return jsonify({"status": "not allowed"})

    c.execute("INSERT INTO private_messages (sender, receiver, text) VALUES (?, ?, ?)",
              (sender, receiver, text))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# ---------- GET MESSAGES ----------
@app.route("/get_private/<user>")
def get_private(user):
    me = session.get("user")

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
    SELECT sender, text FROM private_messages
    WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
    """, (me, user, user, me))

    rows = c.fetchall()
    conn.close()

    return jsonify(rows)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run()
