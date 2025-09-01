from Crypto.Hash import SHA256

report = b"Radiology report: No abnormalities"
h = SHA256.new(report)

print("Digest:", h.hexdigest())