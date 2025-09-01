# keys_setup.py
from Crypto.PublicKey import RSA

# Alice signs with this (keep private key secret)
alice_key = RSA.generate(2048)
open("alice_private.pem", "wb").write(alice_key.export_key())
open("alice_public.pem",  "wb").write(alice_key.publickey().export_key())

# Bob receives and decrypts (keep private key secret)
bob_key = RSA.generate(2048)
open("bob_private.pem", "wb").write(bob_key.export_key())
open("bob_public.pem",  "wb").write(bob_key.publickey().export_key())
print("Keys created: alice_private/public.pem, bob_private/public.pem")