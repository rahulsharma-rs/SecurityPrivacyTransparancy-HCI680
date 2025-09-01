# mint_token.py
import time, jwt
SIGNING_KEY = "hospital-oauth-lab-key"  # demo only; use RSA/EC in production

claims = {
  "iss": "https://id.hospital.example",
  "sub": "bob@hospital",
  "aud": "https://decrypt.ehr.example",
  "scope": "patient/Imaging.read",
  "exp": int(time.time()) + 900
}
access_token = jwt.encode(claims, SIGNING_KEY, algorithm="HS256")
open("token.jwt","w").write(access_token)
print("Minted token.jwt with scope patient/Imaging.read")

