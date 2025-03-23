import re
import matplotlib.pyplot as plt

# Hardcoded log file name (update if needed)
LOGFILE = "log_RAS.txt"

def parse_log_file(filename):
    """
    Parses the log file and extracts for each simulation run:
      - numEntries (from "RUNNING numEntries=...")
      - system.cpu.branchPred.ras.correct
      - system.cpu.branchPred.ras.used

    It computes:
      - RAS Hit Rate = correct / used
      - Total Size = numEntries * 8 (Bytes)
    
    Returns two lists: total_sizes and hit_rates.
    """
    total_sizes = []
    hit_rates = []
    
    # Regular expressions for the values
    re_run = re.compile(r'RUNNING\s+numEntries\s*=\s*(\d+)', re.IGNORECASE)
    re_correct = re.compile(r'system\.cpu\.branchPred\.ras\.correct\s+(\d+)', re.IGNORECASE)
    re_used = re.compile(r'system\.cpu\.branchPred\.ras\.used\s+(\d+)', re.IGNORECASE)
    
    current_numEntries = None
    current_correct = None
    current_used = None

    with open(filename, "r") as f:
        for line in f:
            # Look for the simulation run line (numEntries)
            run_match = re_run.search(line)
            if run_match:
                # Start of a new simulation block; store numEntries.
                current_numEntries = int(run_match.group(1))
                # Reset previous values
                current_correct = None
                current_used = None
            
            # Look for the ras.correct value
            correct_match = re_correct.search(line)
            if correct_match:
                current_correct = int(correct_match.group(1))
            
            # Look for the ras.used value
            used_match = re_used.search(line)
            if used_match:
                current_used = int(used_match.group(1))
            
            # Once we have both values and a valid numEntries, compute and store the data.
            if (current_numEntries is not None and 
                current_correct is not None and 
                current_used is not None and current_used != 0):
                
                hit_rate = current_correct / current_used
                total_size = current_numEntries * 8  # in Bytes
                
                total_sizes.append(total_size)
                hit_rates.append(hit_rate)
                
                # Reset the current values for the next simulation run.
                current_numEntries = None
                current_correct = None
                current_used = None

    return total_sizes, hit_rates

def plot_hit_rate_vs_total_size(total_sizes, hit_rates):
    """
    Plots RAS hit rate versus Total Size.
    """
    # Optionally sort the data by Total Size if not already sorted.
    combined = sorted(zip(total_sizes, hit_rates), key=lambda x: x[0])
    sorted_sizes, sorted_hit_rates = zip(*combined)
    
    plt.figure()
    plt.plot(sorted_sizes, sorted_hit_rates, marker='o', linestyle='-')
    plt.xlabel("Total Size (Bytes)")
    plt.ylabel("RAS Hit Rate")
    plt.xscale("log", base=2)
    plt.title("RAS Hit Rate vs Total Size")
    plt.grid(True, which="both", linestyle="--")
    plt.show()

if __name__ == '__main__':
    sizes, rates = parse_log_file(LOGFILE)
    if not sizes:
        print("No valid data found in the log file.")
    else:
        print(f"Extracted {len(sizes)} data points.")
        plot_hit_rate_vs_total_size(sizes, rates)
