from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

pdf_path = "sample_irb_playbook.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)

lines = [
    "IRB Protocol: Multisite Outcomes Study in Adult Type 2 Diabetes",
    "Version: 2.0 (Approved)",
    "Population: Adults aged 18+ with Type 2 Diabetes (ICD-10: E11.*); Excludes pediatrics",
    "Timeframe: January 1, 2019 through December 31, 2025",
    "Sites: UAB-MainHospital; UAB-ClinicA",
    "Approved Data Elements: encounter dates; labs (A1c, fasting glucose); medications (insulin, metformin, GLP-1); demographics (age, sex, race); vitals (BMI, blood pressure)",
    "Identifiers: Direct identifiers are NOT approved for export; internal analysis may link via MRN in a secure enclave only",
    "HIPAA: IRB has approved a Waiver of Authorization for retrospective EHR review in a secure enclave",
    "Sharing: External sharing limited to De-identified or Limited Dataset with DUA; no raw identifiers may leave enclave",
    "Retention: Analysis workspace auto-deletes derived datasets after 24 months unless renewed",
    "Notes: Expansion to new sites, pediatrics, or new identifiers requires IRB amendment",
]

text = c.beginText(40, 730)
for line in lines:
    text.textLine(line)
c.drawText(text)
c.showPage()
c.save()

print(f"Generated {pdf_path}")
