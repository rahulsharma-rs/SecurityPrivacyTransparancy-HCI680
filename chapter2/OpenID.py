# Goal: simulate an OIDC RP verifying an ID token (HS256 demo; prod uses RS256/ES256 + JWKS).
import jwt
IDP_KEY = "hospital-oidc-hs256-key"

id_token = jwt.encode({
    "iss": "https://id.hospital.example",
    "sub": "alice@hospital",
    "aud": "radiology-viewer-client",   # client_id of the OIDC RP
    "nonce": "xyz123",                  # binds auth request to response
    "email": "alice@hospital"
}, IDP_KEY, algorithm="HS256")

# RP checks issuer, audience, and (normally) expiration & nonce
claims = jwt.decode(id_token, IDP_KEY, algorithms=["HS256"], audience="radiology-viewer-client")
assert claims["iss"] == "https://id.hospital.example"
assert claims["nonce"] == "xyz123"
print("OIDC ID token validated for:", claims["sub"]) 