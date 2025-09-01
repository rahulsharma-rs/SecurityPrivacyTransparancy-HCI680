from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

# Alice creates a key
key =  RSA.generate(2048) # 128-bit AES key
message = b"Prescription: Drug A, dosage 20mg"
h = SHA256.new(message)

signature = pkcs1_15.new(key).sign(h)
print("Signature:", signature.hex()[:50], "...")