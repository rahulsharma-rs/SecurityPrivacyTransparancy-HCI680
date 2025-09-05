"""
Chapter 2: JWT Access Token Minting for Healthcare Authorization
Healthcare Use Case: Hospital's Authorization Server creates a token that allows
Bob (cardiologist) to access Alice's imaging data through the EHR API.

Learning Objectives:
- Understand JWT (JSON Web Token) structure and claims
- Learn about token-based authorization in healthcare
- See how scopes control access to different types of medical data
"""


import time, jwt

print("=== Chapter 2.3.2: JWT Access Token Minting Demo ===")
print("Healthcare Story: Creating an access token for Bob to view imaging data")
print()

# Demo signing key - in production, use RSA/ECDSA keys stored in HSM
SIGNING_KEY = "hospital-oauth-lab-key"  # demo only; use RSA/EC in production

print("STEP 1: Define Token Claims (What the token represents)")
print("  - Claims are statements about the token holder and permissions")
print("  - Similar to information on a hospital visitor badge")

# STEP 2: Create JWT Claims
claims = {
    "iss": "https://id.hospital.example",    # Issuer: Who created this token
    "sub": "bob@hospital",                   # Subject: Who this token is for (Bob)
    "aud": "https://decrypt.ehr.example",    # Audience: Which service accepts this token
    "scope": "patient/Imaging.read",         # Scope: What permissions are granted
    "exp": int(time.time()) + 900            # Expiration: Token valid for 15 minutes
}

print(f"  • Issuer (iss): {claims['iss']}")
print(f"  • Subject (sub): {claims['sub']} (Bob the cardiologist)")
print(f"  • Audience (aud): {claims['aud']} (EHR decryption service)")
print(f"  • Scope: {claims['scope']} (can read imaging data)")
print(f"  • Expires in: {claims['exp'] - int(time.time())} seconds")
print()

# STEP 3: Create and Sign JWT Token
print("STEP 2: Create and sign JWT access token")
print("  - JWT has 3 parts: header.payload.signature")
print("  - Signature prevents tampering (like a tamper-evident seal)")

access_token = jwt.encode(claims, SIGNING_KEY, algorithm="HS256")
print("  ✓ JWT token created and signed")
print()

# STEP 4: Save Token to File
print("STEP 3: Save token for use by other scripts")
token_file = "token.jwt"
open(token_file, "w").write(access_token)
print(f"  ✓ Saved to: {token_file}")
print(f"  → This token allows Bob to decrypt Alice's radiology reports")
print()

# STEP 5: Display Token Structure
print("STEP 4: Token structure (first 80 characters shown)")
print(f"  Token: {access_token[:80]}...")
print("  Structure: [header].[payload].[signature]")
print()

# STEP 6: Demonstrate Token Validation
print("STEP 5: Validate the token we just created")
try:
    # Decode and validate the token
    decoded_claims = jwt.decode(
        access_token,
        SIGNING_KEY,
        algorithms=["HS256"],
        audience="https://decrypt.ehr.example"
    )
    print("  ✓ Token signature valid")
    print("  ✓ Audience matches expected service")
    print("  ✓ Token not expired")
    print(f"  ✓ Scope confirmed: {decoded_claims['scope']}")
except jwt.ExpiredSignatureError:
    print("  ✗ Token has expired - run this script again")
except jwt.InvalidAudienceError:
    print("  ✗ Token audience mismatch")
except jwt.InvalidSignatureError:
    print("  ✗ Token signature invalid - possible tampering")
except Exception as e:
    print(f"  ✗ Token validation error: {e}")

print()
print("=== Files Created ===")
print(f"• {token_file} - JWT access token for Bob")
print()
print("=== Key Takeaways ===")
print("• JWT tokens carry authorization information securely")
print("• Scopes define fine-grained permissions (imaging vs. lab data)")
print("• Tokens expire to limit damage if compromised")
print("• Signatures prevent forgery and tampering")
print("• Used in verify_decrypt.py to authorize decryption")
