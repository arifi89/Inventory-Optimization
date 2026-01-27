"""
Create Master Dataset - Single Source of Truth
Combines all fact and dimension tables into one comprehensive dataset for analysis

NEW STRUCTURE:
- Fact tables now use Product_Number (Brand ID) instead of product_key
- Fact tables contain attributes directly (Description, Size, Unit_Price)
- Sales dates used directly (Sales_Date) instead of date_key conversion
- Simplified joins as data is already denormalized
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def create_master_dataset():
    """Build master dataset from all fact and dimension tables"""
    
    DATA_MODEL_DIR = Path('data/data_model')
    OUTPUT_FILE = DATA_MODEL_DIR / 'master_dataset.parquet'
    
    print('\n' + '='*100)
    print('BUILDING MASTER DATASET - SINGLE SOURCE OF TRUTH')
    print('='*100)
    print()
    
    # ============================================================================
    # STEP 1: Load all tables
    # ============================================================================
    print('Step 1: Loading all tables...')
    print('-'*100)
    
    fact_sales = pd.read_csv(DATA_MODEL_DIR / 'fact_sales.csv')
    fact_purchases = pd.read_csv(DATA_MODEL_DIR / 'fact_purchases.csv')
    fact_inventory = pd.read_csv(DATA_MODEL_DIR / 'fact_inventory_snapshot.csv')
    dim_product = pd.read_csv(DATA_MODEL_DIR / 'dim_product.csv')
    dim_store = pd.read_csv(DATA_MODEL_DIR / 'dim_store.csv')
    dim_vendor = pd.read_csv(DATA_MODEL_DIR / 'dim_vendor.csv')
    dim_date = pd.read_csv(DATA_MODEL_DIR / 'dim_date.csv')
    
    print(f'  ✓ fact_sales: {len(fact_sales):,} rows')
    print(f'  ✓ fact_purchases: {len(fact_purchases):,} rows')
    print(f'  ✓ fact_inventory: {len(fact_inventory):,} rows')
    print(f'  ✓ dim_product: {len(dim_product):,} rows')
    print(f'  ✓ dim_store: {len(dim_store):,} rows')
    print(f'  ✓ dim_vendor: {len(dim_vendor):,} rows')
    print(f'  ✓ dim_date: {len(dim_date):,} rows')
    print()
    
    # ============================================================================
    # STEP 2: Prepare data for joins
    # ============================================================================
    print('Step 2: Preparing data for joins...')
    print('-'*100)
    
    # Convert date columns to datetime
    fact_sales['Sales_Date'] = pd.to_datetime(fact_sales['Sales_Date'])
    fact_purchases['Po_Date'] = pd.to_datetime(fact_purchases['Po_Date'])
    fact_purchases['Invoice_Date'] = pd.to_datetime(fact_purchases['Invoice_Date'])
    fact_inventory['Snapshot_Date'] = pd.to_datetime(fact_inventory['Snapshot_Date'])
    
    # Standardize key types - use Product_Number (Brand ID) instead of product_key
    fact_sales['Product_Number'] = fact_sales['Product_Number'].astype(int)
    fact_sales['Store'] = fact_sales['Store'].astype(int)
    
    fact_purchases['Product_Number'] = fact_purchases['Product_Number'].astype(int)
    fact_purchases['Vendor_Number'] = fact_purchases['Vendor_Number'].astype(int)
    
    fact_inventory['Product_Number'] = fact_inventory['Product_Number'].astype(int)
    fact_inventory['Store'] = fact_inventory['Store'].astype(int)
    
    dim_product['Product_Number'] = dim_product['Product_Number'].astype(int)
    
    print('  ✓ Date columns converted to datetime')
    print('  ✓ Key columns standardized to integers')
    print()
    
    # ============================================================================
    # STEP 3: Start with fact_sales as base
    # ============================================================================
    print('Step 3: Building master dataset with fact_sales as base...')
    print('-'*100)
    
    master = fact_sales.copy()
    
    # Rename columns for clarity (Sales_Date and Product_Number already present)
    master = master.rename(columns={
        'Quantity_Sold': 'Sales_Quantity',
        'Unit_Price': 'Sales_Price',
        'Sales_Amount': 'Gross_Revenue',
        'Store': 'Store_Key'
    })
    
    print(f'  Base dataset: {len(master):,} rows with {len(master.columns)} columns')
    print()
    
    # ============================================================================
    # STEP 4: Join dimension tables for enrichment
    # ============================================================================
    print('Step 4: Joining dimension tables...')
    print('-'*100)
    
    # Join dim_store for store details
    master = master.merge(
        dim_store[['store_key', 'city', 'state', 'region']],
        left_on='Store_Key',
        right_on='store_key',
        how='left'
    )
    master = master.drop(columns=['store_key'], errors='ignore')
    
    # Rename store columns - only rename if they exist
    rename_dict = {}
    if 'city' in master.columns:
        rename_dict['city'] = 'Store_City'
    if 'state' in master.columns:
        rename_dict['state'] = 'Store_State'
    if 'region' in master.columns:
        rename_dict['region'] = 'Store_Region'
    
    if rename_dict:
        master = master.rename(columns=rename_dict)
        print(f'  ✓ Joined dim_store: {master["Store_City"].notna().sum():,} matches')
    else:
        print(f'  ⚠️ Store columns not found in merge result: {master.columns.tolist()}')
    
    # Join dim_date for date attributes
    dim_date_enhanced = dim_date.copy()
    dim_date_enhanced['full_date_dt'] = pd.to_datetime(dim_date_enhanced['full_date'])
    
    master = master.merge(
        dim_date_enhanced[['full_date_dt', 'year', 'quarter', 'month', 'month_name', 'week', 'day_of_week', 'day_name']],
        left_on='Sales_Date',
        right_on='full_date_dt',
        how='left'
    )
    master = master.drop(columns=['full_date_dt'], errors='ignore')
    master = master.rename(columns={
        'year': 'Year',
        'quarter': 'Quarter',
        'month': 'Month',
        'month_name': 'Month_Name',
        'week': 'Week',
        'day_of_week': 'Day_of_Week',
        'day_name': 'Day_Name'
    })
    print(f'  ✓ Joined dim_date: {master["Year"].notna().sum():,} matches')
    print()
    
    # ============================================================================
    # STEP 5: Join fact_purchases (aggregated by product-date)
    # ============================================================================
    print('Step 5: Joining fact_purchases...')
    print('-'*100)
    
    # Aggregate purchases by product and date for joining
    # Note: Purchases don't have store, so we group by product and date only
    purchases_agg = fact_purchases.groupby(['Product_Number', 'Po_Date']).agg({
        'Quantity_Purchased': 'sum',
        'Unit_Cost': 'mean',
        'Purchase_Amount': 'sum',
        'Freight_Cost': 'sum',
        'Vendor_Number': 'first',
        'Vendor_Name': 'first',
        'Po_Number': lambda x: ', '.join(x.astype(str).unique()[:5]),  # First 5 POs
    }).reset_index()
    
    purchases_agg = purchases_agg.rename(columns={
        'Po_Date': 'Purchase_Date',
        'Quantity_Purchased': 'Purchase_Quantity',
        'Unit_Cost': 'Purchase_Unit_Cost',
        'Purchase_Amount': 'Total_Purchase_Amount',
        'Freight_Cost': 'Total_Freight_Cost',
        'Po_Number': 'Purchase_Orders',
        'Vendor_Number': 'Vendor_Key',
        'Vendor_Name': 'Vendor_Name_from_Purchases'
    })
    
    # Join purchases by product and date (exact match on date)
    master = master.merge(
        purchases_agg,
        left_on=['Product_Number', 'Sales_Date'],
        right_on=['Product_Number', 'Purchase_Date'],
        how='left'
    )
    master = master.drop(columns=['Purchase_Date'], errors='ignore')
    master = master.drop(columns=['Vendor_Name_from_Purchases'], errors='ignore')
    
    print(f'  ✓ Joined fact_purchases: {master["Purchase_Quantity"].notna().sum():,} matches ({master["Purchase_Quantity"].notna().sum() / len(master) * 100:.1f}%)')
    
    # Join dim_vendor for vendor details
    master = master.merge(
        dim_vendor[['vendor_key', 'vendor_name', 'lead_time_days']],
        left_on='Vendor_Key',
        right_on='vendor_key',
        how='left'
    )
    master = master.drop(columns=['vendor_key'], errors='ignore')
    master = master.rename(columns={
        'vendor_name': 'Vendor_Name',
        'lead_time_days': 'Vendor_Lead_Time'
    })
    print(f'  ✓ Joined dim_vendor: {master["Vendor_Name"].notna().sum():,} matches')
    print()
    
    # ============================================================================
    # STEP 6: Join fact_inventory_snapshot
    # ============================================================================
    print('Step 6: Joining fact_inventory_snapshot...')
    print('-'*100)
    
    # Aggregate inventory by product-store-date
    inventory_agg = fact_inventory.groupby(['Product_Number', 'Store', 'Snapshot_Date']).agg({
        'On_Hand_Quantity': 'sum',
        'Inventory_Value': 'sum',
        'Snapshot_Type': 'first'
    }).reset_index()
    
    # Join inventory by product, store, and date
    master = master.merge(
        inventory_agg,
        left_on=['Product_Number', 'Store_Key', 'Sales_Date'],
        right_on=['Product_Number', 'Store', 'Snapshot_Date'],
        how='left'
    )
    master = master.drop(columns=['Store'], errors='ignore')
    master = master.drop(columns=['Snapshot_Date'], errors='ignore')
    
    print(f'  ✓ Joined fact_inventory: {master["On_Hand_Quantity"].notna().sum():,} matches ({master["On_Hand_Quantity"].notna().sum() / len(master) * 100:.1f}%)')
    print()
    
    # ============================================================================
    # STEP 7: Add KPI Calculation Columns
    # ============================================================================
    print('Step 7: Adding KPI columns...')
    print('-'*100)
    
    # Revenue metrics
    # Tax is already in master from fact_sales
    if 'Tax' not in master.columns:
        master['Tax'] = 0
    else:
        master['Tax'] = pd.to_numeric(master['Tax'], errors='coerce').fillna(0)
    
    master['Net_Revenue'] = master['Gross_Revenue'] - master['Tax']
    
    # Cost metrics
    master['Purchase_Quantity'] = pd.to_numeric(master['Purchase_Quantity'], errors='coerce').fillna(0)
    master['Purchase_Unit_Cost'] = pd.to_numeric(master['Purchase_Unit_Cost'], errors='coerce').fillna(0)
    master['Purchase_Cost'] = master['Purchase_Quantity'] * master['Purchase_Unit_Cost']
    master['Purchase_Cost'] = master['Purchase_Cost'].fillna(0)
    
    # Freight and landed cost
    master['Total_Freight_Cost'] = pd.to_numeric(master['Total_Freight_Cost'], errors='coerce').fillna(0)
    master['Landed_Cost'] = master['Purchase_Cost'] + master['Total_Freight_Cost']
    
    # Profit metrics
    master['Gross_Profit'] = master['Net_Revenue'] - master['Landed_Cost']
    master['Margin_Percent'] = np.where(
        master['Net_Revenue'] > 0,
        (master['Gross_Profit'] / master['Net_Revenue']) * 100,
        0
    )
    
    # Inventory metrics (placeholders for time-series calculations)
    master['Inventory_Turnover'] = np.nan
    master['Days_of_Inventory'] = np.nan
    
    print('  ✓ Gross_Revenue')
    print('  ✓ Tax')
    print('  ✓ Net_Revenue (Gross_Revenue - Tax)')
    print('  ✓ Purchase_Cost')
    print('  ✓ Total_Freight_Cost')
    print('  ✓ Landed_Cost (Purchase_Cost + Freight_Cost)')
    print('  ✓ Gross_Profit (Net_Revenue - Landed_Cost)')
    print('  ✓ Margin_Percent')
    print('  ✓ Inventory_Turnover (placeholder)')
    print('  ✓ Days_of_Inventory (placeholder)')
    print()
    
    # ============================================================================
    # STEP 8: Validate the dataset
    # ============================================================================
    print('Step 8: Validating master dataset...')
    print('-'*100)
    
    validation_summary = {
        'Total Rows': len(master),
        'Missing Product Numbers': master['Product_Number'].isna().sum(),
        'Missing Store Keys': master['Store_Key'].isna().sum(),
        'Missing Sales Dates': master['Sales_Date'].isna().sum(),
        'Duplicate Rows': master.duplicated().sum(),
        'Product Match Rate': f"{(master['Product_Number'].notna().sum() / len(master) * 100):.2f}%",
        'Store Match Rate': f"{(master['Store_City'].notna().sum() / len(master) * 100):.2f}%",
        'Date Match Rate': f"{(master['Year'].notna().sum() / len(master) * 100):.2f}%",
        'Purchase Match Rate': f"{(master['Purchase_Quantity'].notna().sum() / len(master) * 100):.2f}%",
        'Inventory Match Rate': f"{(master['On_Hand_Quantity'].notna().sum() / len(master) * 100):.2f}%"
    }
    
    for metric, value in validation_summary.items():
        print(f'  {metric:.<50} {value}')
    
    print()
    
    # Check for critical issues
    critical_issues = []
    if master['Product_Number'].isna().sum() > 0:
        critical_issues.append('Missing product numbers detected')
    if master['Store_Key'].isna().sum() > 0:
        critical_issues.append('Missing store keys detected')
    if master['Sales_Date'].isna().sum() > 0:
        critical_issues.append('Missing sales dates detected')
    
    if critical_issues:
        print('  ⚠️  CRITICAL ISSUES FOUND:')
        for issue in critical_issues:
            print(f'     - {issue}')
    else:
        print('  ✅ No critical issues found')
    
    print()
    
    # ============================================================================
    # STEP 9: Organize columns in logical order
    # ============================================================================
    print('Step 9: Organizing columns...')
    print('-'*100)
    
    # Define column order
    column_order = [
        # Transaction Keys
        'Sales_Order',
        'Sales_Date',
        
        # Product Attributes (already in fact_sales)
        'Product_Number',
        'Description',
        'Size',
        
        # Store Attributes
        'Store_Key',
        'Store_City',
        'Store_State',
        'Store_Region',
        
        # Date Attributes
        'Year',
        'Quarter',
        'Month',
        'Month_Name',
        'Week',
        'Day_of_Week',
        'Day_Name',
        
        # Sales Metrics
        'Sales_Quantity',
        'Sales_Price',
        'Gross_Revenue',
        'Tax',
        'Net_Revenue',
        
        # Purchase Metrics
        'Purchase_Orders',
        'Purchase_Quantity',
        'Purchase_Unit_Cost',
        'Purchase_Cost',
        'Total_Purchase_Amount',
        'Total_Freight_Cost',
        'Landed_Cost',
        
        # Vendor Attributes
        'Vendor_Key',
        'Vendor_Name',
        'Vendor_Lead_Time',
        
        # Inventory Metrics
        'On_Hand_Quantity',
        'Inventory_Value',
        'Snapshot_Type',
        
        # KPI Metrics
        'Gross_Profit',
        'Margin_Percent',
        'Inventory_Turnover',
        'Days_of_Inventory'
    ]
    
    # Reorder columns (keep only existing ones)
    existing_cols = [col for col in column_order if col in master.columns]
    other_cols = [col for col in master.columns if col not in existing_cols]
    master = master[existing_cols + other_cols]
    
    print(f'  ✓ Columns organized: {len(master.columns)} total')
    print()
    
    # ============================================================================
    # STEP 10: Export to Parquet and CSV
    # ============================================================================
    print('Step 10: Exporting master dataset...')
    print('-'*100)
    
    # Parquet export
    parquet_file = OUTPUT_FILE
    master.to_parquet(parquet_file, index=False, compression='snappy')
    parquet_size_mb = parquet_file.stat().st_size / (1024 * 1024)
    print(f'  ✓ Exported to Parquet: {parquet_file}')
    print(f'     File size: {parquet_size_mb:.2f} MB')
    
    # CSV export
    csv_file = DATA_MODEL_DIR / 'master_dataset.csv'
    master.to_csv(csv_file, index=False)
    csv_size_mb = csv_file.stat().st_size / (1024 * 1024)
    print(f'  ✓ Exported to CSV: {csv_file}')
    print(f'     File size: {csv_size_mb:.2f} MB')
    print()
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print('='*100)
    print('MASTER DATASET CREATED SUCCESSFULLY')
    print('='*100)
    print()
    print(f'  Total Records: {len(master):,}')
    print(f'  Total Columns: {len(master.columns)}')
    print(f'  Date Range: {master["Sales_Date"].min().date()} to {master["Sales_Date"].max().date()}')
    print(f'  Unique Products: {master["Product_Number"].nunique():,}')
    print(f'  Unique Stores: {master["Store_Key"].nunique()}')
    print(f'  Unique Vendors: {master["Vendor_Key"].nunique()}')
    print()
    
    # Financial Summary
    gross_revenue = master['Gross_Revenue'].sum()
    total_tax = master['Tax'].sum()
    net_revenue = master['Net_Revenue'].sum()
    total_freight = master['Total_Freight_Cost'].sum()
    total_profit = master['Gross_Profit'].sum()
    avg_margin = master['Margin_Percent'].mean()
    
    print('  Financial Summary:')
    print(f'    - Gross Revenue: ${gross_revenue:,.2f}')
    print(f'    - Total Tax: ${total_tax:,.2f}')
    print(f'    - Net Revenue: ${net_revenue:,.2f}')
    print(f'    - Total Freight Cost: ${total_freight:,.2f}')
    print(f'    - Total Gross Profit: ${total_profit:,.2f}')
    print(f'    - Average Margin %: {avg_margin:.2f}%')
    print()
    print('='*100)
    
    return master


if __name__ == '__main__':
    master_df = create_master_dataset()
    print('\nMaster dataset returned successfully!')
    print(f'Shape: {master_df.shape}')
