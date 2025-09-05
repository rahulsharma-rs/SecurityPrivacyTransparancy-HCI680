"""
Chapter 2.2.4: Hash Functions - Alice's tamper seal
Healthcare Use Case: Ensuring medical reports haven't been altered
Think of it like a wax seal - if anyone breaks it, you'll know!
"""

from Crypto.Hash import SHA256

# STEP 1: Alice's radiology report (sensitive medical data)
report = b"Radiology report: No abnormalities"
print("Original Report:", report.decode())

# STEP 2: Alice creates a SHA-256 "fingerprint" of the report
# This fingerprint is unique - even changing one letter creates a completely different hash
h = SHA256.new(report)
original_digest = h.hexdigest()

print("Report Fingerprint (Hash):", original_digest)

# STEP 3: Alice sends both the report AND the fingerprint to Bob
# Bob can verify the report wasn't tampered with by recalculating the hash

# DEMONSTRATION: What happens if Eve tampers with the report?
print("\n🔍 TAMPERING DETECTION TEST:")

# Eve tries to change "No abnormalities" to "Severe abnormalities"
tampered_report = b"Radiology report: Severe abnormalities"
tampered_hash = SHA256.new(tampered_report)
tampered_digest = tampered_hash.hexdigest()

print("Tampered Report:", tampered_report.decode())
print("Tampered Fingerprint:", tampered_digest)

# Bob compares the fingerprints
if original_digest == tampered_digest:
    print("✅ Report is authentic - no tampering detected")
else:
    print("❌ TAMPERING DETECTED! The report has been altered!")
    print("   Original fingerprint:", original_digest[:20], "...")
    print("   Current fingerprint: ", tampered_digest[:20], "...")

# KEY PROPERTIES of Hash Functions:
print("\n📚 HASH FUNCTION PROPERTIES:")
print("1. One-way: Can't reverse the hash to get original data")
print("2. Deterministic: Same input always gives same hash")
print("3. Avalanche effect: Tiny change = completely different hash")
print("4. Fixed size: Always 256 bits for SHA-256, regardless of input size")
