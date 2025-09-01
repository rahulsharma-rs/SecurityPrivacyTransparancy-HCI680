# Goal: simulate a time-based one-time password (TOTP) second factor.
# Requires: pip install pyotp
import pyotp, time

shared_secret = pyotp.random_base32()  # provisioned to Alice's authenticator app

totp = pyotp.TOTP(shared_secret)
code = totp.now()  # Alice reads this on her phone
print("TOTP code (demo):", code)

# Server verifies within a time window
assert totp.verify(code, valid_window=1), "MFA failed"
print("MFA passed for alice@hospital")

