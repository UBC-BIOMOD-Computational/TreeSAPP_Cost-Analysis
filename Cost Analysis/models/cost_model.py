import conversion as cv
import pandas as pd
import numpy as np

final_costs_df = pd.DataFrame(columns=[
        "name",
        "num_cycles",
        "initial_cost",
        "cycle_cost_$",
        "cycle_time_hours",
        "protein_per_cycle_mg"
        ])

## =================================================================
## CELL FREE =======================================================

#  Cell Free Lab ---------------------------------------------------
cfpp_df = pd.read_csv("data/CBPP_lab_20kg_100cycles.csv")

'''
cfpp_initial_cost = mold equipment + photoresist + 24L pdms
'''
cfpp_initial_cost = 0

'''
"$/per cycle = 9448.16
= 437 + 7404 + 22 + 53.4 + 1231.76 + 300 
= 200/3 mL of lysate
+ 74.048mg of dna at $100/mg
+ 2 mL T4 Ligase for 243units/$1
+ 5.34 mL T4 Ligase buffer for $10/mL
+ 61588 units of ApaI for 50 units/$1
+ 3079.4 ug of plasmid purified (7500ug for $300)"
'''

'''
"t = 40h (pipelined into upstream + downstream) 
*not including initial mold making"
'''

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