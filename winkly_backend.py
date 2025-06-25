# === winkly_backend.py ===
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import json
import os
import stripe
from datetime import datetime

app = Flask(__name__)
CORS(app)

USER_FILE = "users.json"
STRIPE_SECRET = os.getenv("STRIPE_SECRET", "sk_test_...")
stripe.api_key = STRIPE_SECRET

# Load users
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Save users
def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if email in users:
        return jsonify({"error": "Email already registered"})
    user_id = str(uuid.uuid4())
    users[email] = {
        "id": user_id,
        "email": email,
        "password": password,
        "coins": 5,
        "vip": False,
        "gifts_received": 0,
        "is_girl": data.get("is_girl", False),
        "created_at": datetime.utcnow().isoformat()
    }
    save_users()
    return jsonify({"user": users[email]})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = users.get(email)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid email or password"})
    return jsonify({"user": user})

@app.route("/get-user", methods=["POST"])
def get_user():
    email = request.json.get("email")
    user = users.get(email)
    if user:
        return jsonify({"user": user})
    return jsonify({"error": "User not found"})

@app.route("/update-coins", methods=["POST"])
def update_coins():
    data = request.json
    email = data.get("email")
    amount = data.get("amount", 0)
    if email in users:
        users[email]["coins"] += amount
        save_users()
        return jsonify({"coins": users[email]["coins"]})
    return jsonify({"error": "User not found"})

@app.route("/update-vip", methods=["POST"])
def update_vip():
    email = request.json.get("email")
    if email in users:
        users[email]["vip"] = True
        save_users()
        return jsonify({"vip": True})
    return jsonify({"error": "User not found"})

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email")
        product = session.get("display_items", [{}])[0].get("custom", {}).get("name", "")

        if email in users:
            if "5 Coins" in product:
                users[email]["coins"] += 5
            elif "20 Coins" in product:
                users[email]["coins"] += 20
            elif "50 Coins" in product:
                users[email]["coins"] += 50
            elif "VIP" in product:
                users[email]["vip"] = True
            save_users()
    return jsonify({"status": "success"})

@app.route("/admin-stats")
def admin_stats():
    total_users = len(users)
    total_vip = sum(1 for u in users.values() if u.get("vip"))
    total_coins = sum(u.get("coins", 0) for u in users.values())
    total_gifts = sum(u.get("gifts_received", 0) for u in users.values())
    total_girls = sum(1 for u in users.values() if u.get("is_girl"))
    return jsonify({
        "users": total_users,
        "vip": total_vip,
        "coins": total_coins,
        "gifts": total_gifts,
        "girls": total_girls
    })

@app.route("/send-gift", methods=["POST"])
def send_gift():
    data = request.json
    sender = data.get("from")
    receiver = data.get("to")
    gift = data.get("gift")

    gift_cost = {"rose": 1, "heart": 3, "diamond": 5}
    cost = gift_cost.get(gift, 1)

    if sender not in users or receiver not in users:
        return jsonify({"error": "Invalid sender or receiver"})
    if users[sender]["coins"] < cost:
        return jsonify({"error": "Not enough coins"})

    users[sender]["coins"] -= cost
    users[receiver]["gifts_received"] += 1
    save_users()

    return jsonify({
        "message": f"{gift} sent from {sender} to {receiver}",
        "coins_left": users[sender]["coins"],
        "gifts": users[receiver]["gifts_received"]
    })

if __name__ == "__main__":
    app.run(debug=True)
