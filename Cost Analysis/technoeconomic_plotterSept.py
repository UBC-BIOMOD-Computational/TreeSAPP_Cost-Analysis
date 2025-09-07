import matplotlib.pyplot as plt
import pandas as pd

# Plot: Lab CFPP x Lab CBPP x Lab CFPP (with micropad recycling)
lab_cfpp = pd.read_csv(r'./data/raw/CFPP Lab.csv')
lab_cbpp = pd.read_csv(r'./data/raw/CBPP Lab.csv')
lab_cfpp_recycled = pd.read_csv(r'./data/raw/CFPP Lab (recycle mpads).csv')

# column names [time (hours),protein (mg),cost ($)]

# plot cost over time for each
plt.figure(figsize=(10, 6))
plt.plot(lab_cbpp['time (hours)'], lab_cbpp['cost ($)'], label='Lab CBPP', color='green')
plt.plot(lab_cfpp_recycled['time (hours)'], lab_cfpp_recycled['cost ($)'], label='Lab CFPP (Recycled)', color='orange')
plt.plot(lab_cfpp['time (hours)'], lab_cfpp['cost ($)'], label='Lab CFPP', color='blue')

# add legend and labels
plt.legend()
plt.xlabel('Time (hours)')
plt.ylabel('Cost ($)')
plt.title('Cost Comparison: Lab CFPP vs Lab CBPP vs Lab CFPP (Recycled)')
plt.grid(True)
plt.yscale('log')  # Use logarithmic scale for y-axis
plt.xscale('log')  # Use logarithmic scale for x-axis
plt.ylim(0.1, 10000)  # Set y-axis limits
plt.xlim(1, 1000)  # Set x-axis limits
plt.tight_layout()

plt.show()