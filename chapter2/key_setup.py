"""
Chapter 2: RSA Key Pair Generation for Healthcare PKI
Healthcare Use Case: Setting up cryptographic identities for Alice (radiologist) 
and Bob (cardiologist) to enable secure communication.

Learning Objectives:
- Understand public-private key pairs
- Learn about PKI in healthcare settings
- See how keys enable both encryption and digital signatures
"""


from Crypto.PublicKey import RSA

print("=== Chapter 2.2: Public Key Infrastructure (PKI) Setup ===")
print("Healthcare Story: Creating digital identities for Alice and Bob")
print()

# STEP 1: Generate Alice's Key Pair (Radiologist)
print("STEP 1: Generating Alice's RSA key pair (2048-bit)")
print("  - Alice needs keys to sign radiology reports")
print("  - Private key: Alice keeps this secret (like her medical license)")
print("  - Public key: Everyone can verify Alice's signatures")

alice_key = RSA.generate(2048)  # Generate 2048-bit RSA key pair

# Save Alice's private key (MUST be kept secret!)
alice_private_pem = alice_key.export_key()
open("alice_private.pem", "wb").write(alice_private_pem)
print("  ✓ Created alice_private.pem (KEEP SECRET!)")

# Save Alice's public key (can be shared publicly)
alice_public_pem = alice_key.publickey().export_key()
open("alice_public.pem", "wb").write(alice_public_pem)
print("  ✓ Created alice_public.pem (shareable)")
print()

# STEP 2: Generate Bob's Key Pair (Cardiologist)
print("STEP 2: Generating Bob's RSA key pair (2048-bit)")
print("  - Bob needs keys to receive encrypted reports from Alice")
print("  - Private key: Bob uses this to decrypt messages sent to him")
print("  - Public key: Alice uses this to encrypt messages for Bob")

bob_key = RSA.generate(2048)  # Generate 2048-bit RSA key pair

# Save Bob's private key (MUST be kept secret!)
bob_private_pem = bob_key.export_key()
open("bob_private.pem", "wb").write(bob_private_pem)
print("  ✓ Created bob_private.pem (KEEP SECRET!)")

# Save Bob's public key (can be shared publicly)
bob_public_pem = bob_key.publickey().export_key()
open("bob_public.pem", "wb").write(bob_public_pem)
print("  ✓ Created bob_public.pem (shareable)")
print()

print("=== Files Created ===")
print("Alice's Keys:")
print("  • alice_private.pem - Alice's private key (for signing & decrypting)")
print("  • alice_public.pem  - Alice's public key (for verification & encrypting to Alice)")
print()
print("Bob's Keys:")
print("  • bob_private.pem   - Bob's private key (for signing & decrypting)")
print("  • bob_public.pem    - Bob's public key (for verification & encrypting to Bob)")
print()

print("=== Key Takeaways ===")
print("• Each person has a key pair: one private (secret), one public (shareable)")
print("• Private keys must be protected like medical licenses")
print("• Public keys can be shared in a hospital directory")
print("• This enables secure communication without pre-shared secrets")
print("• In real hospitals, keys are stored in smart cards or HSMs")
