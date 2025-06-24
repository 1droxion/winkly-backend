@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        print("Webhook Error:", e)
        return "", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get("customer_email")
        ip = request.remote_addr

        # Save VIP status
        with open("vip_users.json", "r+") as f:
            try:
                data = json.load(f)
            except:
                data = []

            if ip not in data:
                data.append(ip)
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        print("✅ VIP Unlocked:", ip)

    return "", 200
