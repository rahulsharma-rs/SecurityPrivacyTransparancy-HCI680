"""
Chapter 2: OpenID Connect (OIDC) Identity Verification
Healthcare Use Case: Bob wants to verify that the user of a radiology app 
is truly Alice (authentication), not just authorize access (authorization).

Learning Objectives:
- Understand the difference between authentication and authorization
- Learn how ID tokens prove user identity
- See how OpenID Connect builds on OAuth 2.0
"""

import jwt

print("=== Chapter 2.3.3: OpenID Connect Identity Verification ===")
print("Healthcare Story: Verifying Alice's identity for radiology app access")
print()

# Demo key - in production, use RSA/ECDSA with JWKS endpoint
IDP_KEY = "hospital-oidc-hs256-key"

print("STEP 1: Understanding the Problem")
print("  - OAuth 2.0 tells us WHAT Alice can access (authorization)")
print("  - OpenID Connect tells us WHO Alice is (authentication)")
print("  - Bob's radiology app needs to know it's really Alice, not Eve")
print()

# STEP 2: Create ID Token
print("STEP 2: Hospital Identity Provider creates ID token for Alice")
print("  - ID token proves Alice successfully authenticated")
print("  - Contains Alice's identity information")
print("  - Signed by trusted hospital identity provider")

id_token_claims = {
    "iss": "https://id.hospital.example",  # Issuer: Hospital identity provider
    "sub": "alice@hospital",  # Subject: Alice's unique identifier
    "aud": "radiology-viewer-client",  # Audience: The radiology app's client ID
    "nonce": "xyz123",  # Nonce: Prevents replay attacks
    "email": "alice@hospital",  # Additional identity info
    "name": "Dr. Alice Smith",  # Human-readable name
    "role": "Radiologist"  # Hospital role
}

print(f"  • Subject: {id_token_claims['sub']} (Alice's hospital ID)")
print(f"  • Audience: {id_token_claims['aud']} (radiology app)")
print(f"  • Email: {id_token_claims['email']}")
print(f"  • Role: {id_token_claims['role']}")
print()

# Create the ID token
id_token = jwt.encode(id_token_claims, IDP_KEY, algorithm="HS256")
print("  ✓ ID token created and signed by hospital")
print(f"  Token: {id_token[:60]}...")
print()

# STEP 3: Radiology App Validates ID Token
print("STEP 3: Radiology app (Relying Party) validates ID token")
print("  - App checks token signature and claims")
print("  - Ensures token is from trusted hospital identity provider")
print("  - Verifies nonce to prevent replay attacks")

try:
    # Validate the ID token
    claims = jwt.decode(
        id_token,
        IDP_KEY,
        algorithms=["HS256"],
        audience="radiology-viewer-client"
    )

    print("  ✓ Token signature valid (from trusted hospital)")
    print("  ✓ Audience matches this radiology app")

    # Verify issuer
    if claims["iss"] == "https://id.hospital.example":
        print("  ✓ Issuer verified (hospital identity provider)")
    else:
        print("  ✗ Untrusted issuer")

    # Verify nonce (prevents replay attacks)
    if claims["nonce"] == "xyz123":
        print("  ✓ Nonce verified (prevents replay)")
    else:
        print("  ✗ Nonce mismatch - possible replay attack")

    print()
    print("STEP 4: Identity Confirmed!")
    print(f"  ✓ User authenticated as: {claims['sub']}")
    print(f"  ✓ Display name: {claims.get('name', 'Unknown')}")
    print(f"  ✓ Hospital role: {claims.get('role', 'Unknown')}")
    print("  → Radiology app can now show Alice's personalized interface")

except jwt.ExpiredSignatureError:
    print("  ✗ ID token expired")
except jwt.InvalidAudienceError:
    print("  ✗ ID token not intended for this app")
except jwt.InvalidSignatureError:
    print("  ✗ ID token signature invalid - possible forgery")
except Exception as e:
    print(f"  ✗ ID token validation failed: {e}")

print()
print("=== Authentication vs Authorization ===")
print("OAuth 2.0 Access Token:")
print("  • Purpose: Authorization (what can Alice do?)")
print("  • Contains: Scopes, permissions, expiration")
print("  • Used by: APIs to check permissions")
print()
print("OpenID Connect ID Token:")
print("  • Purpose: Authentication (who is Alice?)")
print("  • Contains: Identity claims, user info")
print("  • Used by: Apps to personalize user experience")
print()

print("=== Key Takeaways ===")
print("• OpenID Connect proves user identity, not just permissions")
print("• ID tokens contain identity claims (who), access tokens contain scopes (what)")
print("• Nonce prevents token replay attacks")
print("• Critical for healthcare: ensures the right person accesses the right data")
print("• Real hospitals use this for EHR login, patient portals, telemedicine")
