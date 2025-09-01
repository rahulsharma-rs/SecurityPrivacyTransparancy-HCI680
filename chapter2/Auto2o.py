# Goal: simulate an OAuth Authorization Server (AS) minting a JWT access token with scopes
# and a Resource Server (RS) enforcing those scopes.
import jwt, time
AS_SIGNING_KEY = "hospital-oauth-hs256-key"  # demo only; real systems use asymmetric keys

claims = {
    "iss": "https://id.hospital.example",  # issuer
    "sub": "alice@hospital",               # resource owner
    "aud": "https://ehr-api.example",      # audience (RS)
    "scope": "patient/Imaging.read patient/Lab.read",  # SMART on FHIR-like scopes
    "exp": int(time.time()) + 3600,
}
access_token = jwt.encode(claims, AS_SIGNING_KEY, algorithm="HS256")
print("ACCESS_TOKEN=", access_token[:80], "...")

# RS receives the token and enforces scope
decoded = jwt.decode(access_token, AS_SIGNING_KEY, algorithms=["HS256"], audience="https://ehr-api.example")
scopes = set(decoded["scope"].split())
assert "patient/Imaging.read" in scopes, "scope missing: Imaging.read"
print("Scope OK - allow read of imaging resources")



# Use a wrong key to decode (simulate failure)
WRONG_KEY = "wrong-key"
try:
    jwt.decode(access_token, WRONG_KEY, algorithms=["HS256"], audience="https://ehr-api.example")
except jwt.exceptions.InvalidSignatureError:
    print("Auth2.0 failure: Invalid token signature")