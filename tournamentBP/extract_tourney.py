import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1) Read Sheet2 from the Excel file
#    If your file is named differently, change "tourney.xlsx" accordingly.
#    If the first row is indeed the header row, use header=0.
df = pd.read_excel("salvaaa.xlsx", sheet_name="Sheet1", header=0)

# 2) If the columns in your sheet differ from these,
#    either rename them here or update the code below accordingly.
#    For example, if your actual columns are spelled slightly differently,
#    adjust the list below to match them exactly.
expected_cols = [
    "localPredictorSize",
    "localCtrBits",
    "choicePredictorSize",
    "choiceCtrBits",
    "globalPredictorSize",
    "globalCtrBits",
    "localHistoryTableSize",
    "COMMITTED",
    "MISS",
    "MISS Rate",
    "Total Size (Bytes)"
]

# Optional: rename columns to a consistent set if needed.
# Example:
# rename_map = {
#     "PredicticalPredicotrSize": "localPredictorSize",
#     "CtrBits": "choiceCtrBits",
#     # etc...
# }
# df.rename(columns=rename_map, inplace=True)

print("Columns found in Excel:", df.columns.tolist())

# 3) Drop any completely empty rows (just in case)
df.dropna(how="all", inplace=True)

# 4) Convert the relevant columns to numeric
for col in expected_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop Columns where localPredictorSize is different than globalPredictorSize or choicePredictorSize
df = df[df["localPredictorSize"] == df["globalPredictorSize"]]
df = df[df["localPredictorSize"] == df["choicePredictorSize"]]

# 5) Remove rows that are missing essential data for plotting
df.dropna(subset=["MISS Rate", "Total Size (Bytes)"], inplace=True)

# Sort the DataFrame by Total Size for better plotting
df.sort_values("Total Size (Bytes)", inplace=True)

# 7) Plot MISS Rate vs. log2(Total Size)
plt.figure(figsize=(8, 6))
plt.plot(df["Total Size (Bytes)"], df["MISS Rate"], color='blue', marker='o')
plt.xlabel("Total Size (Bytes)")
plt.xscale('log', base=2)
plt.ylabel("MISS Rate")
plt.title("MISS Rate vs. Total Size (Bytes)")
plt.grid(True, which="both", ls="--")
plt.show()

# 8) Print a quick summary to confirm the data loaded properly
print(f"Number of rows in final DataFrame: {len(df)}")
print(df.head(10))
