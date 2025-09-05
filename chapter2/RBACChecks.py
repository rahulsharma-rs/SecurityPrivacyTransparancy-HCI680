"""
Chapter 2: Role-Based Access Control (RBAC) in Healthcare
========================================================

Healthcare Story: Hospital Control Tower
Alice (Physician) needs access to patient imaging reports for treatment.
Bob (Researcher) can only access de-identified, non-sensitive data.
Eve (Attacker) should be blocked from accessing any patient data.

Learning Objectives:
- Understand role-based and attribute-based access control
- Learn how hospitals enforce "need-to-know" principles
- See how purpose-of-use affects data access permissions
- Implement fine-grained authorization policies

Security Concept: Authorization vs Authentication
- Authentication: "Who are you?" (covered in other files)
- Authorization: "What are you allowed to do?" (this file)
"""

# Goal: enforce role- and attribute-based access for EHR resources.
from dataclasses import dataclass


# Step 1: Define the Subject (Who is requesting access?)
# In healthcare: doctors, nurses, researchers, administrators
@dataclass
class Subject:
    user: str  # Unique identifier (e.g., alice@hospital)
    role: str  # Job function (Physician, Nurse, Researcher)
    department: str  # Hospital department (Cardiology, Radiology)
    purpose_of_use: str  # Why accessing data? "treatment", "research", "billing"


# Step 2: Define the Resource (What is being accessed?)
# In healthcare: patient records, imaging, lab results, medications
@dataclass
class Resource:
    type: str  # Type of medical data (ImagingReport, MedicationOrder, LabResult)
    sensitivity: str  # Data classification (standard, high, restricted)


# Step 3: Define Access Control Rules
# These rules implement hospital policies and regulatory requirements (HIPAA)
rules = [
    # Rule 1: Physicians can access any data for treatment purposes
    # Healthcare Use Case: Doctor treating a patient needs full access
    lambda s, r: s.role == "Physician" and s.purpose_of_use == "treatment",

    # Rule 2: Researchers can only access non-sensitive data
    # Healthcare Use Case: Medical research with de-identified data
    lambda s, r: s.role == "Researcher" and r.sensitivity != "high",

    # Additional rules can be added here:
    # - Nurses: limited access based on assigned patients
    # - Billing staff: only billing-related data
    # - Emergency access: override rules during medical emergencies
]


# Step 4: Authorization Decision Function
# This is the "control tower" that enforces hospital access policies
def is_allowed(subj: Subject, res: Resource) -> bool:
    """
    Determines if a subject can access a resource based on defined rules.

    Security Properties:
    - Principle of Least Privilege: Users get minimum necessary access
    - Need-to-Know: Access based on job requirements and purpose
    - Separation of Duties: Different roles have different permissions

    Returns True if ANY rule allows access, False otherwise.
    """
    return any(rule(subj, res) for rule in rules)


# Step 5: Test the Access Control System
# Scenario: Alice (Physician) wants to access a high-sensitivity imaging report for treatment
print("=== Healthcare RBAC Access Control Test ===")
print()

# Create Alice's identity and access request
alice = Subject("alice@hospital", role="Physician", department="Cardiology", purpose_of_use="treatment")
report = Resource("ImagingReport", sensitivity="high")

print(f"Subject: {alice.user}")
print(f"Role: {alice.role}")
print(f"Department: {alice.department}")
print(f"Purpose: {alice.purpose_of_use}")
print()
print(f"Requesting access to: {report.type}")
print(f"Data sensitivity: {report.sensitivity}")
print()

# Make authorization decision
access_granted = is_allowed(alice, report)
print("Access allowed?", access_granted)

if access_granted:
    print("✅ GRANTED: Alice can access the imaging report for patient treatment")
else:
    print("❌ DENIED: Access request violates hospital policy")

print()
print("=== Additional Test Cases ===")

# Test Case 2: Researcher trying to access high-sensitivity data
bob_researcher = Subject("bob@hospital", role="Researcher", department="Research", purpose_of_use="research")
sensitive_data = Resource("GeneticData", sensitivity="high")
print(f"Researcher access to sensitive genetic data: {is_allowed(bob_researcher, sensitive_data)}")

# Test Case 3: Researcher accessing standard sensitivity data
standard_data = Resource("LabResult", sensitivity="standard")
print(f"Researcher access to standard lab results: {is_allowed(bob_researcher, standard_data)}")

print()
print("=== Security Demonstration ===")
print("This RBAC system prevents:")
print("- Unauthorized access to patient data")
print("- Data breaches from role confusion")
print("- Compliance violations (HIPAA, GDPR)")
print("- Insider threats from excessive privileges")
