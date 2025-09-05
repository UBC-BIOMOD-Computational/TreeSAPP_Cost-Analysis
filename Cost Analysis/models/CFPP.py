import pandas as pd
import conversion as cv

"""
Cell-Free Protein Expression
Park, N., Kahn, J., Rice, E. et al. High-yield cell-free protein production from P-gel. Nat Protoc 4, 1759–1770 (2009). https://doi.org/10.1038/nprot.2009.174

"""


df = pd.DataFrame(columns=['section', 'section_time', 'name', 'value', 'unit'])

## Cell-Free Protein Expression Starting Requirements ======================
target_protein_annual = {'name': 'Target Protein', 'value': 0.05, 'unit': 'kg'}
cycles = {'name': 'Total Cycles', 'value': 50, 'unit': 'cycles'}
target_protein = {'name': 'Target Protein Per Cycle', 'value': cv.convert_units_grams(target_protein_annual['value'] / cycles['value'], 'kg', 'g'), 'unit': 'g'}

df1 = pd.DataFrame([target_protein_annual, cycles, target_protein])
df1['section'] = 'Starting Requirements'
df1['section_time'] = 0
df = pd.concat([df, df1])

## Cell-Free Protein Expression Calculations =====================
'''
 2 mg of protein per ml of the mpad-lysate-feed for 24 hours for up to 36h
 3 mg for 36 hours per ml of the mpad-lysate-feed 

 400 ng in 0.05mL at ratio of 3mg/mL = 0.15mg per 400 ng of plasmid
 400 micropads fit in 8uL pgel lyate ; + 35uL of lysate, and total 50uL of solution
 1ng of plasmid = 1 micropad
'''

def calculate_total_expression_solution(g_protein):
    'given grams of protein, calculate total expression solution in mL for 36 hours'
    mg_protein = cv.convert_units_grams(g_protein, 'g', 'mg')
    return mg_protein / 3

def calculate_pgel_pad_count(mL_solution):
    'given mL of solution, calculate total pgel pad count'
    return (cv.convert_units_liters(mL_solution, 'mL', 'uL') / 8) * 400

total_expression_solution = {'name': 'Total Expression Solution', 'value': calculate_total_expression_solution(target_protein['value']), 'unit': 'mL'}
total_pgel_pad_solution = {'name': 'Total Pgel Pad Solution', 'value': total_expression_solution['value'] * 0.16, 'unit': 'mL'}
total_pgel_pad_count = {'name': 'Total Pgel Pad Count', 'value': calculate_pgel_pad_count(total_pgel_pad_solution['value']), 'unit': 'micropads'}
total_gene_plasmid = {'name': 'Total Gene Plasmid', 'value': total_pgel_pad_count['value'], 'unit': 'ng'}

total_lysate = {'name': 'Total Lysate', 'value': 0.7 * total_expression_solution['value'], 'unit': 'mL'}

expression_info = [total_expression_solution, total_pgel_pad_solution, total_pgel_pad_count, total_gene_plasmid, total_lysate]
df2 = pd.DataFrame(expression_info)
df2['section'] = 'Expression'
df2['section_time'] = '36 hours'
df = pd.concat([df, df2])

## P-Gel Formation Calculations =====================
'''
- xDNA = 150 μM in 10.5 μl => ratio = 0.35
  - 41.6 µg in 10.5uL for 40bp
- T4 ligase   (1 uL of 3 U/uL activity) ratio = 0.03333333
- T4 ligase buffer (3uL) => ratio = 0.1
- water = whatever is needed to add up to total volume
total volume 30uL
'''

def calculate_xdna_per_cycle(mL_pgel_a):
    return (cv.convert_units_liters(mL_pgel_a, 'mL', 'uL') * 0.35 / 10.5 * 41.6)

def calculate_t4_ligase_per_cycle(mL_pgel_a):
    return (cv.convert_units_liters(mL_pgel_a, 'mL', 'uL') * 0.03333333 * 3)

total_xdna = {'name': 'Total xDNA', 'value': calculate_xdna_per_cycle(total_pgel_pad_solution['value']), 'unit': 'ug'}
total_t4_ligase = {'name': 'Total T4 Ligase', 'value': calculate_t4_ligase_per_cycle(total_pgel_pad_solution['value']), 'unit': 'units'}
total_t4_ligase_buffer = {'name': 'Total T4 Ligase Buffer', 'value': total_pgel_pad_solution['value'] * 0.1, 'unit': 'mL'}

xdna_formation_info = [total_xdna, total_t4_ligase, total_t4_ligase_buffer]
df3 = pd.DataFrame(xdna_formation_info)
df3['section'] = 'X-DNA Formation'
df3['section_time'] = '16 hours'
df = pd.concat([df, df3])

## Plasmid Linearization Calculations =====================
'''
5 μg of plasmid = requires 100 units in 10 μl ApaI restriction enzyme
pmol=nM * volume in µL÷1000

https://www.promega.com/resources/tools/biomath/ for pmol into ug
'''

total_apaI_units = {'name': 'Total ApaI Volume', 'value': (cv.convert_units_grams(total_gene_plasmid['value'], 'ng', 'ug') / 5) * 100, 'unit': 'units'}

df4 = pd.DataFrame([total_apaI_units])
df4['section'] = 'Plasmid Linearization'
df4['section_time'] = '16 hours'
df = pd.concat([df, df4])

### Plasmid Expression Calculations =========================
'''
3–5 µg of plasmid produce per mL of LB transformed e.coli bacteria
'''
total_ecoli_volume = {'name': 'Total E.coli Volume', 'value': cv.convert_units_grams(total_gene_plasmid['value'] / 1000, 'ng', 'ug') / 5, 'unit': 'mL'}

df5 = pd.DataFrame([total_ecoli_volume])
df5['section'] = 'Plasmid Expression'
df5['section_time'] = '24 hours'
df = pd.concat([df, df5])

### Mold Formation Calculations =========================
'''
1mx1m = 1000 = 1000000 micropads = 1 million micropads
PDMS required = 1mx1mx1cm = 1000 cm^3 = 1L
'''

total_pdms_volume = {'name': 'Total PDMS Volume', 'value': total_pgel_pad_count['value'] / 1000000, 'unit': 'L'}

df6 = pd.DataFrame([total_pdms_volume])
df6['section'] = 'Mold Formation'
df6['section_time'] = '24 hours'
df = pd.concat([df, df6])

## Export =====================
df.to_csv('data/CFPP.csv', index=False)

