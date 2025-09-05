import pandas as pd
import json

def generate_technoeconomic_data(formula_data):
    '''
    Generate techno-economic data for a given number of cycles.
    '''
    data = []

    for cycle in range(int(formula_data['num_cycles']) + 1):
        time_hours = cycle * formula_data['cycle_time_hours']
        protein_mg = cycle * formula_data['protein_per_cycle_mg']
        cost = formula_data['initial_cost'] + cycle * formula_data['cycle_cost_$']
        data.append({
            'time (hours)': time_hours,
            'protein (mg)': protein_mg,
            'cost ($)': cost
        })

    df = pd.DataFrame(data)
    return df

# Example usage:
if __name__ == "__main__":
    cost_time_formula_df = pd.read_csv('data/final_costs.csv')

    for index, row in cost_time_formula_df.iterrows():
        df = generate_technoeconomic_data(row)
        df.to_csv(r'data/raw/' + row["name"] + '.csv', index=False)
