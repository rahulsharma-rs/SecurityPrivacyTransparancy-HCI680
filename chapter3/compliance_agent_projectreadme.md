# 🏥 Hospital Privacy & Compliance Agent — Workflow

This project uses **LangChain** + **vector databases (FAISS)** to check if a researcher’s data request is compliant with **HIPAA, GDPR, and IRB** requirements.

---

## 📂 Project Structure

```
chapter3/
  vectordb/               # persistent FAISS vector DBs
    hipaa/
    gdpr/
    irb/
  GDPR.pdf                # source docs used to build vector DB
  hipaa.pdf
  research-IRB.pdf
  sample_irb_playbook.pdf # example IRB protocol (PDF)
  sample_request.json     # compliant request example
  sample_request_noncompliant.json # non-compliant request example
  compliance_agent.py     # main compliance agent
  build_vectorstores.py   # script to build FAISS indexes
  agent_with_tools.py     # (optional) interactive agent across corpora
```

---

## ⚙️ Workflow

1. **Build Vector Databases (once)**

   * Convert HIPAA, GDPR, and IRB reference PDFs into FAISS vector stores.
   * Command:

     ```bash
     python build_vectorstores.py \
       --gdpr GDPR.pdf \
       --irb IRB.pdf \
       --hipaa hipaa.pdf \
       --out ./vectordb \
       --backend openai
     ```
   * Creates `vectordb/hipaa/`, `vectordb/gdpr/`, `vectordb/irb/` with `index.faiss` + `index.pkl`.

2. **Prepare Inputs**

   * **IRB PDF** → e.g., `sample_irb_playbook.pdf` (approved protocol).
   * **Request JSON** → e.g., `sample_request.json` (researcher’s request).

3. **Run Compliance Agent**

   * Example (OpenAI embeddings):

     ```bash
     export OPENAI_API_KEY=sk-...
     python compliance_agent.py \
       --db_root ./vectordb \
       --irb_pdf sample_irb_playbook.pdf \
       --request_json sample_request.json \
       --out verdict.json \
       --embeddings openai
     ```
   * Or with local embeddings:

     ```bash
     python compliance_agent.py \
       --db_root ./vectordb \
       --irb_pdf sample_irb_playbook.pdf \
       --request_json sample_request.json \
       --out verdict.json \
       --embeddings local
     ```

4. **Review Output**

   * Output file: `verdict.json`
   * Contains:

     * **verdict**: Allowed / Allowed with conditions / Not allowed
     * **findings**: Rule-by-rule pass/fail
     * **irb\_scope**: Extracted info from IRB PDF
     * **report\_markdown**: Human-readable report (with legal anchors + remediation steps)

---

## 🧪 Test Cases

* ✅ `sample_request.json` → Mostly compliant, should be **Allowed** or **Allowed with conditions**.
* ❌ `sample_request_noncompliant.json` → Requests pediatrics + identifiers + external sharing, should be **Not allowed**.

---

## 🔑 Key Ideas

* **Vector DBs** = persistent memory of HIPAA, GDPR, IRB policies.
* **IRB PDF parsing** = what’s approved.
* **Request JSON** = what’s asked for.
* **Agent** = compares request vs. IRB scope + laws → generates compliance verdict.
