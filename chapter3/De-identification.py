#!/usr/bin/env python3
"""
Demonstration of k-anonymity, l-diversity, and t-closeness
on a small synthetic healthcare dataset.

Context:
- Shows how limited datasets (Age, ZIP, Gender, Diagnosis)
  can still carry re-identification risks.
- Illustrates the effect of different generalization strategies
  on privacy metrics.
"""

import pandas as pd
import numpy as np

# ----------------------------
# 1) Dummy dataset (case study example)
# ----------------------------
data_raw = pd.DataFrame({
    'Age':     [28, 29, 29, 40, 40, 41],
    'ZIP':     ['35294', '35294', '35295', '35294', '35295', '35295'],
    'Gender':  ['F', 'M', 'F', 'M', 'F', 'M'],
    'Diagnosis': ['Asthma', 'Diabetes', 'Asthma', 'Cancer', 'Cancer', 'Diabetes']
})
SA_COL = 'Diagnosis'   # Sensitive attribute (SA)

# ----------------------------
# 2) Helper functions
# ----------------------------
def k_anonymity_pandas(df: pd.DataFrame, qi_cols: list[str]) -> int:
    """Compute k-anonymity: smallest group size based on QIs."""
    sizes = df.groupby(qi_cols, dropna=False).size()
    return int(sizes.min()) if len(sizes) > 0 else 0

def l_diversity_count(df: pd.DataFrame, qi_cols: list[str], sa_col: str) -> int:
    """Compute l-diversity: min number of distinct SA values in each group."""
    counts = df.groupby(qi_cols, dropna=False)[sa_col].nunique()
    return int(counts.min()) if len(counts) > 0 else 0

def distribution(series: pd.Series) -> dict:
    """Return normalized frequency distribution for a column."""
    counts = series.value_counts(dropna=False)
    total = counts.sum()
    return {k: v / total for k, v in counts.items()} if total > 0 else {}

def total_variation_distance(p: dict, q: dict) -> float:
    """Total variation distance between two distributions."""
    keys = set(p.keys()).union(q.keys())
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)

def t_closeness_tv(df: pd.DataFrame, qi_cols: list[str], sa_col: str) -> float:
    """
    Compute t-closeness using total variation distance.
    - For each equivalence class, compare SA distribution with global SA distribution.
    - Return the maximum deviation across groups.
    """
    global_dist = distribution(df[sa_col])
    max_tv = 0.0
    for _, sub in df.groupby(qi_cols, dropna=False):
        tv = total_variation_distance(distribution(sub[sa_col]), global_dist)
        if tv > max_tv:
            max_tv = tv
    return float(max_tv)

def report_violations(df: pd.DataFrame, qi_cols: list[str], sa_col: str, k_req: int, l_req: int, t_req: float):
    """Print a simple privacy report for given QI columns."""
    print(f"\n--- Privacy report for QI={qi_cols} ---")

    # k-anonymity
    sizes = df.groupby(qi_cols, dropna=False).size().reset_index(name='size')
    k_val = sizes['size'].min() if not sizes.empty else 0
    print(f"k-anonymity = {k_val}  (require k ≥ {k_req})")
    if k_val < k_req:
        print("  Groups violating k:")
        print(sizes[sizes['size'] < k_req].to_string(index=False))

    # l-diversity
    l_counts = df.groupby(qi_cols, dropna=False)[sa_col].nunique().reset_index(name='l_count')
    l_val = l_counts['l_count'].min() if not l_counts.empty else 0
    print(f"l-diversity = {l_val}  (require l ≥ {l_req})")
    if l_val < l_req:
        print("  Groups violating l:")
        print(l_counts[l_counts['l_count'] < l_req].to_string(index=False))

    # t-closeness
    t_val = t_closeness_tv(df, qi_cols, sa_col) if not df.empty else 0.0
    print(f"t-closeness (TV) = {t_val:.3f}  (require t ≤ {t_req})")
    if t_val > t_req:
        print("  t-closeness violated (group distribution too far from global).")

def band_age(age: int) -> str:
    """Group ages into 10-year bands (e.g., 20–29, 30–39)."""
    lower = (age // 10) * 10
    upper = lower + 9
    return f"{lower}-{upper}"

def zip3_prefix(z: str) -> str:
    """Generalize ZIP code: keep first 3 digits only."""
    z = str(z)
    return (z[:3] + "**") if len(z) >= 3 else z + "**"

# ----------------------------
# 3) Scenario A — RAW data
# ----------------------------
print("\n================= SCENARIO A: RAW DATA =================")
print(data_raw.to_string(index=False))
QI_A = ['Age', 'ZIP', 'Gender']
report_violations(data_raw, QI_A, SA_COL, k_req=2, l_req=2, t_req=0.20)

# ----------------------------
# 4) Scenario B — Light generalization
#    (Age bands + ZIP3 + Gender)
# ----------------------------
print("\n================= SCENARIO B: LIGHT GENERALIZATION =================")
data_B = data_raw.copy()
data_B['AgeBand'] = data_B['Age'].apply(band_age)
data_B['ZIP3']    = data_B['ZIP'].apply(zip3_prefix)
print(data_B[['AgeBand', 'ZIP3', 'Gender', SA_COL]].to_string(index=False))
QI_B = ['AgeBand', 'ZIP3', 'Gender']
report_violations(data_B, QI_B, SA_COL, k_req=2, l_req=2, t_req=0.20)

# ----------------------------
# 5) Scenario C — Stronger generalization
#    (drop Gender from QI → larger groups, higher k & l)
# ----------------------------
print("\n================= SCENARIO C: STRONGER GENERALIZATION =================")
QI_C = ['AgeBand', 'ZIP3']
print(data_B[QI_C + [SA_COL]].to_string(index=False))
report_violations(data_B, QI_C, SA_COL, k_req=3, l_req=2, t_req=0.34)

# ----------------------------
# 6) Optional: Compare with pycanon library if installed
# ----------------------------
try:
    from pycanon.anonymity import k_anonymity as k_anon_lib, l_diversity as l_div_lib
    print("\n================= OPTIONAL: pycanon comparison =================")
    print("k-anonymity (pycanon):", k_anon_lib(data_B, QI_C))
    print("l-diversity  (pycanon):", l_div_lib(data_B, QI_C, [SA_COL]))
except Exception:
    print("\n(pycanon not available; skipping comparison.)")
