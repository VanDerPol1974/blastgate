from flask import Flask, jsonify, request
from serial_bridge import SerialBridge

app = Flask(__name__)

# ----------------------------
# Serial Bridge starten
# ----------------------------
bridge = SerialBridge()

# ----------------------------
# STATUS API
# ----------------------------
@app.route("/api/status")
def api_status():
    s = bridge.state
    return jsonify({
        "online": s.online,
        "state": s.state,
        "motor1": s.motor1,
        "motor2": s.motor2,
        "gates": s.gates,
        "error": s.error
    })

# ----------------------------
# GATE STEUERUNG
# ----------------------------
@app.route("/api/gate", methods=["POST"])
def api_gate():
    data = request.json
    gate = int(data["gate"])
    action = data["action"]  # OPEN / CLOSE / TOGGLE

    bridge.send(f"CMD:GATE:{gate}:{action}")
    return jsonify({"ok": True})

# ----------------------------
# SYSTEMZUSTAND
# ----------------------------
@app.route("/api/state", methods=["POST"])
def api_state():
    data = request.json
    state = data["state"]  # RUN / SERVICE / ERROR

    bridge.send(f"CMD:STATE:{state}")
    return jsonify({"ok": True})

# ----------------------------
# MOTOR NOT-AUS
# ----------------------------
@app.route("/api/motors/off", methods=["POST"])
def api_motors_off():
    bridge.send("CMD:MOTORS:OFF")
    return jsonify({"ok": True})

# ----------------------------
# FEHLER QUITTIEREN
# ----------------------------
@app.route("/api/error/clear", methods=["POST"])
def api_error_clear():
    bridge.send("CMD:STATE:RUN")
    return jsonify({"ok": True})

# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
