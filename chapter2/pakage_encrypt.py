# package_encrypt.py
import json, base64
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Random import get_random_bytes

# Load keys
alice_priv = RSA.import_key(open("alice_private.pem","rb").read())
bob_pub    = RSA.import_key(open("bob_public.pem","rb").read())

# Read the PDF
data = open("dummy_radiology_report.pdf","rb").read()

# 1) Symmetric key + encrypt
k = get_random_bytes(32)  # AES-256
cipher = AES.new(k, AES.MODE_EAX)  # AEAD mode
ciphertext, tag = cipher.encrypt_and_digest(data)

# 2) Wrap the AES key for Bob
wrap = PKCS1_OAEP.new(bob_pub)
wrapped_key = wrap.encrypt(k)

# 3) Build header (without signature)
header = {
  "alg": {"sym": "AES-EAX-256", "wrap": "RSA-OAEP", "sig": "RSASSA-PKCS1-v1_5-SHA256"},
  "nonce": base64.b64encode(cipher.nonce).decode(),
  "tag":   base64.b64encode(tag).decode(),
  "recipient": {"bob_pub_fp": SHA256.new(bob_pub.export_key()).hexdigest()},
  "wrapped_key": base64.b64encode(wrapped_key).decode(),
  "signer": {"alice_pub": base64.b64encode(alice_priv.publickey().export_key()).decode()}
}

# 4) Sign header + ciphertext digest
h = SHA256.new(json.dumps(header, sort_keys=True).encode() + ciphertext)
signature = pkcs1_15.new(alice_priv).sign(h)
header["signature"] = base64.b64encode(signature).decode()

# 5) Write envelope
open("header.json","w").write(json.dumps(header, indent=2))
open("payload.bin","wb").write(ciphertext)
print("Wrote header.json + payload.bin")