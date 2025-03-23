import re
import matplotlib.pyplot as plt

# Hardcoded log file name (change this to your actual log file name)
LOGFILE = "log_BTB_entries.txt"

def parse_log_file(filename):
    """
    Parses the log file to extract numEntries and BTBHitRatio values.
    It computes the total BTB size as numEntries * 16.
    """
    total_sizes = []
    hit_ratios = []
    current_num_entries = None

    with open(filename, 'r') as f:
        for line in f:
            # Look for the numEntries in the "RUNNING" line
            num_match = re.search(r'RUNNING.*numEntries\s*=\s*(\d+)', line)
            if num_match:
                current_num_entries = int(num_match.group(1))
            
            # Look for the BTB hit ratio line
            hit_match = re.search(r'system\.cpu\.branchPred\.BTBHitRatio\s+([\d\.]+)', line)
            if hit_match and current_num_entries is not None:
                hit_ratio = float(hit_match.group(1))
                total_size = current_num_entries * 16
                total_sizes.append(total_size)
                hit_ratios.append(hit_ratio)
                # Reset for the next section
                current_num_entries = None

    return total_sizes, hit_ratios

def plot_btb(total_sizes, hit_ratios):
    """
    Creates a scatter plot of BTB hit ratio vs. total BTB size.
    The x-axis is logarithmic with base 2.
    """
    # Convert Hit Ratios to percentages
    hit_ratios = [ratio * 100 for ratio in hit_ratios]

    plt.figure()
    plt.plot(total_sizes, hit_ratios, marker='o')
    plt.xlabel('Total BTB Size (Bytes)')
    plt.ylabel('BTB Hit Ratio (%)')
    plt.title('BTB Hit Ratio vs. Total BTB Size')
    plt.xscale('log', base=2)
    plt.grid(True, which="both", linestyle="--")
    plt.show()

if __name__ == '__main__':
    total_sizes, hit_ratios = parse_log_file(LOGFILE)
    if not total_sizes:
        print("No valid data found in the log file.")
    else:
        print(f"Extracted {len(total_sizes)} data points.")
        plot_btb(total_sizes, hit_ratios)
