import re
import pandas as pd
import matplotlib.pyplot as plt

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
log_file_path = "log_local_bfs.txt"  # Update this with your actual file path
df = extract_branch_pred_stats(log_file_path)

# Save the DataFrame to an Excel file
output_excel = "branch_pred_stats.xlsx"
df.to_excel(output_excel, index=False)
print(f"Data stored in {output_excel}")

# Compute Miss Rate in percent: (Mispredicted / Committed)*100
df['Miss Rate (%)'] = df['Mispredicted Branches'] / df['Committed Branches'] * 100

# Plot Miss Rate by Local Predictor Size for each Counter configuration
plt.figure(figsize=(10, 6))

# Group by Counter and plot each series
for counter, group in df.groupby("Counter"):
    group = group.sort_values("Local Predictor Size")
    plt.plot(group["Local Predictor Size"], group["Miss Rate (%)"], marker='o', label=f"Counter = {counter}")

plt.xlabel("Local Predictor Size")
plt.ylabel("Miss Rate (%)")
plt.title("Miss Rate by Local Predictor Size and Counter")
plt.xscale('log')  # Using log scale because sizes vary significantly
plt.legend()
plt.grid(True)
plt.show()
