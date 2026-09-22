import pandas as pd
import math
from app.services.ingestion import _safe_float

df = pd.read_excel('test_dataset.xlsx', sheet_name='Orders')

for idx, row in df.iterrows():
    sp = _safe_float(row.get("selling_price"))
    qty = int(row.get("quantity")) if not pd.isna(row.get("quantity")) else 1
    dsc = _safe_float(row.get("discount"))
    tax = _safe_float(row.get("tax"))
    shp = _safe_float(row.get("shipping_fee"))
    
    net = (sp * qty) - dsc + tax + shp
    if net > 9999999999.99 or net < -9999999999.99:
        print(f"Row {idx} overflows: net={net}")
        
print("Check done for computed net_revenue")

