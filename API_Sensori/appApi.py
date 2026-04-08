from flask import Flask, request, jsonify, session, redirect, url_for
import sqlite3
import RPi.GPIO as GPIO
import time
from Alphabot import AlphaBot
from flasgger import Swagger
from functools import wraps
 
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
swagger = Swagger(app)
 
# Credenziali hardcoded (come nella versione originale)
USERNAME = "admin"
PASSWORD = "alphabot"
 
# Inizializza robot
alphabot = AlphaBot()
alphabot.stop()
 
DB = "istruzioniAlpha.db"
 
def get_db():
    return sqlite3.connect(DB)
 
 
# ======================
# DECORATORE AUTH
# ======================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"errore": "Non autenticato"}), 401
        return f(*args, **kwargs)
    return decorated
 
 
# ======================
# AUTH API
# ======================
@app.route('/api/login', methods=['POST'])
def login():
    """
    Login utente
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login riuscito
      401:
        description: Credenziali errate
    """
    data = request.json
    if not data:
        return jsonify({"errore": "Dati mancanti"}), 400
 
    username = data.get("username")
    password = data.get("password")
 
    if username == USERNAME and password == PASSWORD:
        session["logged_in"] = True
        return jsonify({"messaggio": "Login effettuato"})
 
    return jsonify({"errore": "Credenziali non valide"}), 401
 
 
@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """
    Logout
    ---
    responses:
      200:
        description: Logout effettuato
    """
    session.clear()
    alphabot.stop()
    return jsonify({"messaggio": "Logout effettuato"})
 
 
# ======================
# SENSORI API
# ======================
@app.route('/api/sensori', methods=['GET'])
@login_required
def stato_sensori():
    """
    Stato sensori ostacoli (sinistro e destro)
    ---
    responses:
      200:
        description: Stato attuale dei sensori GPIO
        schema:
          type: object
          properties:
            sensore_sinistro:
              type: object
              properties:
                pin:
                  type: integer
                valore:
                  type: integer
                ostacolo:
                  type: boolean
            sensore_destro:
              type: object
              properties:
                pin:
                  type: integer
                valore:
                  type: integer
                ostacolo:
                  type: boolean
    """
    sin_val = GPIO.input(19)
    des_val = GPIO.input(16)
 
    return jsonify({
        "sensore_sinistro": {
            "pin": 19,
            "valore": sin_val,
            "ostacolo": sin_val == 0
        },
        "sensore_destro": {
            "pin": 16,
            "valore": des_val,
            "ostacolo": des_val == 0
        }
    })
 
 
@app.route('/api/sensori/sinistro', methods=['GET'])
@login_required
def sensore_sinistro():
    """
    Stato sensore sinistro (pin 19)
    ---
    responses:
      200:
        description: Stato sensore sinistro
    """
    val = GPIO.input(19)
    return jsonify({
        "pin": 19,
        "valore": val,
        "ostacolo": val == 0
    })
 
 
@app.route('/api/sensori/destro', methods=['GET'])
@login_required
def sensore_destro():
    """
    Stato sensore destro (pin 16)
    ---
    responses:
      200:
        description: Stato sensore destro
    """
    val = GPIO.input(16)
    return jsonify({
        "pin": 16,
        "valore": val,
        "ostacolo": val == 0
    })
 
 
# ======================
# MOVIMENTO API
# ======================
@app.route('/api/movimento', methods=['POST'])
@login_required
def movimento():
    """
    Invia un comando di movimento al robot
    ---
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - command
          properties:
            command:
              type: string
              description: "Comando: W (avanti), S (indietro), A (sinistra), D (destra), STOP, triangolo, cerchio, quadrato"
    responses:
      200:
        description: Comando eseguito
      400:
        description: Comando non valido
      401:
        description: Non autenticato
    """
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"errore": "Comando mancante"}), 400
 
    command = data["command"]
 
    # Forme dal database
    if command in ["triangolo", "cerchio", "quadrato"]:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT cod FROM istruzioni WHERE nome = ?", (command,))
        result = cursor.fetchone()
        conn.close()
 
        if not result:
            return jsonify({"errore": f"Forma '{command}' non trovata nel database"}), 404
 
        command = result[0]
 
    # Esecuzione comandi
    command_map = {
        "W":    ("avanti",    alphabot.forward),
        "S":    ("indietro",  alphabot.backward),
        "A":    ("sinistra",  alphabot.left),
        "D":    ("destra",    alphabot.right),
        "STOP": ("stop",      alphabot.stop),
        1:      ("triangolo", alphabot.triangolo),
        2:      ("quadrato",  alphabot.quadrato),
        3:      ("cerchio",   alphabot.cerchio),
    }
 
    if command not in command_map:
        return jsonify({"errore": f"Comando '{command}' non riconosciuto"}), 400
 
    action_name, action_fn = command_map[command]
    action_fn()
 
    return jsonify({"status": "ok", "azione": action_name})
 
 
@app.route('/api/movimento/stop', methods=['POST'])
@login_required
def stop():
    """
    Ferma il robot immediatamente
    ---
    responses:
      200:
        description: Robot fermato
    """
    alphabot.stop()
    return jsonify({"status": "ok", "azione": "stop"})
 
 
# ======================
# FORME (lettura DB)
# ======================
@app.route('/api/forme', methods=['GET'])
@login_required
def lista_forme():
    """
    Elenco delle forme disponibili nel database
    ---
    responses:
      200:
        description: Lista delle forme
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, cod FROM istruzioni")
    forme = cursor.fetchall()
    conn.close()
 
    return jsonify([{"nome": f[0], "cod": f[1]} for f in forme])
 
 
@app.route('/api/forme/<nome>', methods=['GET'])
@login_required
def dettaglio_forma(nome):
    """
    Dettaglio di una forma specifica
    ---
    parameters:
      - name: nome
        in: path
        required: true
        type: string
    responses:
      200:
        description: Dettaglio forma
      404:
        description: Forma non trovata
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, cod FROM istruzioni WHERE nome = ?", (nome,))
    forma = cursor.fetchone()
    conn.close()
 
    if not forma:
        return jsonify({"errore": "Forma non trovata"}), 404
 
    return jsonify({"nome": forma[0], "cod": forma[1]})
 
 
# ======================
# OSTACOLI (logica interna)
# ======================
def gestisci_ostacolo():
    """Logica di evitamento ostacoli (da chiamare in un thread separato se necessario)."""
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
    print("Swagger UI: http://<ip-raspberry>:5000/apidocs/")
    app.run(host="0.0.0.0", port=5000, debug=True)