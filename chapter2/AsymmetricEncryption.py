from Crypto.PublicKey import RSA

# Bob generates his RSA key pair
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

print("Public Key:", public_key.decode()[:100], "...")

"""
Chapter 2: Asymmetric Encryption (Public Key Cryptography)
Healthcare Cybersecurity - The Mailbox Analogy

Learning Objective: Understand how asymmetric encryption solves the key distribution problem
in healthcare by using public/private key pairs for secure communication between clinicians.

Healthcare Story: Bob (cardiologist) creates a digital "mailbox" so Alice (radiologist) 
can send him encrypted patient reports without sharing secret keys beforehand.
"""

from Crypto.PublicKey import RSA

print("=== Chapter 2.2.2: Asymmetric Encryption Demo ===")
print("Healthcare Use Case: Secure key exchange between hospital departments")
print()

# STEP 1: Key Pair Generation (Bob creates his digital mailbox)
print("STEP 1: Bob (cardiologist) generates his RSA key pair")
print("- This is like Bob creating a special mailbox with two keys:")
print("  * Public key = mailbox slot (anyone can use to send messages)")
print("  * Private key = mailbox key (only Bob can open and read messages)")
print()

# Bob generates his RSA key pair
key = RSA.generate(2048)  # 2048-bit RSA provides strong security for healthcare data
private_key = key.export_key()
public_key = key.publickey().export_key()

print("✓ Bob's key pair generated successfully!")
print("- Key size: 2048 bits (meets healthcare security standards)")
print("- Public key can be shared openly (like publishing mailbox address)")
print("- Private key must be kept secret (like Bob's personal mailbox key)")
print()

# STEP 2: Public Key Distribution
print("STEP 2: Bob shares his public key with the hospital")
print("- Bob publishes his public key in the hospital directory")
print("- Alice and other doctors can now send him encrypted messages")
print("- Even if Eve (attacker) sees the public key, she cannot decrypt messages")
print()

print("Public Key (first 100 characters):", public_key.decode()[:100], "...")
print()

# STEP 3: Security Properties Explained
print("SECURITY PROPERTIES OF ASYMMETRIC ENCRYPTION:")
print("✓ Confidentiality: Only Bob can decrypt messages sent with his public key")
print("✓ Key Distribution: No need to share secret keys beforehand")
print("✓ Scalability: Each person needs only one key pair for all communications")
print()

print("HEALTHCARE BENEFITS:")
print("• Secure communication between different hospital departments")
print("• No need to pre-share secret keys between doctors")
print("• Supports secure telemedicine and remote consultations")
print("• Enables secure email for patient referrals")
print()

print("COMPARISON WITH SYMMETRIC ENCRYPTION:")
print("• Symmetric: Fast but has key-sharing problem")
print("• Asymmetric: Solves key-sharing but slower for large files")
print("• Best Practice: Use hybrid approach (RSA + AES)")
print()

print("NEXT STEPS:")
print("1. Alice can now encrypt messages using Bob's public key")
print("2. Only Bob can decrypt using his private key")
print("3. See 'pakage_encrypt.py' for complete hybrid encryption example")
print()

print("FILES CREATED: None (keys are displayed but not saved)")
print("NOTE: In production, private keys should be stored securely (HSM/TPM)")
