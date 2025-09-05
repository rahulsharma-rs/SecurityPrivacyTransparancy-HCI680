"""
Chapter 2.3.1: Single Sign-On (SSO) - Alice's hospital badge
Healthcare Use Case: Alice logs in once and accesses all hospital systems
Security: Signed cookies prevent Eve from forging access tokens
"""

import hmac, hashlib, base64, json, time

# STEP 1: Hospital's secret signing key (like the master key for making ID badges)
# In real hospitals, this would be stored in a Hardware Security Module (HSM)
SECRET = b"hospital-sso-signing-key"


def sign_session(payload: dict) -> str:
    """
    Creates a signed session cookie - like a tamper-proof hospital ID badge
    The signature ensures Eve can't forge or modify Alice's credentials
    """
    # Encode the user information (like printing info on an ID badge)
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    # Create a cryptographic signature (like a hologram on the badge)
    sig = hmac.new(SECRET, body.encode(), hashlib.sha256).digest()
    mac = base64.urlsafe_b64encode(sig).decode().rstrip("=")

    # Combine info + signature (badge with hologram)
    return f"{body}.{mac}"


# STEP 2: Alice successfully logs in with username/password
# The Identity Provider (IdP) issues her a signed session cookie
print("🏥 Alice logs into the hospital system...")
alice_session = {
    "sub": "alice@hospital",  # Alice's identity
    "roles": ["Radiologist"],  # What she's allowed to do
    "iat": int(time.time())  # When the session was created
}

cookie = sign_session(alice_session)
print("SSO Cookie issued to Alice:", cookie[:80], "...")

# STEP 3: Alice visits different hospital systems (EHR, lab system, etc.)
# Each system verifies her cookie without asking for password again
print("\n🔍 Hospital system verifies Alice's cookie...")
body, mac = cookie.split(".")

# Recalculate the signature to verify authenticity
expected = base64.urlsafe_b64encode(hmac.new(SECRET, body.encode(), hashlib.sha256).digest()).decode().rstrip("=")

if mac == expected:
    # Decode Alice's information from the cookie
    alice_info = json.loads(base64.urlsafe_b64decode(body + "=="))
    print("✅ Valid SSO cookie! Welcome,", alice_info["sub"])
    print("   Roles:", alice_info["roles"])
else:
    print("❌ Invalid SSO cookie - access denied!")

# STEP 4: Security demonstration - What if Eve tries to tamper?
print("\n🚨 SECURITY TEST: Eve tries to tamper with Alice's cookie...")
bad_cookie = cookie[:-1] + ("A" if cookie[-1] != "A" else "B")  # Change last character
body, mac = bad_cookie.split(".")
expected = base64.urlsafe_b64encode(hmac.new(SECRET, body.encode(), hashlib.sha256).digest()).decode().rstrip("=")

try:
    assert mac == expected, "invalid SSO cookie"
    print("❌ This shouldn't happen - tampering not detected!")
except AssertionError:
    print("✅ Tampering DETECTED! Eve's forged cookie rejected.")

print("\n📚 SSO BENEFITS:")
print("✅ Convenience: Alice logs in once, accesses everything")
print("✅ Security: Cryptographic signatures prevent forgery")
print("⚠️  Risk: If Eve steals Alice's cookie, she gets broad access")
