"""
Chapter 2: End-to-End Radiology Report Encryption (Sender Side)
Healthcare Use Case: Alice (radiologist) securely packages a CT scan report 
for Bob (cardiologist) using hybrid cryptography and digital signatures.

Learning Objectives:
- Understand hybrid cryptography (AES + RSA)
- Learn about authenticated encryption (AES-EAX)
- See how digital signatures provide authenticity and integrity
- Understand key wrapping for secure key distribution
"""


import json, base64
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Random import get_random_bytes

print("=== Chapter 2.4: Secure Radiology Report Packaging ===")
print("Healthcare Story: Alice encrypts a CT report for Bob")
print()

# STEP 1: Load Cryptographic Keys
print("STEP 1: Load Alice's and Bob's keys")
print("  - Alice's private key: For signing the report")
print("  - Bob's public key: For encrypting the AES key")

try:
    alice_priv = RSA.import_key(open("alice_private.pem","rb").read())
    bob_pub = RSA.import_key(open("bob_public.pem","rb").read())
    print("  ✓ Keys loaded successfully")
except FileNotFoundError:
    print("  ✗ Key files not found. Run key_setup.py first!")
    exit(1)
print()

# STEP 2: Read the Medical Document
print("STEP 2: Read the radiology report (PDF)")
try:
    data = open("dummy_radiology_report.pdf","rb").read()
    print(f"  ✓ Loaded report: {len(data)} bytes")
    print("  → This could be a real CT scan, MRI, or X-ray report")
except FileNotFoundError:
    print("  ✗ Radiology report not found!")
    print("  → Create dummy_radiology_report.pdf or use any PDF file")
    exit(1)
print()

# STEP 3: Symmetric Encryption (Fast for Large Files)
print("STEP 3: Encrypt report with AES-256 (symmetric encryption)")
print("  - AES is fast for large medical images")
print("  - EAX mode provides both confidentiality and integrity")
print("  - Random key ensures each encryption is unique")

k = get_random_bytes(32)  # Generate random 256-bit AES key
cipher = AES.new(k, AES.MODE_EAX)  # AEAD mode (authenticated encryption)
ciphertext, tag = cipher.encrypt_and_digest(data)

print(f"  ✓ AES key generated: {len(k)} bytes")
print(f"  ✓ Report encrypted: {len(ciphertext)} bytes")
print(f"  ✓ Authentication tag: {len(tag)} bytes")
print("  → Even Eve can't read the encrypted report without the key")
print()

# STEP 4: Key Wrapping (Solve Key Distribution Problem)
print("STEP 4: Wrap AES key for Bob (asymmetric encryption)")
print("  - Problem: How to securely send the AES key to Bob?")
print("  - Solution: Encrypt AES key with Bob's public key")
print("  - Only Bob can decrypt with his private key")

wrap = PKCS1_OAEP.new(bob_pub)
wrapped_key = wrap.encrypt(k)
print(f"  ✓ AES key wrapped for Bob: {len(wrapped_key)} bytes")
print("  → Only Bob can unwrap this with his private key")
print()

# STEP 5: Create Metadata Header
print("STEP 5: Create cryptographic metadata header")
print("  - Specifies algorithms used")
print("  - Contains nonce and authentication tag")
print("  - Identifies recipient and signer")

header = {
    "alg": {
        "sym": "AES-EAX-256",                    # Symmetric algorithm
        "wrap": "RSA-OAEP",                      # Key wrapping algorithm  
        "sig": "RSASSA-PKCS1-v1_5-SHA256"       # Digital signature algorithm
    },
    "nonce": base64.b64encode(cipher.nonce).decode(),           # AES nonce
    "tag": base64.b64encode(tag).decode(),                      # Authentication tag
    "recipient": {
        "bob_pub_fp": SHA256.new(bob_pub.export_key()).hexdigest()  # Bob's key fingerprint
    },
    "wrapped_key": base64.b64encode(wrapped_key).decode(),      # Encrypted AES key
    "signer": {
        "alice_pub": base64.b64encode(alice_priv.publickey().export_key()).decode()  # Alice's public key
    }
}

print("  ✓ Header created with cryptographic metadata")
print(f"  • Algorithms: {header['alg']}")
print(f"  • Recipient: Bob (fingerprint: {header['recipient']['bob_pub_fp'][:16]}...)")
print()

# STEP 6: Digital Signature (Authenticity + Integrity)
print("STEP 6: Sign header and ciphertext with Alice's private key")
print("  - Proves the report came from Alice (authenticity)")
print("  - Detects any tampering with header or content (integrity)")
print("  - Bob can verify using Alice's public key")

# Create hash of header + ciphertext
message_to_sign = json.dumps(header, sort_keys=True).encode() + ciphertext
h = SHA256.new(message_to_sign)
signature = pkcs1_15.new(alice_priv).sign(h)
header["signature"] = base64.b64encode(signature).decode()

print(f"  ✓ Digital signature created: {len(signature)} bytes")
print("  → Bob can verify this came from Alice and wasn't tampered with")
print()

# STEP 7: Write Secure Package
print("STEP 7: Write secure package files")
print("  - Separating header and payload for efficiency")
print("  - Header contains metadata and signature")
print("  - Payload contains encrypted report")

header_file = "header.json"
payload_file = "payload.bin"

open(header_file, "w").write(json.dumps(header, indent=2))
open(payload_file, "wb").write(ciphertext)

print(f"  ✓ Created {header_file} (metadata + signature)")
print(f"  ✓ Created {payload_file} (encrypted report)")
print()

print("=== Files Created ===")
print(f"• {header_file} - Cryptographic metadata and signature")
print(f"• {payload_file} - Encrypted radiology report")
print()
print("=== Security Properties Achieved ===")
print("✓ Confidentiality: Only Bob can decrypt (key wrapped with his public key)")
print("✓ Integrity: Authentication tag detects tampering")
print("✓ Authenticity: Digital signature proves Alice created this")
print("✓ Non-repudiation: Alice cannot deny signing this report")
print()
print("=== Next Steps ===")
print("1. Run mint_token.py to create authorization token")
print("2. Run verify_decrypt.py to decrypt and verify as Bob")
