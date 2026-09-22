import pandas as pd

# Inspect test data
xl = pd.ExcelFile(r'c:\projects\commercepulse\AZURE\backend\test_dataset.xlsx', engine='openpyxl')
print("Sheets:", xl.sheet_names)

for s in xl.sheet_names:
    df = xl.parse(s)
    print(f"\n--- {s} ---")
    print(f"Columns: {list(df.columns)}")
    print(f"Rows: {len(df)}")
    if len(df) > 0:
        print("First row:")
        for k, v in dict(df.iloc[0]).items():
            print(f"  {k}: {v}")
    print()

# Also check the main test data
try:
    xl2 = pd.ExcelFile(r'c:\projects\commercepulse\AZURE\commercepulse_testdata.xlsx', engine='openpyxl')
    print("\n=== MAIN TEST DATA ===")
    print("Sheets:", xl2.sheet_names)
    for s in xl2.sheet_names:
        df = xl2.parse(s)
        print(f"\n--- {s} ---")
        print(f"Columns: {list(df.columns)}")
        print(f"Rows: {len(df)}")
        if len(df) > 0:
            print("First row:")
            for k, v in dict(df.iloc[0]).items():
                print(f"  {k}: {v}")
except Exception as e:
    print(f"Could not read main test data: {e}")
