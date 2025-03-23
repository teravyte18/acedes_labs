import re
import matplotlib.pyplot as plt

# Hardcoded log file name (change this if needed)
LOGFILE = "log_BTB_full.txt"

def parse_log_file(filename):
    """
    Parses the log file and extracts associativity, numEntries, and BTBHitRatio.
    It searches for lines like:
      RUNNING associativity=VALUE AND numEntries=VALUE
    and then captures the corresponding BTBHitRatio (hit rate) value.
    
    The data is grouped by numEntries (which determines the Total BTB Size as numEntries × 16).
    Returns a dictionary where each key is numEntries and each value is a list of (associativity, hit_rate) tuples.
    """
    data = {}  # key: numEntries, value: list of (associativity, hit_rate)
    current_assoc = None
    current_entries = None

    with open(filename, "r") as f:
        for line in f:
            # Look for the RUNNING line that contains associativity and numEntries
            run_match = re.search(r'RUNNING\s+associativity\s*=\s*(\d+)\s+AND\s+numEntries\s*=\s*(\d+)', line)
            if run_match:
                current_assoc = int(run_match.group(1))
                current_entries = int(run_match.group(2))
                continue

            # Look for the BTB hit ratio (hit rate) line
            hit_match = re.search(r'system\.cpu\.branchPred\.BTBHitRatio\s+([\d\.]+)', line)
            if hit_match and current_assoc is not None and current_entries is not None:
                hit_rate = float(hit_match.group(1))
                if current_entries not in data:
                    data[current_entries] = []
                data[current_entries].append((current_assoc, hit_rate))
                # Reset for the next simulation section
                current_assoc = None
                current_entries = None
    return data

def plot_hit_rate(data):
    """
    Plots the hit rate (BTBHitRatio) versus associativity.
    Each line represents a different total BTB size (Total Size = numEntries × 16).
    The x-axis (associativity) is displayed on a logarithmic scale with base 2.
    """
    # Convert Hit Ratios to percentages
    for num_entries, pairs in data.items():
        data[num_entries] = [(assoc, hit_rate * 100) for assoc, hit_rate in pairs]

    # Drop Values for Total Size > 64KB
    data = {k: v for k, v in data.items() if k * 16 <= 64 * 1024}  # 64KB is the maximum size in the log file


    plt.figure()
    for num_entries, pairs in data.items():
        # Sort data points by associativity
        pairs.sort(key=lambda x: x[0])
        associativities = [p[0] for p in pairs]
        hit_rates = [p[1] for p in pairs]
        total_size = num_entries   # Total BTB size in bytes
        plt.plot(associativities, hit_rates, marker='o', label=f"Total Size = {total_size} KB")

    plt.xlabel("Associativity")
    plt.ylabel("Hit Rate")
    plt.title("Hit Rate vs. Associativity for Different Total BTB Sizes")
    plt.xscale("log", base=2)
    plt.grid(True, which="both", linestyle="--")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    data = parse_log_file(LOGFILE)
    if not data:
        print("No valid data found in the log file.")
    else:
        plot_hit_rate(data)
