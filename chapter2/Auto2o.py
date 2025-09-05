"""
Chapter 2: OAuth 2.0 Authorization Server Simulation
Healthcare Use Case: Alice (radiologist) wants to give a mobile app permission to access 
her imaging data without sharing her password. OAuth 2.0 provides secure delegation.

Learning Objectives:
- Understand OAuth 2.0 token-based authorization
- Learn about scopes and audience validation
- See how Resource Servers enforce permissions
"""

# STEP 1: OAuth 2.0 Authorization Server (Hospital Identity Provider)
# Think of this as the hospital's security office that issues visitor passes
import jwt, time

# Demo signing key - in production, hospitals use RSA/ECDSA keys
AS_SIGNING_KEY = "hospital-oauth-hs256-key"  # demo only; real systems use asymmetric keys

print("=== Chapter 2.3.2: OAuth 2.0 Delegation Demo ===")
print("Healthcare Story: Alice wants a radiology app to access her imaging data")
print()

# STEP 2: Create Access Token Claims
# These claims define what the token holder can do
claims = {
    "iss": "https://id.hospital.example",  # issuer (who created this token)
    "sub": "alice@hospital",  # subject (resource owner - Alice)
    "aud": "https://ehr-api.example",  # audience (which API can use this token)
    "scope": "patient/Imaging.read patient/Lab.read",  # SMART on FHIR-like scopes (permissions)
    "exp": int(time.time()) + 3600,  # expiration (1 hour from now)
}

print("STEP 2: Authorization Server creates access token for Alice")
print(f"  - Subject: {claims['sub']} (Alice the radiologist)")
print(f"  - Scopes: {claims['scope']} (what Alice is allowing)")
print(f"  - Expires in: {claims['exp'] - int(time.time())} seconds")
print()

# STEP 3: Mint the JWT Access Token
# This is like creating a visitor pass with specific permissions
access_token = jwt.encode(claims, AS_SIGNING_KEY, algorithm="HS256")
print("STEP 3: Minted JWT access token:")
print("ACCESS_TOKEN=", access_token[:80], "...")
print()

# STEP 4: Resource Server Validates Token
# The EHR API checks if the token is valid and has the right permissions
print("STEP 4: Resource Server (EHR API) validates the token")
try:
    decoded = jwt.decode(access_token, AS_SIGNING_KEY, algorithms=["HS256"], audience="https://ehr-api.example")
    scopes = set(decoded["scope"].split())

    print(f"  ✓ Token signature valid")
    print(f"  ✓ Audience matches: {decoded['aud']}")
    print(f"  ✓ Available scopes: {scopes}")

    # Check if the required scope is present
    if "patient/Imaging.read" in scopes:
        print("  ✓ Scope OK - allow read of imaging resources")
        print("  → Alice's app can now fetch her CT scans!")
    else:
        print("  ✗ Missing required scope")

except Exception as e:
    print(f"  ✗ Token validation failed: {e}")

print()

# STEP 5: Demonstrate Security - Wrong Key Attack
print("STEP 5: Security Demo - What happens if Eve tries to forge a token?")
WRONG_KEY = "wrong-key"
try:
    # Eve tries to decode with wrong key (simulating token forgery)
    jwt.decode(access_token, WRONG_KEY, algorithms=["HS256"], audience="https://ehr-api.example")
    print("  ✗ This should never print - security breach!")
except jwt.exceptions.InvalidSignatureError:
    print("  ✓ OAuth 2.0 security works: Invalid token signature detected")
    print("  → Eve cannot forge tokens without the hospital's signing key")

print()
print("=== Key Takeaways ===")
print("• OAuth 2.0 enables secure delegation without password sharing")
print("• Scopes limit what the token can access (principle of least privilege)")
print("• JWT signatures prevent token forgery")
print("• Tokens expire to limit damage if compromised")
