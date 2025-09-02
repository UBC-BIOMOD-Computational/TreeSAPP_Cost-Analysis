import conversion as cv
import pandas as pd
import numpy as np

final_costs_dict = []

## =================================================================
## CELL FREE =======================================================

#  Cell Free Lab ---------------------------------------------------
cfpp_df = pd.read_csv("data/CFPP_lab_20kg_100cycles.csv")
def cfpp_lab(name):
    return cfpp_df.loc[cfpp_df['name'] == name, 'value'].iloc[0]

'''
cfpp_initial_cost = mold equipment + photoresist + pdms for mold creation
'''
cfpp_initial_cost = 77000 + 750 + cfpp_lab('Total PDMS Volume') * 340

'''
"$/per cycle = 
=  lysate at 602CAD/0.5L
+ dna sequences for xdna arms at $100/mg
+ T4 Ligase for 243units/$1
+ T4 Ligase buffer for $10/mL
+ ApaI for 50 units/$1
+ plasmid purified (7500ug for $300)"
'''
cost_lysate = cfpp_lab('Total Lysate') * 2 * 602
cost_xdna = cv.convert_units_grams(cfpp_lab('Total xDNA'), 'ug', 'mg') * 100
cost_t4_ligase = cfpp_lab('Total T4 Ligase') / 243
cost_t4_buffer = cfpp_lab('Total T4 Ligase Buffer') * 10
cost_apaI = cfpp_lab('Total ApaI Volume') / 50
cost_plasmid = cv.convert_units_grams(cfpp_lab('Total Gene Plasmid'), 'ng', 'ug') / 7500 * 300
print('cost_lysate + cost_xdna + cost_t4_ligase + cost_t4_buffer + cost_apaI + cost_plasmid')
print(cost_lysate, cost_xdna, cost_t4_ligase, cost_t4_buffer, cost_apaI, cost_plasmid)
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
    "protein_per_cycle_mg": 200 / 3
})

#  Cell Free Industry ----------------------------------------------

#  Cell Free Prototype ---------------------------------------------

#  Cell Free Lab (recycle mpads) -----------------------------------

#  Cell Free Industry (recycle mpads) ------------------------------

#  Cell Free Prototype (recycle mpads) -----------------------------

#  Cell Free Prototype (Switching Proteins) ------------------------

#  Cell Free Prototype (recycle mpads) (Switching Proteins) --------

## =================================================================
## CELL BASED ======================================================

#  Cell Based Lab --------------------------------------------------
'''
"$  =  60000
= 10000 +  30000 + 20000
= stable cell line development + cellular expression equipment + highPressureHomogenizer/centrifuge "
'''
cbpp_initial_cost = 0

'''
"$/per cycle = 1277.91854336
= 12  + 0.259*40.83 + 0.015*7.0128 + 0.321*7.266352 + 12*103 + 0.054*120 + 0.08862 * 117.647059 
LB 12L +  KH₂PO₄ 40.83 g 
NaCl 7.0128g + MgSO4 7.22166g + CaCl2  0.266352g +  12g NH4Cl
Glucose 120g + 117.647059 mg of IPTG "
'''

#  Cell Based Industry ---------------------------------------------

#  Cell Based Prototype --------------------------------------------

#  Cell Based Prototype (Switching Proteins) -----------------------


## =================================================================
## EXPORT ==========================================================

final_costs_df = pd.DataFrame(final_costs_dict)
final_costs_df.to_csv("data/final_costs.csv", index=False)