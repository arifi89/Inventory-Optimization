import pandas as pd
from pathlib import Path

# Load the master dataset
master = pd.read_parquet(Path('data/data_model/master_dataset.parquet'))

print('\n' + '='*100)
print('MASTER DATASET - DETAILED PREVIEW')
print('='*100)
print()

print('DATASET OVERVIEW:')
print('-'*100)
print(f'  Total Records: {len(master):,}')
print(f'  Total Columns: {len(master.columns)}')
print(f'  Memory Usage: {master.memory_usage(deep=True).sum() / 1024**2:.2f} MB')
print(f'  Date Range: {master["Sales_Date"].min().date()} to {master["Sales_Date"].max().date()}')
print()

print('COLUMN LIST (41 columns):')
print('-'*100)
for i, col in enumerate(master.columns, 1):
    dtype = master[col].dtype
    null_pct = (master[col].isna().sum() / len(master)) * 100
    print(f'  {i:2d}. {col:.<40} {str(dtype):.<15} {null_pct:>6.2f}% null')
print()

print('='*100)
print('KEY STATISTICS:')
print('='*100)
print(f'  Unique Products: {master["product_key"].nunique():,}')
print(f'  Unique Stores: {master["store_key"].nunique()}')
print(f'  Unique Vendors: {master["vendor_key"].nunique()}')
print(f'  Unique Sales Orders: {master["Sales_Order"].nunique():,}')
print()

print(f'  Total Sales Amount: ${master["Sales_Amount"].sum():,.2f}')
print(f'  Total Purchase Cost: ${master["Purchase_Cost"].sum():,.2f}')
print(f'  Total Gross Profit: ${master["Gross_Profit"].sum():,.2f}')
print(f'  Average Margin: {master["Margin_Percent"].mean():.2f}%')
print()

print(f'  Records with Purchase Data: {master["Purchase_Quantity"].notna().sum():,} ({master["Purchase_Quantity"].notna().sum() / len(master) * 100:.1f}%)')
print(f'  Records with Inventory Data: {master["On_Hand_Quantity"].notna().sum():,} ({master["On_Hand_Quantity"].notna().sum() / len(master) * 100:.1f}%)')
print()

print('='*100)
print('TOP 10 PRODUCTS BY SALES:')
print('='*100)
top_products = master.groupby(['product_key', 'Product_Name']).agg({
    'Sales_Amount': 'sum',
    'Sales_Quantity': 'sum'
}).sort_values('Sales_Amount', ascending=False).head(10)
print(top_products.to_string())
print()

print('='*100)
print('SAMPLE RECORDS (Top 5 high-value sales):')
print('='*100)
sample = master.nlargest(5, 'Sales_Amount')[['Sales_Order', 'Product_Name', 'Store_City', 'Sales_Date', 'Sales_Quantity', 'Sales_Amount', 'Gross_Profit', 'Margin_Percent']]
print(sample.to_string(index=False))
print()

print('='*100)
