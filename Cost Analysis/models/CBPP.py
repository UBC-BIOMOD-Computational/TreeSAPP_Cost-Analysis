import pandas as pd
import numpy as np
import conversion as cv

"""
Sivashanmugam, A., Murray, V., Cui, C., Zhang, Y., Wang, J., & Li, Q. (2009). 
Practical protocols for production of very high yields of recombinant proteins using Escherichia coli. 
Protein Science, 18(5), 936–948. https://doi.org/10.1002/pro.102
"""
df = pd.DataFrame(columns=['section', 'section_time', 'name', 'value', 'unit'])

## Cell-Based Protein Expression Starting Requirements ======================
target_protein_annual = {'name': 'Target Protein', 'value': 0.001, 'unit': 'kg'}
cycles = {'name': 'Total Cycles', 'value': 10, 'unit': 'cycles'}
target_protein = {'name': 'Target Protein Per Cycle', 'value': cv.convert_units_grams(target_protein_annual['value'] / cycles['value'], 'kg', 'g'), 'unit': 'g'}

df1 = pd.DataFrame([target_protein_annual, cycles, target_protein])
df1['section'] = 'Starting Requirements'
df1['section_time'] = 0
df = pd.concat([df, df1])


## Volumes after lysis/centrifugation ======================
'''
"
- protein produced
14 mg of NMR triple-labeled proteins and 17 mg of unlabeled proteins from a 50-mL cell culture for all seven proteins we tested (OD600 of 15–20)
https://onlinelibrary.wiley.com/doi/10.1002/pro.102 
meaning => 17mg per 50mL of cellculture

https://pmc.ncbi.nlm.nih.gov/articles/PMC6190294/  - high pressure homogenizer"
'''

total_cell_culture_volume = {'name': 'Total Cell Culture Volume', 'value': cv.convert_units_grams(target_protein['value'], 'g', 'mg') / 17 * 50, 'unit': 'mL'}

df2 = pd.DataFrame([total_cell_culture_volume])
df2['section'] = 'Volumes after Lysis/Centrifugation'
df2['section_time'] = '2 hours'
df = pd.concat([df, df2])

## induction + incubation calculations ======================
'''
0.5mg of IPTG for every 50mL of cell culture
https://onlinelibrary.wiley.com/doi/10.1002/pro.102 

 induced at 0.5 mM IPTG (plus Zn²⁺), then incubated overnight (~16–20 h) at 20 °C.
https://microbialcellfactories.biomedcentral.com/articles/10.1186/s12934-024-02463-5
'''

total_IPTG = {'name': 'Total IPTG', 'value': 0.5 * (total_cell_culture_volume['value'] / 50), 'unit': 'mg'}

df3 = pd.DataFrame([total_IPTG])
df3['section'] = 'Induction + Incubation'
df3['section_time'] = '36 hours'
df = pd.concat([df, df3])

## Rapid Cell-Growth to OD600 = 15 =====================
'''
- E. coli K–12 exhibits a doubling time of ~20 min in exponential phase
https://pmc.ncbi.nlm.nih.gov/articles/PMC2168924/ 

 optical density (OD), you can use the formula μ = (ln OD₂ - ln OD₁) / (t₂ - t₁),

- 2.66 × 10⁹ ecoli cells/mL @ 1.0 OD600 unit. 1 OD600 unit is when a 1 mL sample of culture is measured and gives an absorbance of 1.0 at 600 nm. https://www.tipbiosystems.com/wp-content/uploads/2023/12/AN102-E.coli-Cell-Count_2019_04_25.pdf 

media: using table 1 
https://onlinelibrary.wiley.com/doi/10.1002/pro.102 
25 mM KH2PO4 (pH 8.0–8.2); mw: 136.09 g/mol
10 mM NaCl;  mw:58.44 g/mol
5 mM MgSO4;  mw:120.361 g/mol
0.2 mM CaCl2;  mw:110.98 g/mol
0.25× Metals
0.25× Vitamins
0.1% NH4Cl or 15NH4Cl  = 0.1 g per 100 mL of solution
1.0% Glucose or 13C-Glucose =  1 g of glucose per 100 mL of solution

0.1 ml of 0.5% thiamine vitamin B, per L of solution 
https://pmc.ncbi.nlm.nih.gov/articles/PMC6819147/

100uM which is 100 micromoles of iron per L of medium; 5.585 mg of iron per liter 
https://pmc.ncbi.nlm.nih.gov/articles/PMC9444934/#S1

time: 5 + 3 hours 
= 5 is growing proper starting culture overnight to reach OD600 = 3
= 3 is for doubling to reach OD600 = 15
'''

total_LB = {'name': 'Total LB', 'value': round(cv.convert_units_liters(total_cell_culture_volume['value'], 'mL', 'L')), 'unit': 'L'}
total_KH2PO4 = {'name': 'Total KH2PO4', 'value': total_LB['value'] * 0.025 * 136.09, 'unit': 'g'}
total_NaCl = {'name': 'Total NaCl', 'value': total_LB['value'] * 0.01 * 58.44, 'unit': 'g'}
total_MgSO4 = {'name': 'Total MgSO4', 'value': total_LB['value'] * 0.005 * 120.361, 'unit': 'g'}
total_CaCl2 = {'name': 'Total CaCl2', 'value': total_LB['value'] * 0.0002 * 110.98, 'unit': 'g'}
total_NH4Cl = {'name': 'Total NH4Cl', 'value': total_cell_culture_volume['value'] / 100 * 0.1, 'unit': 'g'}
total_glucose = {'name': 'Total Glucose', 'value': total_cell_culture_volume['value'] / 100, 'unit': 'g'}
total_vitamin_b = {'name': 'Total Vitamin B', 'value': total_LB['value'] * 0.1, 'unit': 'mL'}
total_iron = {'name': 'Total Iron', 'value': total_LB['value'] *  5.585 , 'unit': 'mg'}

df4 = pd.DataFrame([total_LB, total_KH2PO4, total_NaCl, total_MgSO4, total_CaCl2, total_NH4Cl, total_glucose, total_vitamin_b, total_iron])
df4['section'] = 'Growth Time'
df4['section_time'] = '8 hours'
df = pd.concat([df, df4])

## Export =====================
df.to_csv('data/CBPP.csv', index=False)

