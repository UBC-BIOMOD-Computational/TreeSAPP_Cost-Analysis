import matplotlib.pyplot as plt
import pandas as pd

def create_protein(time_hours: int):
    """TODO for Cost Analysis team: Change the logic here to reflect the actual protein production process."""
    return {
        'cost in $': 232 * time_hours,
        'protein in g': 12 * time_hours
    }

# Generate data using formulas for a range of hours
time_values = list(range(1, 6))  # Example time inputs: 1 to 5 hours. Read documentation for range() to understand why 6th hour doesn't count.
protein_yield = []
cost = []
time = []

for t in time_values:
    result = create_protein(t)
    protein_yield.append(result['protein in g'])
    cost.append(result['cost in $'])
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
x = range(len(protein_yield))  # x-axis labels as sample indices

# Cost Efficiency Plot
axs[0].plot(x, cost_efficiency, marker='o', color='blue')
axs[0].set_title('Cost Efficiency')
axs[0].set_ylabel('g per $')
axs[0].set_xticks(x)

# Time Efficiency Plot
axs[1].plot(x, time_efficiency, marker='s', color='green')
axs[1].set_title('Time Efficiency')
axs[1].set_ylabel('g per hour')
axs[1].set_xticks(x)

# Production Efficiency Plot
axs[2].plot(x, production_efficiency, marker='^', color='red')
axs[2].set_title('Production Efficiency')
axs[2].set_ylabel('g per ($·hour)')
axs[2].set_xlabel('Sample Index')
axs[2].set_xticks(x)

# add spacing between subplots
plt.tight_layout(pad=2.0)
plt.show()