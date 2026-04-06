from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def home():
    return "Server Running"

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("uploads", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Server Working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
