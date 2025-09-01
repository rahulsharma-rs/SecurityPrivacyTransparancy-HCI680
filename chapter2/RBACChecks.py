# Goal: enforce role- and attribute-based access for EHR resources.
from dataclasses import dataclass

@dataclass
class Subject:
    user: str
    role: str
    department: str
    purpose_of_use: str  # e.g., "treatment", "research"

@dataclass
class Resource:
    type: str  # e.g., "ImagingReport", "MedicationOrder"
    sensitivity: str  # e.g., "standard", "high"

rules = [
    lambda s, r: s.role == "Physician" and s.purpose_of_use == "treatment",
    lambda s, r: s.role == "Researcher" and r.sensitivity != "high",
]

def is_allowed(subj: Subject, res: Resource) -> bool:
    return any(rule(subj, res) for rule in rules)

alice = Subject("alice@hospital", role="Physician", department="Cardiology", purpose_of_use="treatment")
report = Resource("ImagingReport", sensitivity="high")
print("Access allowed?", is_allowed(alice, report))

