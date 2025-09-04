import conversion as cv
import pandas as pd
import numpy as np

final_costs_dict = []

## =================================================================
## CELL FREE =======================================================

#  Cell Free Lab ---------------------------------------------------
cfpp_lab_df = pd.read_csv("data/CFPP_lab_20kg_100cycles.csv")
def cfpp_lab(name):
    return cfpp_lab_df.loc[cfpp_lab_df['name'] == name, 'value'].iloc[0]

'''
cfpp_initial_cost = mold equipment + photoresist + pdms for mold creation
'''
cfpp_initial_cost = 77000 + 750 + cfpp_lab('Total PDMS Volume') * 340

'''
"$/per cycle = 
=  lysate at 800CAD/1L
+ dna sequences for xdna arms at $100/mg
+ T4 Ligase for 243units/$1
+ T4 Ligase buffer for $10/mL
+ ApaI for 50 units/$1
+ plasmid purified (7500ug for $300)"
'''
cost_lysate = cfpp_lab('Total Lysate') * 800
cost_xdna = cv.convert_units_grams(cfpp_lab('Total xDNA'), 'ug', 'mg') * 100
cost_t4_ligase = cfpp_lab('Total T4 Ligase') / 243
cost_t4_buffer = cfpp_lab('Total T4 Ligase Buffer') * 10
cost_apaI = cfpp_lab('Total ApaI Volume') / 50
cost_plasmid = cv.convert_units_grams(cfpp_lab('Total Gene Plasmid'), 'ng', 'ug') / 7500 * 300
# cfpp # print('cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid')
# cfpp # print(cost_lysate, cost_xdna, cost_t4_ligase, cost_t4_buffer, cost_apaI, cost_plasmid)
cfpp_per_cycle_cost = cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid

'''
"t = 40h (pipelined into upstream + downstream) 
*not including initial mold making"
'''
cfpp_time = 40

final_costs_dict.append({
    "name": "CFPP Lab",
    "num_cycles": cfpp_lab('Total Cycles'),
    "initial_cost": cfpp_initial_cost,
    "cycle_cost_$": cfpp_per_cycle_cost,
    "cycle_time_hours": cfpp_time,
    "protein_per_cycle_mg": cfpp_lab('Target Protein Per Cycle')
})

#  Cell Free Industry ----------------------------------------------

cfpp_ind_df = pd.read_csv("data/CFPP_industry_200kg_100cycles.csv")
def cfpp_ind(name):
    return cfpp_ind_df.loc[cfpp_ind_df['name'] == name, 'value'].iloc[0]

'''
cfpp_initial_cost = mold equipment + photoresist + pdms for mold creation
'''
cfpp_initial_cost = 77000 + 750 + cfpp_ind('Total PDMS Volume') * 340

'''
"$/per cycle = 
=  lysate at 600CAD/1L
+ dna sequences for xdna arms at $100/mg
+ T4 Ligase for 243units/$1
+ T4 Ligase buffer for $10/mL
+ ApaI for 50 units/$1
+ plasmid purified (7500ug for $300)"
'''
cost_lysate = cfpp_ind('Total Lysate') * 600
cost_xdna = cv.convert_units_grams(cfpp_ind('Total xDNA'), 'ug', 'mg') * 100
cost_t4_ligase = cfpp_ind('Total T4 Ligase') / 243
cost_t4_buffer = cfpp_ind('Total T4 Ligase Buffer') * 10
cost_apaI = cfpp_ind('Total ApaI Volume') / 50
cost_plasmid = cv.convert_units_grams(cfpp_ind('Total Gene Plasmid'), 'ng', 'ug') / 7500 * 300
# cfpp # print('cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid')
# cfpp # print(cost_lysate, cost_xdna, cost_t4_ligase, cost_t4_buffer, cost_apaI, cost_plasmid)
cfpp_per_cycle_cost = cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid

'''
"t = 40h (pipelined into upstream + downstream) 
*not including initial mold making"
'''
cfpp_time = 40

final_costs_dict.append({
    "name": "CFPP Industry",
    "num_cycles": cfpp_ind('Total Cycles'),
    "initial_cost": cfpp_initial_cost,
    "cycle_cost_$": cfpp_per_cycle_cost,
    "cycle_time_hours": cfpp_time,
    "protein_per_cycle_mg": cfpp_ind('Target Protein Per Cycle')
})


#  Cell Free Prototype ---------------------------------------------
cfpp_proto_df = pd.read_csv("data/CFPP_prototype_10g_10cycles.csv")
def cfpp_proto(name):
    return cfpp_proto_df.loc[cfpp_proto_df['name'] == name, 'value'].iloc[0]

'''
cfpp_initial_cost = mold equipment + photoresist + pdms for mold creation
'''
cfpp_initial_cost = 77000 + 750 + cfpp_proto('Total PDMS Volume') * 340

'''
"$/per cycle = 
=  lysate at 800CAD/1L
+ dna sequences for xdna arms at $100/mg
+ T4 Ligase for 243units/$1
+ T4 Ligase buffer for $10/mL
+ ApaI for 50 units/$1
+ plasmid purified (7500ug for $300)"
'''
cost_lysate = cfpp_proto('Total Lysate') * 800
cost_xdna = cv.convert_units_grams(cfpp_proto('Total xDNA'), 'ug', 'mg') * 100
cost_t4_ligase = cfpp_proto('Total T4 Ligase') / 243
cost_t4_buffer = cfpp_proto('Total T4 Ligase Buffer') * 10
cost_apaI = cfpp_proto('Total ApaI Volume') / 50
cost_plasmid = cv.convert_units_grams(cfpp_proto('Total Gene Plasmid'), 'ng', 'ug') / 7500 * 300
# cfpp # print('cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid')
# cfpp # print(cost_lysate, cost_xdna, cost_t4_ligase, cost_t4_buffer, cost_apaI, cost_plasmid)
cfpp_per_cycle_cost = cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid

'''
"t = 40h (pipelined into upstream + downstream) 
*not including initial mold making"
'''
cfpp_time = 40

final_costs_dict.append({
    "name": "CFPP Prototype",
    "num_cycles": cfpp_proto('Total Cycles'),
    "initial_cost": cfpp_initial_cost,
    "cycle_cost_$": cfpp_per_cycle_cost,
    "cycle_time_hours": cfpp_time,
    "protein_per_cycle_mg": cfpp_proto('Target Protein Per Cycle')
})

#  Cell Free Prototype (Switching Proteins) ------------------------
#  same as cell-free prototype (original)
final_costs_dict.append({
    "name": "CFPP Prototype (Switching Proteins)",
    "num_cycles": cfpp_proto('Total Cycles'),
    "initial_cost": cfpp_initial_cost,
    "cycle_cost_$": cfpp_per_cycle_cost,
    "cycle_time_hours": cfpp_time,
    "protein_per_cycle_mg": cfpp_proto('Target Protein Per Cycle')
})


#  Cell Free Lab (recycle mpads) -----------------------------------

#  Cell Free Industry (recycle mpads) ------------------------------

#  Cell Free Prototype (recycle mpads) -----------------------------

#  Cell Free Prototype (recycle mpads) (Switching Proteins) --------


## =================================================================
## CELL BASED ======================================================

#  Cell Based Lab --------------------------------------------------
cbpp_lab_df = pd.read_csv("data/CBPP_lab_20kg_100cycles.csv")
def cbpp_lab(name):
    return cbpp_lab_df.loc[cbpp_lab_df['name'] == name, 'value'].iloc[0]

'''
bioreactor 2000L for $200000
high pressure homogenizer for $20000 for 100 mL/min = 6L/hour; needs to be done in 4 hours 
one-time costs = stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge "
'''
cbpp_initial_cost = 10000 + cbpp_lab('Total Cell Culture Volume')/2000 * 200000 + cv.convert_units_liters(cbpp_lab('Total Cell Culture Volume'), 'ml', 'L')/50*30000    
print("stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge")
print(10000 , cbpp_lab('Total Cell Culture Volume')/2000 * 200000 , cv.convert_units_liters(cbpp_lab('Total Cell Culture Volume'), 'ml', 'L')/50*30000)

'''
$/per cycle = 
LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG

'''

# cbpp_per_cycle_cost = LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG
cbpp_per_cycle_cost = (cbpp_lab('Total LB') 
    + cv.convert_units_grams(cbpp_lab('Total KH2PO4'), 'g', 'kg') * 259 
    + cv.convert_units_grams(cbpp_lab('Total NaCl'), 'g', 'kg') * 15 
    + cv.convert_units_grams(cbpp_lab('Total MgSO4'), 'g', 'kg') * 321 
    + cbpp_lab('Total CaCl2')/500 * 523 
    + cbpp_lab('Total NH4Cl') * 103 
    + cv.convert_units_grams(cbpp_lab('Total Glucose'), 'g', 'kg') * 54 
    + cv.convert_units_grams(cbpp_lab('Total IPTG'), 'mg', 'g') * 177.24)

print(cbpp_lab('Total LB')  
, cv.convert_units_grams(cbpp_lab('Total KH2PO4'), 'g', 'kg') * 259 
, cv.convert_units_grams(cbpp_lab('Total NaCl'), 'g', 'kg') * 15 
, cv.convert_units_grams(cbpp_lab('Total MgSO4'), 'g', 'kg') * 321 
, cbpp_lab('Total CaCl2')/500 * 523 
, cbpp_lab('Total NH4Cl') * 103 
, cv.convert_units_grams(cbpp_lab('Total Glucose'), 'g', 'kg') * 54 
, cv.convert_units_grams(cbpp_lab('Total IPTG'), 'mg', 'g') * 177.24)
cbpp_time = 46 # TODO

final_costs_dict.append({
    "name": "CFPP Lab",
    "num_cycles": cbpp_lab('Total Cycles'),
    "initial_cost": cbpp_initial_cost,
    "cycle_cost_$": cbpp_per_cycle_cost,
    "cycle_time_hours": cbpp_time,
    "protein_per_cycle_mg": cbpp_lab('Target Protein Per Cycle')
})


#  Cell Based Industry ---------------------------------------------

cbpp_ind_df = pd.read_csv("data/CBPP_industry_200kg_100cycles.csv")
def cbpp_ind(name):
    return cbpp_ind_df.loc[cbpp_ind_df['name'] == name, 'value'].iloc[0]

'''
bioreactor 2000L for $200000
high pressure homogenizer for $20000 for 100 mL/min = 6L/hour; needs to be done in 4 hours 
one-time costs = stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge "
'''
cbpp_initial_cost = 75000 + cbpp_ind('Total Cell Culture Volume')/2000 * 200000 + cv.convert_units_liters(cbpp_ind('Total Cell Culture Volume'), 'ml', 'L')/500*200000    
print("stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge")
print(75000 , cbpp_ind('Total Cell Culture Volume')/2000 * 200000 , cv.convert_units_liters(cbpp_ind('Total Cell Culture Volume'), 'ml', 'L')/500*200000)

'''
$/per cycle = 
LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG

'''
# cbpp_per_cycle_cost = LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG
cbpp_per_cycle_cost = (cbpp_ind('Total LB') 
    + cv.convert_units_grams(cbpp_ind('Total KH2PO4'), 'g', 'kg') * 259 
    + cv.convert_units_grams(cbpp_ind('Total NaCl'), 'g', 'kg') * 15 
    + cv.convert_units_grams(cbpp_ind('Total MgSO4'), 'g', 'kg') * 321 
    + cbpp_ind('Total CaCl2')/500 * 523 
    + cbpp_ind('Total NH4Cl') * 103 
    + cv.convert_units_grams(cbpp_ind('Total Glucose'), 'g', 'kg') * 54 
    + cv.convert_units_grams(cbpp_ind('Total IPTG'), 'mg', 'g') * 177.24)

print(cbpp_ind('Total LB')  
, cv.convert_units_grams(cbpp_ind('Total KH2PO4'), 'g', 'kg') * 259 
, cv.convert_units_grams(cbpp_ind('Total NaCl'), 'g', 'kg') * 15 
, cv.convert_units_grams(cbpp_ind('Total MgSO4'), 'g', 'kg') * 321 
, cbpp_ind('Total CaCl2')/500 * 523 
, cbpp_ind('Total NH4Cl') * 103 
, cv.convert_units_grams(cbpp_ind('Total Glucose'), 'g', 'kg') * 54 
, cv.convert_units_grams(cbpp_ind('Total IPTG'), 'mg', 'g') * 177.24)
cbpp_time = 46 # TODO

final_costs_dict.append({
    "name": "CFPP Industry",
    "num_cycles": cbpp_ind('Total Cycles'),
    "initial_cost": cbpp_initial_cost,
    "cycle_cost_$": cbpp_per_cycle_cost,
    "cycle_time_hours": cbpp_time,
    "protein_per_cycle_mg": cbpp_ind('Target Protein Per Cycle')
})

#  Cell Based Prototype --------------------------------------------
cbpp_proto_df = pd.read_csv("data/CBPP_prototype_10g_10cycles.csv")
def cbpp_proto(name):
    return cbpp_proto_df.loc[cbpp_proto_df['name'] == name, 'value'].iloc[0]

'''
2000 cell line development
1L bioreactor for $5000
high pressure homogenizer for $20000 for 100 mL/min = 6L/hour; needs to be done in 4 hours 
one-time costs = stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge "
'''
cbpp_initial_cost = 2000 + 5000 +  cv.convert_units_liters(cbpp_proto('Total Cell Culture Volume'), 'ml', 'L')*10000
print("stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge")
print(2000 , 5000 , cv.convert_units_liters(cbpp_proto('Total Cell Culture Volume'), 'ml', 'L')*10000)

'''
$/per cycle = 
LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG

'''
# cbpp_per_cycle_cost = LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG
cbpp_per_cycle_cost = (cbpp_proto('Total LB') 
    + cv.convert_units_grams(cbpp_proto('Total KH2PO4'), 'g', 'kg') * 259 
    + cv.convert_units_grams(cbpp_proto('Total NaCl'), 'g', 'kg') * 15 
    + cv.convert_units_grams(cbpp_proto('Total MgSO4'), 'g', 'kg') * 321 
    + cbpp_proto('Total CaCl2')/500 * 523 
    + cbpp_proto('Total NH4Cl') * 103 
    + cv.convert_units_grams(cbpp_proto('Total Glucose'), 'g', 'kg') * 54 
    + cv.convert_units_grams(cbpp_proto('Total IPTG'), 'mg', 'g') * 177.24)

print(cbpp_proto('Total LB')  
, cv.convert_units_grams(cbpp_proto('Total KH2PO4'), 'g', 'kg') * 259 
, cv.convert_units_grams(cbpp_proto('Total NaCl'), 'g', 'kg') * 15 
, cv.convert_units_grams(cbpp_proto('Total MgSO4'), 'g', 'kg') * 321 
, cbpp_proto('Total CaCl2')/500 * 523 
, cbpp_proto('Total NH4Cl') * 103 
, cv.convert_units_grams(cbpp_proto('Total Glucose'), 'g', 'kg') * 54 
, cv.convert_units_grams(cbpp_proto('Total IPTG'), 'mg', 'g') * 177.24)
cbpp_time = 46 

final_costs_dict.append({
    "name": "CFPP Prototype",
    "num_cycles": cbpp_proto('Total Cycles'),
    "initial_cost": cbpp_initial_cost,
    "cycle_cost_$": cbpp_per_cycle_cost,
    "cycle_time_hours": cbpp_time,
    "protein_per_cycle_mg": cbpp_proto('Target Protein Per Cycle')
})

#  Cell Based Prototype (Switching Proteins) -----------------------

'''
2000 cell line development
1L bioreactor for $5000
high pressure homogenizer for $20000 for 100 mL/min = 6L/hour; needs to be done in 4 hours 
one-time costs = cellular expression equipment + highPressureHomogenizer/centrifuge "
'''
cbpp_initial_cost =  5000 +  cv.convert_units_liters(cbpp_proto('Total Cell Culture Volume'), 'ml', 'L')*10000
print(" cellular expression equipment + highPressureHomogenizer/centrifuge")
print( 5000 , cv.convert_units_liters(cbpp_proto('Total Cell Culture Volume'), 'ml', 'L')*10000)

'''
$/per cycle =  stable cell line development + 
LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG

'''
# cbpp_per_cycle_cost = LB + KH2PO4 + NaCl + MgSO4 + CaCl2 + NH4Cl + Glucose + IPTG
cbpp_per_cycle_cost = (2000 
    + cbpp_proto('Total LB') 
    + cv.convert_units_grams(cbpp_proto('Total KH2PO4'), 'g', 'kg') * 259 
    + cv.convert_units_grams(cbpp_proto('Total NaCl'), 'g', 'kg') * 15 
    + cv.convert_units_grams(cbpp_proto('Total MgSO4'), 'g', 'kg') * 321 
    + cbpp_proto('Total CaCl2')/500 * 523 
    + cbpp_proto('Total NH4Cl') * 103 
    + cv.convert_units_grams(cbpp_proto('Total Glucose'), 'g', 'kg') * 54 
    + cv.convert_units_grams(cbpp_proto('Total IPTG'), 'mg', 'g') * 177.24)

print(cbpp_proto('Total LB')  
, cv.convert_units_grams(cbpp_proto('Total KH2PO4'), 'g', 'kg') * 259 
, cv.convert_units_grams(cbpp_proto('Total NaCl'), 'g', 'kg') * 15 
, cv.convert_units_grams(cbpp_proto('Total MgSO4'), 'g', 'kg') * 321 
, cbpp_proto('Total CaCl2')/500 * 523 
, cbpp_proto('Total NH4Cl') * 103 
, cv.convert_units_grams(cbpp_proto('Total Glucose'), 'g', 'kg') * 54 
, cv.convert_units_grams(cbpp_proto('Total IPTG'), 'mg', 'g') * 177.24)
cbpp_time = 46 

final_costs_dict.append({
    "name": "CFPP Prototype (Switching Proteins)",
    "num_cycles": cbpp_proto('Total Cycles'),
    "initial_cost": cbpp_initial_cost,
    "cycle_cost_$": cbpp_per_cycle_cost,
    "cycle_time_hours": cbpp_time,
    "protein_per_cycle_mg": cbpp_proto('Target Protein Per Cycle')
})


## =================================================================
## EXPORT ==========================================================

final_costs_df = pd.DataFrame(final_costs_dict)
final_costs_df.to_csv("data/final_costs.csv", index=False)