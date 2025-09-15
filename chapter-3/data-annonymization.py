"""
This script generates a synthetic healthcare dataset using Faker, anonymizes it by removing names, masking birth dates and zip codes, and saves the anonymized data to a CSV file. It demonstrates Safe Harbor anonymization for privacy compliance.
"""
import pandas as pd
import faker, random

fake = faker.Faker()
data = {
"PatientID": range(1, 11),
"Name": [fake.name() for _ in range(10)],
"DOB": [fake.date_of_birth(minimum_age=20, maximum_age=90) for _ in range(10)],
"ZipCode": [fake.zipcode() for _ in range(10)],
"Diagnosis": [random.choice(["Diabetes", "Hypertension", "Asthma"]) for _ in range(10)]
}
df = pd.DataFrame(data)

# Safe Harbor anonymization
df_anon = df.copy()
df_anon.drop(columns=["Name"], inplace=True)
df_anon["DOB"] = df_anon["DOB"].astype(str).str[:4] # keep year only
df_anon["ZipCode"] = df_anon["ZipCode"].str[:3] + "XX"

print("Original Data:\n", df.head())
print("\nAnonymized Data:\n", df_anon.head())

#samve the anonymized data to a CSV file
df_anon.to_csv("anonymized_health_data.csv", index=False)