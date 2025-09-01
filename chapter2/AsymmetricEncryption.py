from Crypto.PublicKey import RSA

# Bob generates his RSA key pair
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

print("Public Key:", public_key.decode()[:100], "...")

