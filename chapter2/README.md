# Chapter 2: Cryptography and Authentication Basics for Healthcare

## 🏥 Welcome to Healthcare Security!

This chapter teaches you how to protect patient data using cryptography and authentication - the same techniques used in real hospitals to keep medical records safe. You'll learn through a story about Alice (a radiologist), Bob (a cardiologist), and Eve (a hacker trying to steal patient data).

## 📋 What You'll Learn

- **Encryption**: How to lock patient data so only authorized people can read it
- **Digital Signatures**: How to prove a medical document is authentic and hasn't been tampered with
- **Authentication**: How to verify that users are who they claim to be
- **Authorization**: How to control what different users can access

## 🛠️ Setup Instructions

### Prerequisites
1. Install Python 3.9 or higher from [python.org](https://python.org)
2. Download all files to a folder on your computer

### Step 1: Create Virtual Environment
<!-- Added virtual environment setup instructions -->
A virtual environment keeps your project dependencies separate from other Python projects.

**For Windows:**
\`\`\`bash
# Navigate to your project folder
cd path/to/chapter2

# Create virtual environment
python -m venv healthcare_crypto_env

# Activate virtual environment
healthcare_crypto_env\Scripts\activate
\`\`\`

**For macOS/Linux:**
\`\`\`bash
# Navigate to your project folder
cd path/to/chapter2

# Create virtual environment
python3 -m venv healthcare_crypto_env

# Activate virtual environment
source healthcare_crypto_env/bin/activate
\`\`\`

### Step 2: Install Required Packages
<!-- Updated package installation to use requirements.txt -->
\`\`\`bash
# Install all required packages at once
pip install -r requirements.txt

# OR install individually if needed:
# pip install pycryptodome pyjwt pyotp
\`\`\`

### Step 3: Verify Installation
\`\`\`bash
# Test that packages are installed correctly
python -c "from Crypto.Cipher import AES; import jwt; import pyotp; print('All packages installed successfully!')"
\`\`\`

### Important Notes:
- **Always activate your virtual environment** before running the scripts
- If you close your terminal, you'll need to activate the environment again
- To deactivate the environment when done: `deactivate`

### Getting Started
1. Open a terminal/command prompt in the folder where you downloaded the files
2. Follow the exercises below in order

## 📚 Learning Exercises

### Exercise 1: Understanding Basic Encryption
**Story**: Alice wants to encrypt a CT scan before sending it over the hospital network.

**Files to run**:
- `SymmetricEncryption.py` - Shows how Alice locks data with a secret key
- `AsymmetricEncryption.py` - Shows how Alice and Bob can share keys safely

**What happens**: These scripts demonstrate encryption without creating any new files.

---

### Exercise 2: Ensuring Data Integrity
**Story**: Alice wants to make sure her radiology report hasn't been tampered with.

**Files to run**:
- `HashFuctions.py` - Creates a digital "fingerprint" of the report
- `DigitalSignature.py` - Alice signs the report to prove it's authentic

**What happens**: These scripts show how to detect if Eve tries to modify the data.

---

### Exercise 3: Hospital Authentication Systems
**Story**: Alice needs to log into multiple hospital systems without entering her password repeatedly.

**Files to run in order**:
1. `SSO.py` - Simulates Alice's hospital badge working across systems
2. `Auto2o.py` - Shows how apps can access data on Alice's behalf
3. `OpenID.py` - Verifies Alice's identity
4. `MFASimulation.py` - Adds extra security with phone-based codes
5. `RBACChecks.py` - Controls what different staff members can access

**What happens**: These scripts demonstrate authentication without creating files.

---

### Exercise 4: Complete Document Security (Hands-On Lab)
**Story**: Alice needs to securely send a radiology PDF to Bob, ensuring Eve can't read or modify it.

**Important Note**: `pakage_encrypt.py` and `verify_decrypt.py` work together as a complete use case - you encrypt a document with the first script and decrypt it with the second script.

**Step 1: Generate Keys**
\`\`\`bash
python key_setup.py
\`\`\`
**Files created**:
- `alice_private.pem` - Alice's secret signing key (keep private!)
- `alice_public.pem` - Alice's public key for verification
- `bob_private.pem` - Bob's secret decryption key (keep private!)
- `bob_public.pem` - Bob's public key for encryption

**Step 2: Create Secure Package**
\`\`\`bash
python pakage_encrypt.py
\`\`\`
**Files created**:
- `header.json` - Contains encryption details and digital signature
- `payload.bin` - The encrypted radiology report

**Step 3: Issue Access Permission**
\`\`\`bash
python mint_token.py
\`\`\`
**Files created**:
- `token.jwt` - Digital permission slip allowing Bob to decrypt the file

**Step 4: Decrypt and Verify**
\`\`\`bash
python verify_decrypt.py
\`\`\`
**Files created**:
- `radiology_report_decrypted.pdf` - The original report, now safely decrypted

**⚠️ Token Expiration**: If you get a token expiration error when running `verify_decrypt.py`, simply re-run `mint_token.py` to create a fresh token. This simulates how real systems refresh expired access tokens.

---

## 🔍 Understanding the Security Process

### What Each File Does

| File | Purpose | Creates |
|------|---------|---------|
| `key_setup.py` | Generates encryption keys for Alice and Bob | 4 PEM key files |
| `pakage_encrypt.py` | Encrypts and signs the medical document | `header.json`, `payload.bin` |
| `mint_token.py` | Creates permission to decrypt | `token.jwt` |
| `verify_decrypt.py` | Checks permissions and decrypts safely | Decrypted PDF |

### Security Layers Explained

1. **Encryption** (AES-256): Scrambles the data so Eve can't read it
2. **Key Wrapping** (RSA): Protects the encryption key using Bob's public key
3. **Digital Signature**: Proves the document came from Alice and wasn't modified
4. **Access Token**: Controls who can decrypt the document and when

## 🚨 Testing Security (Try These!)

### Test 1: Wrong Permissions
1. Delete `token.jwt`
2. Run `verify_decrypt.py`
3. **Result**: Access denied! The system protects the data.

### Test 2: Expired Token
1. Wait a few minutes after running `mint_token.py`
2. Run `verify_decrypt.py`
3. **Result**: Token expired! Re-run `mint_token.py` to refresh the token.

### Test 3: Tampered Data
1. Open `header.json` and change any character
2. Run `verify_decrypt.py`
3. **Result**: Signature verification fails! Tampering detected.

### Test 4: Wrong Recipient
1. Delete Bob's key files
2. Run `key_setup.py` to create new ones
3. Try `verify_decrypt.py`
4. **Result**: Decryption fails! The data was encrypted for the original Bob.

## ❓ Troubleshooting

**Problem**: "ModuleNotFoundError"
**Solution**: Install missing libraries with `pip install pycryptodome pyjwt pyotp`

**Problem**: "File not found"
**Solution**: Make sure you run the scripts in the correct order (key_setup.py first!)

**Problem**: "Token has expired" or "JWT expired"
**Solution**: Re-run `mint_token.py` to generate a fresh access token, then try `verify_decrypt.py` again

**Problem**: "Signature verification failed"
**Solution**: Don't modify the header.json or payload.bin files between encryption and decryption

## 🎯 Learning Objectives

By completing this chapter, you will:
- Understand how hospitals protect patient data
- Know the difference between encryption and digital signatures
- Recognize common authentication methods in healthcare
- Appreciate the balance between security and usability in medical settings
- Be able to implement basic cryptographic protections for sensitive documents

## 🔗 Next Steps

After mastering these concepts, you'll be ready to explore:
- Advanced key management systems
- Healthcare-specific protocols (SMART on FHIR)
- Compliance requirements (HIPAA, GDPR)
- Cloud security for medical data

---

**Remember**: In real healthcare systems, protecting patient data isn't just about technology - it's about saving lives and maintaining trust. Every security measure you implement helps keep sensitive medical information safe from those who would misuse it.
