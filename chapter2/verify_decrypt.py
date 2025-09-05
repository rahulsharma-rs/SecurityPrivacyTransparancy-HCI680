"""
Chapter 2: End-to-End Radiology Report Decryption (Receiver Side)
Healthcare Use Case: Bob (cardiologist) receives Alice's encrypted CT report,
verifies authorization, authenticity, and integrity before decrypting.

Learning Objectives:
- Understand token-based authorization in healthcare
- Learn signature verification for authenticity
- See key unwrapping and authenticated decryption
- Understand the complete secure communication workflow
"""

import json, base64, jwt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

print("=== Chapter 2.4: Secure Radiology Report Decryption ===")
print("Healthcare Story: Bob verifies and decrypts Alice's CT report")
print()

# Configuration for OAuth-style authorization
AS_KEY = "hospital-oauth-lab-key"  # Authorization Server's signing key
REQUIRED_SCOPE = "patient/Imaging.read"  # Required permission scope

print("STEP 1: Load encrypted package and access token")
print("  - header.json: Contains cryptographic metadata")
print("  - payload.bin: Contains encrypted report")
print("  - token.jwt: Authorization token from hospital")

try:
    header = json.load(open("header.json"))
    ciphertext = open("payload.bin", "rb").read()
    print("  ✓ Encrypted package loaded")
    print(f"  • Header algorithms: {header['alg']}")
    print(f"  • Payload size: {len(ciphertext)} bytes")
except FileNotFoundError as e:
    print(f"  ✗ Missing file: {e}")
    print("  → Run pakage_encrypt.py first to create the encrypted package")
    exit(1)
print()

# STEP 2: Validate Authorization Token
print("STEP 2: Validate OAuth access token")
print("  - Ensures Bob has permission to decrypt imaging data")
print("  - Checks token signature, expiration, and required scopes")
print("  - Similar to checking Bob's hospital badge permissions")

try:
    access_token = open("token.jwt").read()
    claims = jwt.decode(
        access_token,
        AS_KEY,
        algorithms=["HS256"],
        audience="https://decrypt.ehr.example"
    )

    # Check if token has required scope
    token_scopes = claims.get("scope", "").split()
    if REQUIRED_SCOPE not in token_scopes:
        print(f"  ✗ Missing required scope: {REQUIRED_SCOPE}")
        print(f"  → Token scopes: {token_scopes}")
        exit(1)

    print("  ✓ Access token valid")
    print(f"  • Subject: {claims['sub']} (Bob)")
    print(f"  • Scopes: {token_scopes}")
    print("  → Bob is authorized to decrypt imaging data")

except jwt.ExpiredSignatureError:
    print("  ✗ Access token expired")
    print("  → Run mint_token.py to create a new token")
    exit(1)
except FileNotFoundError:
    print("  ✗ Access token not found")
    print("  → Run mint_token.py to create authorization token")
    exit(1)
except Exception as e:
    print(f"  ✗ Token validation failed: {e}")
    exit(1)
print()

# STEP 3: Verify Digital Signature (Authenticity + Integrity)
print("STEP 3: Verify Alice's digital signature")
print("  - Proves the report really came from Alice")
print("  - Detects any tampering with header or encrypted content")
print("  - Uses Alice's public key from the header")

try:
    # Extract Alice's public key from header
    alice_pub_bytes = base64.b64decode(header["signer"]["alice_pub"])
    alice_pub = RSA.import_key(alice_pub_bytes)

    # Recreate the message that was signed
    header_without_sig = {k: header[k] for k in header if k != "signature"}
    signed_message = json.dumps(header_without_sig, sort_keys=True).encode() + ciphertext
    msg_hash = SHA256.new(signed_message)

    # Verify signature
    signature_bytes = base64.b64decode(header["signature"])
    pkcs1_15.new(alice_pub).verify(msg_hash, signature_bytes)

    print("  ✓ Digital signature verified")
    print("  • Authenticity: Report confirmed from Alice")
    print("  • Integrity: No tampering detected")
    print("  → Safe to proceed with decryption")

except Exception as e:
    print(f"  ✗ Signature verification failed: {e}")
    print("  → Report may be forged or tampered with!")
    exit(1)
print()

# STEP 4: Unwrap AES Key (Key Distribution Solution)
print("STEP 4: Unwrap AES decryption key using Bob's private key")
print("  - Alice wrapped the AES key with Bob's public key")
print("  - Only Bob can unwrap it with his private key")
print("  - Solves the secure key distribution problem")

try:
    bob_priv = RSA.import_key(open("bob_private.pem", "rb").read())
    unwrapper = PKCS1_OAEP.new(bob_priv)

    wrapped_key_bytes = base64.b64decode(header["wrapped_key"])
    aes_key = unwrapper.decrypt(wrapped_key_bytes)

    print(f"  ✓ AES key unwrapped: {len(aes_key)} bytes")
    print("  → Bob now has the symmetric decryption key")

except FileNotFoundError:
    print("  ✗ Bob's private key not found")
    print("  → Run key_setup.py to generate keys")
    exit(1)
except Exception as e:
    print(f"  ✗ Key unwrapping failed: {e}")
    print("  → Report may not be intended for Bob")
    exit(1)
print()

# STEP 5: Decrypt Report (Authenticated Decryption)
print("STEP 5: Decrypt radiology report with AES-EAX")
print("  - Uses unwrapped AES key and nonce from header")
print("  - Verifies authentication tag to detect tampering")
print("  - Recovers original radiology report")

try:
    # Reconstruct AES cipher with original nonce
    nonce = base64.b64decode(header["nonce"])
    aes_cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)

    # Decrypt and verify authentication tag
    auth_tag = base64.b64decode(header["tag"])
    plaintext = aes_cipher.decrypt_and_verify(ciphertext, auth_tag)

    # Save decrypted report
    output_file = "radiology_report_decrypted.pdf"
    open(output_file, "wb").write(plaintext)

    print(f"  ✓ Report decrypted: {len(plaintext)} bytes")
    print(f"  ✓ Authentication tag verified")
    print(f"  ✓ Saved as: {output_file}")
    print("  → Bob can now view Alice's CT scan report")

except Exception as e:
    print(f"  ✗ Decryption failed: {e}")
    print("  → Ciphertext may be corrupted or tampered with")
    exit(1)

print()
print("=== Files Created ===")
print(f"• {output_file} - Decrypted radiology report")
print()
print("=== Security Verification Complete ===")
print("✓ Authorization: Bob's token grants imaging access")
print("✓ Authenticity: Signature confirms report from Alice")
print("✓ Integrity: No tampering detected in header or content")
print("✓ Confidentiality: Report successfully decrypted for Bob")
print()
print("=== Healthcare Security Workflow Complete ===")
print("1. Alice encrypted report with hybrid cryptography")
print("2. Alice signed report for authenticity and integrity")
print("3. Hospital issued authorization token to Bob")
print("4. Bob verified all security properties before decryption")
print("5. Secure medical communication achieved!")
