"""
Chapter 2: Multi-Factor Authentication (MFA) Simulation
Healthcare Use Case: Alice needs both her password AND her phone to access
the EHR system, preventing Eve from breaking in with just a stolen password.

Learning Objectives:
- Understand the three authentication factors
- Learn how TOTP (Time-based One-Time Passwords) work
- See why MFA is critical in healthcare environments
"""


# Requires: pip install pyotp
import pyotp, time

print("=== Chapter 2.3.4: Multi-Factor Authentication Demo ===")
print("Healthcare Story: Alice logs into the EHR with password + phone")
print()

# STEP 1: Provision Shared Secret
print("STEP 1: Hospital IT provisions Alice's authenticator app")
print("  - This happens once during setup (like getting a hospital badge)")
print("  - The secret is shared between hospital server and Alice's phone")

shared_secret = pyotp.random_base32()  # In reality, this is securely provisioned
print(f"  ✓ Shared secret created: {shared_secret[:8]}... (truncated for security)")
print("  → Alice scans QR code to add this to her authenticator app")
print()

# STEP 2: Generate Time-Based One-Time Password
print("STEP 2: Alice's phone generates a 6-digit code")
print("  - Code changes every 30 seconds")
print("  - Based on current time + shared secret")
print("  - Even if Eve sees this code, it expires quickly")

totp = pyotp.TOTP(shared_secret)
code = totp.now()  # This is what Alice sees on her phone
print(f"  📱 Alice's phone shows: {code}")
print(f"  ⏰ Code valid for: {30 - (int(time.time()) % 30)} more seconds")
print()

# STEP 3: Hospital Server Verifies Code
print("STEP 3: Hospital EHR system verifies Alice's code")
print("  - Server generates expected code using same secret")
print("  - Allows small time window for clock differences")

try:
    # Server verification (allows 1 time step tolerance)
    is_valid = totp.verify(code, valid_window=1)
    if is_valid:
        print("  ✓ MFA verification successful!")
        print("  → Alice gains access to patient records")
    else:
        print("  ✗ MFA verification failed")
        print("  → Access denied")
except Exception as e:
    print(f"  ✗ MFA error: {e}")

print()

# STEP 4: Security Demonstration
print("STEP 4: Why MFA protects against Eve")
print("Authentication Factors:")
print("  1. Something Alice KNOWS: Password")
print("  2. Something Alice HAS: Phone with authenticator app")
print("  3. Something Alice IS: Fingerprint/face (not shown here)")
print()
print("Security Benefits:")
print("  • Even if Eve steals Alice's password, she can't access EHR")
print("  • Eve would need BOTH password AND Alice's physical phone")
print("  • Codes expire every 30 seconds (limited replay window)")
print("  • No network connection needed for code generation")
print()

print("=== Key Takeaways ===")
print("• MFA requires multiple independent factors")
print("• TOTP codes are time-synchronized and expire quickly")
print("• Critical for healthcare: protects patient data even with password theft")
print("• Real hospitals often use: password + smart card + fingerprint")
