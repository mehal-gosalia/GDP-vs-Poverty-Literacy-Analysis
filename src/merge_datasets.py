import pandas as pd
from pathlib import Path

# Paths
RAW_DIR = Path("data/raw")
PROC_DIR = Path("data/processed")
PROC_DIR.mkdir(parents=True, exist_ok=True)

# Mapping of filename to new column name
FILES = {
    "gdp_per_capita.csv": "gdp_per_capita",
    "poverty_rate.csv": "poverty_rate",
    "literacy_rate.csv": "literacy_rate",
    "population.csv": "population"
}

def load_and_clean(file_name, col_name):
    """Load a World Bank CSV and reshape to long format."""
    df = pd.read_csv(RAW_DIR / file_name, skiprows=4)
    df = df.melt(
        id_vars=["Country Name", "Country Code"],
        var_name="year",
        value_name=col_name
    )
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df

if __name__ == "__main__":
    dfs = []
    for file, col in FILES.items():
        print(f"Loading {file}...")
        dfs.append(load_and_clean(file, col))
    
    # Merge all datasets
    from functools import reduce
    panel = reduce(lambda left, right: pd.merge(left, right, on=["Country Name", "Country Code", "year"], how="outer"), dfs)
    
    # Filter for years 2000–2023
    panel = panel[(panel["year"] >= 2000) & (panel["year"] <= 2023)]

    # Convert year to integer so Tableau reads it correctly
    panel["year"] = panel["year"].astype(int)

    # (Optional) Remove aggregate regions like "High income", "Arab World"
    exclude_codes = ["HIC", "LIC", "LMC", "UMC", "EAS", "EAP", "EMU", "EUU", "ARB", "WLD"]
    panel = panel[~panel["Country Code"].isin(exclude_codes)]

    # Save
    out_path = PROC_DIR / "panel.csv"
    panel.to_csv(out_path, index=False)
    print(f"✅ Saved merged dataset to {out_path}")
