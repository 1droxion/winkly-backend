from flask import Flask, request, jsonify
import os, json
import stripe
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# Load or init VIP and coin data
VIP_FILE = "vip_users.json"
COIN_FILE = "user_coins.json"
if not os.path.exists(VIP_FILE): json.dump([], open(VIP_FILE, "w"))
if not os.path.exists(COIN_FILE): json.dump({}, open(COIN_FILE, "w"))

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        print("❌ Stripe error:", e)
        return "Invalid", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get("customer_email")
        amount = int(session.get("amount_total", 0)) / 100
        ip = request.remote_addr

        # Check what they bought based on amount
        coins = 0
        is_vip = False

        if amount == 1.99:
            coins = 5
        elif amount == 5.00:
            coins = 20
        elif amount == 9.99:
            coins = 50
        elif amount == 19.99:
            is_vip = True

        if is_vip:
            with open(VIP_FILE, "r+") as f:
                data = json.load(f)
                if ip not in data:
                    data.append(ip)
                    f.seek(0)
                    json.dump(data, f)
                    f.truncate()
            print(f"👑 VIP granted to {ip}")
        elif coins > 0:
            with open(COIN_FILE, "r+") as f:
                data = json.load(f)
                data[ip] = data.get(ip, 0) + coins
                f.seek(0)
                json.dump(data, f)
                f.truncate()
            print(f"💰 {coins} coins added to {ip}")

    return "Success", 200

@app.route("/check-vip", methods=["GET"])
def check_vip():
    ip = request.remote_addr
    with open(VIP_FILE) as f:
        data = json.load(f)
    return jsonify({"isVIP": ip in data})

@app.route("/get-coins", methods=["GET"])
def get_coins():
    ip = request.remote_addr
    with open(COIN_FILE) as f:
        data = json.load(f)
    return jsonify({"coins": data.get(ip, 0)})
