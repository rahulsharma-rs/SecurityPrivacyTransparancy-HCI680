"""
Chapter 2.2.1: Symmetric Encryption - Alice locks the CT scan
Healthcare Use Case: Alice (radiologist) wants to send a CT scan to Bob (cardiologist)
Problem: How to share the secret key securely without Eve (attacker) stealing it?
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# STEP 1: Alice generates a secret key (like a physical key to a locked box)
# This key will be used for both locking (encryption) and unlocking (decryption)
key = get_random_bytes(16)  # 128-bit AES key - strong enough for medical data
print("Secret Key (Alice keeps this safe):", key.hex()[:20], "...")

# STEP 2: Alice creates an encryption "machine" using AES-EAX mode
# EAX mode provides both confidentiality AND integrity (tamper detection)
cipher = AES.new(key, AES.MODE_EAX)

# STEP 3: Alice's sensitive medical data (CT scan results)
scan = b"CT Scan: Patient ID 12345, results normal"
print("Original CT Scan:", scan.decode())

# STEP 4: Alice encrypts the scan - now it looks like random data to Eve
# The 'tag' acts like a tamper-evident seal - if Eve changes anything, Bob will know
ciphertext, tag = cipher.encrypt_and_digest(scan)

print("Encrypted Scan (Eve can't read this):", ciphertext.hex()[:40], "...")
print("Integrity Tag (detects tampering):", tag.hex())

# THE PROBLEM: How does Alice safely give Bob the secret key?
# This is called the "Key Distribution Problem" - solved by asymmetric encryption!
print("\n⚠️  KEY DISTRIBUTION PROBLEM: Alice needs to safely share the key with Bob")
