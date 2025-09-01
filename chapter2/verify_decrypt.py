# verify_decrypt.py
import json, base64, jwt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

# Config (AS shared secret for demo)
AS_KEY = "hospital-oauth-lab-key"
REQUIRED_SCOPE = "patient/Imaging.read"

# Load artifacts
header = json.load(open("header.json"))
ciphertext = open("payload.bin","rb").read()

# 1) Validate token
access_token = open("token.jwt").read()
claims = jwt.decode(access_token, AS_KEY, algorithms=["HS256"], audience="https://decrypt.ehr.example")
assert REQUIRED_SCOPE in claims.get("scope",""), "missing scope"

# 2) Verify signature (Alice)
alice_pub = RSA.import_key(base64.b64decode(header["signer"]["alice_pub"]))
msg_hash = SHA256.new(json.dumps({k: header[k] for k in header if k != "signature"}, sort_keys=True).encode() + ciphertext)
try:
    pkcs1_15.new(alice_pub).verify(msg_hash, base64.b64decode(header["signature"]))
    print("Signature OK -- from Alice, header+payload untampered")
except Exception as e:
    raise SystemExit(f"Signature verification failed: {e}")

# 3) Unwrap AES key (Bob)
bob_priv = RSA.import_key(open("bob_private.pem","rb").read())
unwrapper = PKCS1_OAEP.new(bob_priv)
k = unwrapper.decrypt(base64.b64decode(header["wrapped_key"]))

# 4) Decrypt
aes = AES.new(k, AES.MODE_EAX, nonce=base64.b64decode(header["nonce"]))
plaintext = aes.decrypt_and_verify(ciphertext, base64.b64decode(header["tag"]))
open("radiology_report_decrypted.pdf","wb").write(plaintext)
print("Decryption OK -- wrote radiology_report.decrypted.pdf")

