from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import RPi.GPIO as GPIO
import time
from Alphabot import AlphaBot

# ======================
# SETUP GPIO
# ======================
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.IN)  # sensore sinistro
GPIO.setup(16, GPIO.IN)  # sensore destro

# ======================
# APP FLASK
# ======================
app = Flask(__name__)
app.secret_key = "admin"

# Credenziali
USERNAME = "admin"
PASSWORD = "alphabot"

# Inizializza robot
alphabot = AlphaBot()
alphabot.stop()

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form.get("username") == USERNAME and
            request.form.get("password") == PASSWORD):
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Credenziali errate")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    alphabot.stop()
    return redirect(url_for("login"))

# ======================
# HOME
# ======================
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

# ======================
# MOVIMENTO
# ======================
@app.route("/move", methods=["POST"])
def move():
    if not session.get("logged_in"):
        return jsonify({"status": "error"}), 401

    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"status": "error"}), 400

    command = data["command"]

    # Forme dal database
    if command in ["triangolo", "cerchio", "quadrato"]:
        conn = sqlite3.connect("istruzioniAlpha.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cod FROM istruzioni WHERE nome = ?", (command,))
        result = cursor.fetchone()
        conn.close()

        if result:
            command = result[0]

    # Comandi movimento
    if command == "W":
        alphabot.forward()
        action = "forward"
    elif command == "S":
        alphabot.backward()
        action = "backward"
    elif command == "A":
        alphabot.left()
        action = "left"
    elif command == "D":
        alphabot.right()
        action = "right"
    elif command == "STOP":
        alphabot.stop()
        action = "stop"
    elif command == 1:
        alphabot.triangolo()
        action = "triangolo"
    elif command == 2:
        alphabot.quadrato()
        action = "quadrato"
    elif command == 3:
        alphabot.cerchio()
        action = "cerchio"
    else:
        return jsonify({"status": "error"}), 400

    return jsonify({"status": "ok", "action": action})

# ======================
# OSTACOLI
# ======================
def ostacolo():
    if GPIO.input(19) == 0:
        alphabot.stop()
        time.sleep(0.5)
        alphabot.backward()
        time.sleep(0.5)
        alphabot.right()
        time.sleep(0.5)

    if GPIO.input(16) == 0:
        alphabot.stop()
        time.sleep(0.5)
        alphabot.backward()
        time.sleep(0.5)
        alphabot.left()
        time.sleep(0.5)

# ======================
# AVVIO
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)