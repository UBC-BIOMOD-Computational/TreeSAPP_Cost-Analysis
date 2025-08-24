import pandas as pd
import json

# 200g proteins produced per cycle
# it costs $87350 at hour zero, and each additional cycle costs an additional $20534
# cycle time is 40hours per cycle

def generate_technoeconomic_data(config_data):
    '''
    Generate techno-economic data for a given number of cycles.
    '''
    data = []

    for cycle in range(config_data['num_cycles'] + 1):
        time_hours = cycle * config_data['cycle_time']
        protein_mg = cycle * config_data['protein_per_cycle_mg']
        cost = config_data['initial_cost'] + cycle * config_data['cycle_cost']
        data.append({
            'time (hours)': time_hours,
            'protein (mg)': protein_mg,
            'cost ($)': cost
        })

    df = pd.DataFrame(data)
    return df

# Example usage:
if __name__ == "__main__":
    with open('cost_analysis_config.json') as f:
        config_data_all = json.load(f)

    for config_data in config_data_all.values():
        df = generate_technoeconomic_data(config_data)
        df.to_csv('data/' + config_data["name"] + '.csv', index=False)
