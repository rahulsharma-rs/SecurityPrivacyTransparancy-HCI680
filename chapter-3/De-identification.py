"""
This code demonstrates how to assess the privacy of a small healthcare dataset using k-anonymity and l-diversity metrics. It creates a sample dataset with quasi-identifiers and a sensitive attribute, calculates k-anonymity and l-diversity using the pycanon library, and prints the results to show potential privacy risks.
Hands-on exercises are critical for understanding de-identification and re-identification risks. Beyond theory, practical coding examples allow consultants, students, and researchers to see how privacy techniques operate in real-world scenarios.
Use-Case Scenario:
A hospital wants to share a dataset with external researchers studying asthma outcomes without exposing patient identities. The dataset includes quasi-identifiers (age, ZIP code, gender) and sensitive attributes (diagnosis). Even though direct identifiers have been removed, the combination of quasi-identifiers poses a re-identification risk.
Case Study Example (Dummy Data):
Suppose we have the following records:
Age | ZIP   | Gender | Diagnosis
----------------------------------
28  | 35294 | F      | Asthma
29  | 35294 | M      | Diabetes
29  | 35295 | F      | Asthma
40  | 35294 | M      | Cancer
40  | 35295 | F      | Cancer
41  | 35295 | M      | Diabetes
This dataset seems safe at first glance. However, a motivated adversary with access to public voter rolls (containing age, gender, ZIP) might re-identify patients, especially in sparsely populated ZIP codes.

"""
import pandas as pd
from pycanon.anonymity import k_anonymity, l_diversity

# Example dataset with quasi-identifiers and sensitive attribute
data = pd.DataFrame({
    'Age': [28, 29, 29, 40, 40, 41],
    'ZIP': ['35294', '35294', '35295', '35294', '35295', '35295'],
    'Gender': ['F', 'M', 'F', 'M', 'F', 'M'],
    'Diagnosis': ['Asthma', 'Diabetes', 'Asthma', 'Cancer', 'Cancer', 'Diabetes']
})

# Check for k-anonymity (using quasi-identifiers: Age, ZIP, Gender)
k_val = k_anonymity(data, ['Age', 'ZIP', 'Gender'])
print("K-anonymity:", k_val)



l_val = l_diversity(data, ['Age', 'ZIP', 'Gender'], ['Diagnosis'])
print("L-diversity:", l_val)


import pandas as pd
from pycanon.anonymity import k_anonymity, l_diversity

data = pd.DataFrame({
    'Age': [28, 29, 29, 40, 40, 41],
    'ZIP': ['35294', '35294', '35295', '35294', '35295', '35295'],
    'Gender': ['F', 'M', 'F', 'M', 'F', 'M'],
    'Diagnosis': ['Asthma', 'Diabetes', 'Asthma', 'Cancer', 'Cancer', 'Diabetes']
})

qi = ['Age', 'ZIP', 'Gender']
sa = ['Diagnosis']

k_val = k_anonymity(data, qi)
print("K-anonymity:", k_val)

# Show groups with k=1
grouped = data.groupby(qi).size().reset_index(name='count')
violating_k = grouped[grouped['count'] == 1]
if not violating_k.empty:
    print("Rows violating k-anonymity (k=1):")
    print(violating_k)

l_val = l_diversity(data, qi, sa)
print("L-diversity:", l_val)

# Show groups with l=1
grouped_l = data.groupby(qi)['Diagnosis'].nunique().reset_index(name='l_count')
violating_l = grouped_l[grouped_l['l_count'] == 1]


# Show groups with l=1 (violating l-diversity)
grouped_l = data.groupby(qi)['Diagnosis'].nunique().reset_index(name='l_count')
violating_l = grouped_l[grouped_l['l_count'] == 1]
if not violating_l.empty:
    print("Rows violating l-diversity (l=1):")
    print(violating_l)