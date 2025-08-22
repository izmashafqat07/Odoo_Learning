from flask import Flask, request, jsonify
from datetime import datetime
import time, random, string

app = Flask(__name__)

# Simple in-memory token store
TOKENS = {}

def make_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

@app.route("/auth/token", methods=["POST"])
def auth_token():
    data = request.get_json(force=True, silent=True) or {}
    if not data.get("client_id") or not data.get("client_secret"):
        return jsonify({"error": "invalid_client"}), 400
    token = make_token()
    TOKENS[token] = time.time() + 1800
    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": 1800})

def verify_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.split(" ",1)[1]
    exp = TOKENS.get(token)
    return bool(exp and exp > time.time())

@app.route("/api/invoices", methods=["POST"])
def submit_invoice():
    if not verify_auth():
        return jsonify({"success": False, "message": "unauthorized"}), 401
    data = request.get_json(force=True, silent=True) or {}
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    inv_no = f"FBR-{now}-{random.randint(1000,9999)}"
    irn = ''.join(random.choices(string.hexdigits.lower(), k=32))
    # Make a very simple QR payload
    qr = f"FBR|{inv_no}|{data.get('InvoiceTotal')}|{data.get('InvoiceTaxTotal')}|{data.get('InvoiceDate')}"
    return jsonify({
        "success": True,
        "fbr_invoice_number": inv_no,
        "irn": irn,
        "qr_string": qr,
        "submitted_at": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/api/invoices/cancel", methods=["POST"])
def cancel_invoice():
    if not verify_auth():
        return jsonify({"success": False, "message": "unauthorized"}), 401
    return jsonify({"success": True, "message": "cancelled"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)