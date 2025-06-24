from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid, json, time, os
from datetime import datetime

app = Flask(__name__)
CORS(app)

LOG_FILE = "user_logs.json"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

def log_user(ip, action):
    with open(LOG_FILE, "r") as f:
        logs = json.load(f)
    logs.append({
        "ip": ip,
        "action": action,
        "time": datetime.utcnow().isoformat()
    })
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

@app.route("/create_user", methods=["POST"])
def create_user():
    user_id = str(uuid.uuid4())
    ip = request.remote_addr
    log_user(ip, f"User created: {user_id}")
    return jsonify({"user_id": user_id})

@app.route("/match", methods=["GET"])
def match_user():
    ip = request.remote_addr
    log_user(ip, "Requested match")
    return jsonify({"matched": True, "room": str(uuid.uuid4())})

@app.route("/coins", methods=["POST"])
def get_coins():
    data = request.get_json()
    user_id = data.get("user_id")
    ip = request.remote_addr
    log_user(ip, f"Coins checked: {user_id}")
    return jsonify({"coins": 5})

@app.route("/")
def home():
    return "Winkly Backend Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
