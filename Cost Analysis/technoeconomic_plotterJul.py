import matplotlib.pyplot as plt
import pandas as pd

initial_investment_cost = 87350 + 20534 per cycle   # Example initial investment cost in dollars

def create_protein(time_hours: int):
    """TODO for Cost Analysis team: Change the logic here to reflect the actual protein production process."""
    return {
        'cost in $': 5001.5 * time_hours,
        'protein in g': 20 * time_hours
    }

# Generate data using formulas for a range of hours
time_values = list(range(1, 1000, 10))  # Example time inputs: 1 to 5 hours. Read documentation for range() to understand why 6th hour doesn't count.
protein_yield = []
cost = []
time = []

for t in time_values:
    result = create_protein(t)
    protein_yield.append(result['protein in g'])
    cost.append(result['cost in $'] + initial_investment_cost)
    time.append(t)

# Print out the generated data (just for Charity debugging)
print("Time (hr):", time)
print("Protein Yield (g):", protein_yield)
print("Cost ($):", cost)

# Efficiency calculations
cost_efficiency = [py / c for py, c in zip(protein_yield, cost)]
time_efficiency = [py / t for py, t in zip(protein_yield, time)]
production_efficiency = [py / (c * t) for py, c, t in zip(protein_yield, cost, time)]

# Plotting setup
fig, axs = plt.subplots(3, 1, figsize=(10, 12))

# Cost Efficiency Plot
axs[0].plot(time, cost_efficiency, marker='o', color='blue')
axs[0].set_title('Cost Efficiency')
axs[0].set_ylabel('mg per $')
axs[0].set_xticks(range(0, max(time)+1, 100))

# Time Efficiency Plot
axs[1].plot(time, time_efficiency, marker='s', color='green')
axs[1].set_title('Time Efficiency')
axs[1].set_ylabel('mg per hour')
axs[1].set_xticks(range(0, max(time)+1, 100))

# Production Efficiency Plot
axs[2].plot(time, production_efficiency, marker='^', color='red')
axs[2].set_title('Production Efficiency')
axs[2].set_ylabel('mg per ($·hour)')
axs[2].set_xlabel('Time (hours)')
axs[2].set_xticks(range(0, max(time)+1, 100))

# add spacing between subplots
plt.tight_layout(pad=2.0)
plt.show()