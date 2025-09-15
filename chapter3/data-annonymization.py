"""
This script generates a synthetic healthcare dataset using Faker,
then anonymizes it to demonstrate HIPAA Safe Harbor anonymization.

Steps:
1. Generate fake patient records (Name, DOB, Zip, Diagnosis).
2. Apply anonymization:
   - Remove names
   - Keep only year of birth
   - Mask last two digits of ZIP code
3. Save anonymized dataset to CSV file.
"""

import pandas as pd
import faker, random

# Initialize Faker for synthetic (fake) patient data
fake = faker.Faker()

# Create dummy dataset with 10 patients
data = {
    "PatientID": range(1, 11),  # unique patient IDs
    "Name": [fake.name() for _ in range(10)],  # fake names
    "DOB": [fake.date_of_birth(minimum_age=20, maximum_age=90) for _ in range(10)],  # fake birth dates
    "ZipCode": [fake.zipcode() for _ in range(10)],  # fake ZIP codes
    "Diagnosis": [random.choice(["Diabetes", "Hypertension", "Asthma"]) for _ in range(10)]  # random diagnosis
}

# Convert dictionary into DataFrame
df = pd.DataFrame(data)

# ---------------- Safe Harbor Anonymization ----------------
df_anon = df.copy()
df_anon.drop(columns=["Name"], inplace=True)           # remove names (direct identifier)
df_anon["DOB"] = df_anon["DOB"].astype(str).str[:4]    # keep only year of birth
df_anon["ZipCode"] = df_anon["ZipCode"].str[:3] + "XX" # mask ZIP (only first 3 digits kept)

# Show sample before and after anonymization
print("Original Data:\n", df.head())
print("\nAnonymized Data:\n", df_anon.head())

# Save anonymized dataset for later use (e.g., Q&A agent demo)
df_anon.to_csv("anonymized_health_data.csv", index=False)
