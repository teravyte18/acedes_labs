import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def extract_branch_pred_stats(log_file):
    data = []
    with open(log_file, 'r') as file:
        lines = file.readlines()
    
    predictor_size, counter = None, None
    for line in lines:
        # Detect predictor size and counter
        match = re.search(r'RUNNING LOCAL PREDICTOR WITH SIZE=(\d+) AND COUNTER=(\d+)', line)
        if match:
            predictor_size = int(match.group(1))
            counter = int(match.group(2))
        
        # Extract committed branches
        match_committed = re.search(r'system\.cpu\.branchPred\.committed_0::DirectCond\s+(\d+)', line)
        if match_committed and predictor_size is not None and counter is not None:
            committed = int(match_committed.group(1))
        
        # Extract mispredicted branches
        match_mispred = re.search(r'system\.cpu\.branchPred\.mispredicted_0::DirectCond\s+(\d+)', line)
        if match_mispred and predictor_size is not None and counter is not None:
            mispredicted = int(match_mispred.group(1))
            data.append((predictor_size, counter, committed, mispredicted))
            # Reset predictor size and counter for next block
            predictor_size, counter = None, None

    df = pd.DataFrame(data, columns=["Local Predictor Size", "Counter", "Committed Branches", "Mispredicted Branches"])
    return df

# Define your log file path
log_file_path = "log_local_bfs.txt"  # Update with your actual log file path
df = extract_branch_pred_stats(log_file_path)

# Save the DataFrame to an Excel file
output_excel = "branch_pred_stats.xlsx"
df.to_excel(output_excel, index=False)
print(f"Data stored in {output_excel}")

# Compute Miss Rate (%) = (Mispredicted Branches / Committed Branches) * 100
df['Miss Rate (%)'] = df['Mispredicted Branches'] / df['Committed Branches'] * 100

# --- Graph 1: Miss Rate vs Local Predictor Size ---
plt.figure(figsize=(10, 6))
for counter, group in df.groupby("Counter"):
    group = group.sort_values("Local Predictor Size")
    plt.plot(group["Local Predictor Size"], group["Miss Rate (%)"],
             marker='o', label=f"Control Bits = {counter}")

plt.xlabel("Local Predictor Size (Bits)")
plt.ylabel("Miss Rate (%)")
plt.title("Miss Rate by Local Predictor Size and Control Bits")
plt.xscale('log', base=2)  # Log scale with base 2
# Set x ticks to be the predictor sizes (which are powers of 2)
sizes = sorted(df["Local Predictor Size"].unique())
plt.xticks(sizes, sizes)
plt.legend()
plt.grid(True, which="both", ls="--")
plt.show()

# --- Graph 2: Miss Rate vs Total Size in Bytes ---
# Compute total size in Bytes as (Local Predictor Size * Counter) / 8
df['Total Size (Bytes)'] = (df['Local Predictor Size'] * df['Counter']) / 8

plt.figure(figsize=(10, 6))
for counter, group in df.groupby("Counter"):
    group = group.sort_values("Total Size (Bytes)")
    plt.plot(group["Total Size (Bytes)"], group["Miss Rate (%)"],
             marker='o', label=f"Control Bits = {counter}")

plt.xlabel("Total Size (Bytes)")
plt.ylabel("Miss Rate (%)")
plt.title("Miss Rate by Total Predictor Storage Size and Control Bits")
plt.xscale('log', base=2)
# Set x ticks as powers of 2 within the range of total sizes
min_total = df['Total Size (Bytes)'].min()
max_total = df['Total Size (Bytes)'].max()
ticks = []
current = 2**int(np.floor(np.log2(min_total)))
while current <= max_total:
    ticks.append(current)
    current *= 2
plt.xticks(ticks, ticks)
plt.legend()
plt.grid(True, which="both", ls="--")
plt.show()
