"""
Chapter 2.2.5: Digital Signatures - Alice proves authorship
Healthcare Use Case: Bob needs to verify the prescription really came from Alice
Security Properties: Authenticity (proves who sent it) + Integrity (detects changes)
"""

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# STEP 1: Alice generates her RSA key pair (like having a unique signature stamp)
# Private key = Alice's secret signature stamp (NEVER share this!)
# Public key = Everyone can use this to verify Alice's signatures
key = RSA.generate(2048)  # 2048-bit RSA key - secure for medical documents
private_key = key
public_key = key.publickey()

print("Alice's Public Key (everyone can see this):", public_key.export_key().decode()[:100], "...")

# STEP 2: Alice's prescription that needs to be signed
message = b"Prescription: Drug A, dosage 20mg"
print("Original Prescription:", message.decode())

# STEP 3: Alice creates a "fingerprint" of the prescription using SHA-256
# This ensures even tiny changes will be detected
h = SHA256.new(message)
print("Prescription Fingerprint:", h.hexdigest()[:20], "...")

# STEP 4: Alice signs the fingerprint with her private key
# This is like Alice putting her unique signature on the prescription
signature = pkcs1_15.new(private_key).sign(h)
print("Alice's Digital Signature:", signature.hex()[:50], "...")

# STEP 5: Bob can verify this signature using Alice's public key
# If verification passes, Bob knows: 1) Alice signed it, 2) No one tampered with it
try:
    pkcs1_15.new(public_key).verify(h, signature)
    print("✅ Signature VALID - Prescription is authentic and untampered!")
except:
    print("❌ Signature INVALID - Either forged or tampered!")

# DEMONSTRATION: What happens if Eve tries to tamper?
print("\n🔍 TAMPERING TEST:")
tampered_message = b"Prescription: Drug A, dosage 200mg"  # Eve changed dosage!
tampered_hash = SHA256.new(tampered_message)
try:
    pkcs1_15.new(public_key).verify(tampered_hash, signature)
    print("❌ This shouldn't happen - tampering not detected!")
except:
    print("✅ Tampering DETECTED - Bob knows someone changed the prescription!")
