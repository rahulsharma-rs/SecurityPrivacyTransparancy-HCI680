# Goal: simulate an SSO IdP issuing a signed session cookie after Alice authenticates.

import hmac, hashlib, base64, json, time

SECRET = b"hospital-sso-signing-key"

def sign_session(payload: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(SECRET, body.encode(), hashlib.sha256).digest()
    mac = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{body}.{mac}"

# IdP issues session cookie after Alice passes login
cookie = sign_session({"sub": "alice@hospital", "roles": ["Radiologist"], "iat": int(time.time())})
print("SSO_COOKIE=", cookie[:80], "...")

# Verifier (service) checks the MAC before trusting the cookie
body, mac = cookie.split(".")
#SECRET = b"hospital-sso-signing-key1"
expected = base64.urlsafe_b64encode(hmac.new(SECRET, body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
assert mac == expected, "invalid SSO cookie"

# Tamper with the MAC to simulate a wrong cookie
bad_cookie = cookie[:-1] + ("A" if cookie[-1] != "A" else "B")
body, mac = bad_cookie.split(".")
expected = base64.urlsafe_b64encode(hmac.new(SECRET, body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
assert mac == expected, "invalid SSO cookie"