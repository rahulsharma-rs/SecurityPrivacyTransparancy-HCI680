from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Alice creates a key
key = get_random_bytes(16)  # 128-bit AES key
cipher = AES.new(key, AES.MODE_EAX)

scan = b"CT Scan: Patient ID 12345, results normal"
ciphertext, tag = cipher.encrypt_and_digest(scan)

print("Encrypted Scan:", ciphertext)

