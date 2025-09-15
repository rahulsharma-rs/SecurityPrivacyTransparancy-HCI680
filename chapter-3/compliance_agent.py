#!/usr/bin/env python
"""
compliance_agent.py

Hospital Privacy & Compliance Agent (LangChain-based)
- Uses your prebuilt, persistent vector DBs (FAISS) for HIPAA / GDPR / IRB.
- Parses an IRB PDF + a request JSON.
- Runs policy checks and generates a grounded report.

Embeddings backend:
  --embeddings openai    -> langchain_openai.OpenAIEmbeddings  (requires OPENAI_API_KEY)
  --embeddings local     -> sentence-transformers/all-MiniLM-L6-v2 (no key; offline)

IMPORTANT: You MUST load FAISS indexes with the SAME embedding model type that was used to build them.
If you originally built your FAISS stores with OpenAI embeddings, you must run with --embeddings openai.
If you built them with sentence-transformers, run with --embeddings local.

Usage:
  export OPENAI_API_KEY=sk-...   # only if using --embeddings openai or using ChatOpenAI for the report
  python compliance_agent.py \
    --db_root ./vectordb \
    --irb_pdf ./sample_irb_playbook.pdf \
    --request_json ./sample_request.json \
    --out ./verdict.json \
    --embeddings local
"""

import argparse, os, re, json
from typing import Dict, Any, List

from pypdf import PdfReader

# LangChain vector store
from langchain_community.vectorstores import FAISS

# LLM for the final narrative (optional; will gracefully fall back if not available)
try:
    from langchain_openai import ChatOpenAI
    HAVE_OPENAI_LLM = True
except Exception:
    HAVE_OPENAI_LLM = False

# ---------------- Config ----------------
DIRECT_IDENTIFIERS = {
    "name","names","full_name","mrn","medical_record_number","ssn","social",
    "address","addresses","phone","telephone","email","dob","date_of_birth","street"
}

IRB_FIELDS = {
    "population": r"Population:\s*(.+)",
    "timeframe": r"Timeframe:\s*(.+)",
    "sites": r"Sites:\s*(.+)",
    "approved_elements": r"Approved Data Elements:\s*(.+)",
    "identifiers_rule": r"Identifiers:\s*(.+)",
    "hipaa": r"HIPAA:\s*(.+)",
    "sharing": r"Sharing:\s*(.+)",
    "retention": r"Retention:\s*(.+)",
    "notes": r"Notes:\s*(.+)"
}

DEFAULT_POLICY_QUERIES = {
    "hipaa":[
        "HIPAA minimum necessary standard §164.502(b)",
        "HIPAA de-identification Safe Harbor or Expert Determination §164.514(b)",
        "HIPAA Limited Data Set and Data Use Agreement §164.514(e)",
        "HIPAA Authorization requirement §164.508"
    ],
    "gdpr":[
        "GDPR Article 6 lawful basis for processing health data",
        "GDPR Article 9 special category data and research safeguards",
        "GDPR international transfers Articles 44–49"
    ],
    "irb":[
        "45 CFR 46.109 IRB review requirements",
        "45 CFR 46.116 informed consent requirements"
    ]
}

# -------------- Helpers --------------
def load_irb_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join([p.extract_text() or "" for p in reader.pages])

def extract_irb_scope(text: str) -> Dict[str, Any]:
    scope = {}
    for key, pat in IRB_FIELDS.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            scope[key] = m.group(1).strip()
    if "sites" in scope:
        scope["sites"] = [s.strip() for s in re.split(r"[;,]", scope["sites"]) if s.strip()]
    if "approved_elements" in scope:
        elems = [e.strip().lower() for e in re.split(r"[;,]", scope["approved_elements"]) if e.strip()]
        scope["approved_elements"] = elems
    return scope

def get_embeddings(backend: str):
    """
    Returns an embeddings object compatible with how your FAISS DBs were built.
    backend: "openai" or "local"
    """
    if backend == "openai":
        # OpenAIEmbeddings (requires OPENAI_API_KEY)
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings()
    elif backend == "local":
        # Sentence-transformers local model (offline)
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    else:
        raise ValueError("Unsupported --embeddings backend. Use 'openai' or 'local'.")

def load_store(path: str, embeddings):
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Vector DB directory not found: {path}")
    # allow_dangerous_deserialization is required for FAISS persistence
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

def build_retrievers(db_root: str, embeddings, k: int = 4) -> Dict[str, Any]:
    paths = {
        "hipaa": os.path.join(db_root, "hipaa"),
        "gdpr":  os.path.join(db_root, "gdpr"),
        "irb":   os.path.join(db_root, "irb"),
    }
    retrievers = {}
    for name, p in paths.items():
        vs = load_store(p, embeddings)
        retrievers[name] = vs.as_retriever(search_kwargs={"k": k})
    return retrievers

# -------------- Policy rule checks --------------
def evaluate_rules(irb_scope: Dict[str,Any], req: Dict[str,Any]) -> List[Dict[str,Any]]:
    results = []

    # IRB scope alignment
    site_issues = [s for s in req.get("sites",[]) if s not in (irb_scope.get("sites") or [])]
    pop_ok = ("diabetes" in (req.get("population",{}).get("condition","").lower())) or \
             ("e11" in (req.get("population",{}).get("condition","").lower()))
    time_issue = False
    if "timeframe" in irb_scope and "time_window" in req:
        req_start = req["time_window"].split("to")[0].strip()
        # naive parse: infer IRB start if present
        irb_start = ""
        m = re.search(r"(\d{4})", irb_scope["timeframe"])
        if m:
            irb_start = f"{m.group(1)}-01-01"
        if irb_start and req_start < irb_start:
            time_issue = True

    issues = []
    if site_issues: issues.append(f"Sites not in IRB: {', '.join(site_issues)}")
    if not pop_ok: issues.append("Population condition may not match IRB scope.")
    if time_issue: issues.append("Requested start date precedes IRB timeframe.")
    results.append({
        "rule_set":"irb","id":"irb_scope_alignment","title":"IRB Scope Alignment",
        "pass": len(issues)==0, "detail": "; ".join(issues),
        "citations":["45 CFR 46.109","45 CFR 46.116"],
        "remediation":"Amend IRB or narrow request to align population/timeframe/sites/elements."
    })

    # HIPAA minimum necessary & De-ID/Limited Dataset
    requested = set(e.lower() for e in req.get("data_elements",[]))
    direct = [e for e in requested if e in DIRECT_IDENTIFIERS]
    if direct:
        results.append({
            "rule_set":"hipaa","id":"hipaa_minimum_necessary","title":"HIPAA Minimum Necessary",
            "pass": False, "detail":"Direct identifiers requested.",
            "citations":["HIPAA §164.502(b)"],
            "remediation":"Trim to minimum necessary; justify elements in DMP/IRB."
        })
        results.append({
            "rule_set":"hipaa","id":"hipaa_deid_or_limited","title":"HIPAA De-ID or Limited Dataset",
            "pass": False, "detail":"Prefer De-Identification or Limited Dataset + DUA.",
            "citations":["HIPAA §164.514(b)","HIPAA §164.514(e)"],
            "remediation":"Remove direct identifiers; De-ID or Limited Dataset + DUA."
        })
    else:
        results.append({
            "rule_set":"hipaa","id":"hipaa_minimum_necessary","title":"HIPAA Minimum Necessary",
            "pass": True, "detail":"", "citations":["HIPAA §164.502(b)"], "remediation":""
        })
        results.append({
            "rule_set":"hipaa","id":"hipaa_deid_or_limited","title":"HIPAA De-ID or Limited Dataset",
            "pass": True, "detail":"", "citations":["HIPAA §164.514(b)","HIPAA §164.514(e)"], "remediation":""
        })

    # HIPAA Authorization or Waiver
    hipaa_text = (irb_scope.get("hipaa") or "").lower()
    has_waiver = "waiver" in hipaa_text
    if direct and not has_waiver:
        results.append({
            "rule_set":"hipaa","id":"hipaa_auth_or_waiver","title":"HIPAA Authorization or IRB Waiver",
            "pass": False, "detail":"Identifiers with no HIPAA Authorization or IRB Waiver indicated.",
            "citations":["HIPAA §164.508"], "remediation":"Obtain Authorization or secure IRB Waiver."
        })
    else:
        results.append({
            "rule_set":"hipaa","id":"hipaa_auth_or_waiver","title":"HIPAA Authorization or IRB Waiver",
            "pass": True, "detail":"", "citations":["HIPAA §164.508"], "remediation":""
        })

    # GDPR checks if EU
    if "EU" in (req.get("jurisdictions") or []):
        results.append({
            "rule_set":"gdpr","id":"gdpr_lawful_basis","title":"GDPR Lawful Basis & Art.9",
            "pass": False, "detail":"Document Art.6 and Art.9(2) safeguards.",
            "citations":["GDPR Art.6","GDPR Art.9"], "remediation":"Record basis + safeguards (Art.89)."
        })
    else:
        results.append({
            "rule_set":"gdpr","id":"gdpr_lawful_basis","title":"GDPR Lawful Basis & Art.9",
            "pass": True, "detail":"Not in scope for this request.",
            "citations":["GDPR Art.6","GDPR Art.9"], "remediation":""
        })

    return results

def decide_verdict(results: List[Dict[str,Any]]) -> str:
    if any(r["rule_set"]=="irb" and not r["pass"] for r in results):
        return "Not allowed"
    if any(r["rule_set"]=="hipaa" and not r["pass"] for r in results):
        return "Allowed with conditions"
    return "Allowed"

def collect_policy_excerpts(retrievers: Dict[str,Any], queries: Dict[str, List[str]] = None) -> str:
    queries = queries or DEFAULT_POLICY_QUERIES
    excerpts = []
    for name, retr in retrievers.items():
        for q in queries.get(name, []):
            try:
                docs = retr.get_relevant_documents(q)
                if docs:
                    d = docs[0]
                    txt = (d.page_content or "").strip().replace("\n"," ")
                    src = d.metadata.get("source") or d.metadata.get("source_file") or name.upper()
                    excerpts.append(f"[{name.upper()}] {q} — {src}: {txt[:600]}")
            except Exception as e:
                excerpts.append(f"[{name.upper()}] {q}: (no excerpt: {e})")
    return "\n\n".join(excerpts)

def render_report_markdown(verdict: str, results: List[Dict[str,Any]], irb_scope: Dict[str,Any],
                           req: Dict[str,Any], excerpts: str, model_name: str = "gpt-4o-mini") -> str:
    """
    If ChatOpenAI is available and OPENAI_API_KEY is set, use LLM to draft a polished report.
    Otherwise, fallback to a deterministic text report.
    """
    if HAVE_OPENAI_LLM and os.environ.get("OPENAI_API_KEY"):
        llm = ChatOpenAI(model=model_name, temperature=0)
        prompt = f"""
You are a hospital privacy compliance AI. Produce a concise compliance report grounded in the provided policy excerpts.
Include a verdict, rationale bullets, required changes, and legal anchors (HIPAA § / GDPR Art. / 45 CFR 46).

Verdict: {verdict}

Findings JSON:
{json.dumps(results, indent=2)}

IRB Scope:
{json.dumps(irb_scope, indent=2)}

Request:
{json.dumps(req, indent=2)}

Policy Excerpts (for citations):
{excerpts}

Format exactly:
### Verdict
<Allowed | Allowed with conditions | Not allowed>

### Rationale
- ...

### Required Changes
1) ...

### Legal Anchors
- HIPAA ...
- GDPR ...
- IRB ...
"""
        return llm.invoke(prompt).content

    # Fallback deterministic rendering (no LLM)
    lines = []
    lines.append("### Verdict")
    lines.append(verdict)
    lines.append("\n### Rationale")
    for r in results:
        status = "PASS" if r["pass"] else "ISSUE"
        detail = f" — {r.get('detail','')}" if r.get("detail") else ""
        lines.append(f"- [{status}] {r['title']}{detail}")
    lines.append("\n### Required Changes")
    idx = 1
    for r in results:
        if not r["pass"]:
            rem = r.get("remediation","(remediation not specified)")
            lines.append(f"{idx}) {rem}")
            idx += 1
    if idx == 1:
        lines.append("No changes required.")
    lines.append("\n### Legal Anchors")
    anchors = set()
    for r in results:
        for c in r.get("citations",[]):
            anchors.add(c)
    for a in sorted(anchors):
        lines.append(f"- {a}")
    lines.append("\n### Policy Excerpts")
    lines.append(excerpts or "(no excerpts)")
    return "\n".join(lines)

# -------------- CLI --------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db_root", required=True, help="Path containing hipaa/, gdpr/, irb/ FAISS dirs")
    ap.add_argument("--irb_pdf", required=True, help="Path to IRB PDF to analyze")
    ap.add_argument("--request_json", required=True, help="Path to request JSON")
    ap.add_argument("--out", required=True, help="Output JSON path for verdict/report")
    ap.add_argument("--embeddings", choices=["openai","local"], default="openai",
                    help="Embedding backend; MUST match what the FAISS stores were built with.")
    ap.add_argument("--k", type=int, default=4, help="# of chunks to retrieve per corpus")
    ap.add_argument("--llm_model", default="gpt-4o-mini", help="OpenAI chat model for the report (if available)")
    args = ap.parse_args()

    # Load IRB + request
    irb_text = load_irb_text(args.irb_pdf)
    irb_scope = extract_irb_scope(irb_text)
    with open(args.request_json) as f:
        req = json.load(f)

    # Embeddings must match your FAISS build
    embeddings = get_embeddings(args.embeddings)

    # Build retrievers from your persistent stores
    retrievers = build_retrievers(args.db_root, embeddings, k=args.k)

    # Evaluate rules & decide verdict
    results = evaluate_rules(irb_scope, req)
    verdict = decide_verdict(results)

    # Pull short policy excerpts from each corpus
    excerpts = collect_policy_excerpts(retrievers)

    # Render final report (LLM if available, else deterministic)
    report_md = render_report_markdown(verdict, results, irb_scope, req, excerpts, model_name=args.llm_model)

    out_obj = {
        "verdict": verdict,
        "findings": results,
        "irb_scope": irb_scope,
        "report_markdown": report_md
    }
    with open(args.out, "w") as f:
        json.dump(out_obj, f, indent=2)
    print(f"[OK] Wrote {args.out} (verdict={verdict})")

if __name__ == "__main__":
    main()
