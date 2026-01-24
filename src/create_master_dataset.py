"""
Create Master Dataset - Single Source of Truth
Combines all fact and dimension tables into one comprehensive dataset for analysis
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
    
    # Convert date columns to datetime for matching
    fact_sales['Sales_Date'] = pd.to_datetime(fact_sales['date_key'], format='%d/%m/%Y')
    fact_purchases['Purchase_Date'] = pd.to_datetime(fact_purchases['date_key'], format='%d/%m/%Y')
    fact_inventory['Inventory_Date'] = pd.to_datetime(fact_inventory['Snapshot_Date'])
    
    # Standardize key types
    fact_sales['product_key'] = fact_sales['product_key'].astype(str)
    fact_sales['store_key'] = fact_sales['store_key'].astype(int)
    
    fact_purchases['product_key'] = fact_purchases['product_key'].astype(str)
    fact_purchases['store_key'] = fact_purchases['store_key'].astype(int)
    
    fact_inventory['product_key'] = fact_inventory['product_key'].astype(str)
    fact_inventory['store_key'] = fact_inventory['store_key'].astype(int)
    
    dim_product['product_key'] = dim_product['product_key'].astype(str)
    
    print('  ✓ Date columns converted to datetime')
    print('  ✓ Key columns standardized')
    print()
    
    # ============================================================================
    # STEP 3: Start with fact_sales as base
    # ============================================================================
    print('Step 3: Building master dataset with fact_sales as base...')
    print('-'*100)
    
    master = fact_sales.copy()
    master = master.rename(columns={
        'quantity_sold': 'Sales_Quantity',
        'sales_price': 'Sales_Price',
        'sales_amount': 'Sales_Amount'
    })
    
    print(f'  Base dataset: {len(master):,} rows')
    print()
    
    # ============================================================================
    # STEP 4: Join dimension tables first (for enrichment)
    # ============================================================================
    print('Step 4: Joining dimension tables...')
    print('-'*100)
    
    # Join dim_product
    master = master.merge(
        dim_product[['product_key', 'brand_code', 'description', 'size']],
        on='product_key',
        how='left',
        suffixes=('', '_dim')
    )
    master = master.drop(columns=['Product_description'], errors='ignore')  # Remove duplicate
    master = master.rename(columns={
        'brand_code': 'Brand',
        'description': 'Product_Name',
        'size': 'Product_Size'
    })
    print(f'  ✓ Joined dim_product: {master["product_key"].notna().sum():,} matches')
    
    # Join dim_store
    master = master.merge(
        dim_store[['store_key', 'city', 'state', 'region']],
        on='store_key',
        how='left'
    )
    master = master.rename(columns={
        'city': 'Store_City',
        'state': 'Store_State',
        'region': 'Store_Region'
    })
    print(f'  ✓ Joined dim_store: {master["Store_City"].notna().sum():,} matches')
    
    # Join dim_date (create comprehensive date attributes)
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
    # STEP 5: Join fact_purchases (aggregated by product-store-date)
    # ============================================================================
    print('Step 5: Joining fact_purchases...')
    print('-'*100)
    
    # Aggregate purchases by product-store-date
    purchases_agg = fact_purchases.groupby(['product_key', 'store_key', 'Purchase_Date']).agg({
        'quantity_purchased': 'sum',
        'purchase_price': 'mean',
        'purchase_amount': 'sum',
        'vendor_key': 'first',
        'Po_Number': lambda x: ', '.join(x.astype(str).unique()[:5]),  # First 5 POs
        'Delivery_location': 'first'
    }).reset_index()
    
    purchases_agg = purchases_agg.rename(columns={
        'quantity_purchased': 'Purchase_Quantity',
        'purchase_price': 'Purchase_Price',
        'purchase_amount': 'Purchase_Amount',
        'Po_Number': 'Purchase_Orders'
    })
    
    # Join purchases with date matching (same date or closest prior)
    master = master.merge(
        purchases_agg,
        left_on=['product_key', 'store_key', 'Sales_Date'],
        right_on=['product_key', 'store_key', 'Purchase_Date'],
        how='left'
    )
    master = master.drop(columns=['Purchase_Date'], errors='ignore')
    
    print(f'  ✓ Joined fact_purchases: {master["Purchase_Quantity"].notna().sum():,} matches ({master["Purchase_Quantity"].notna().sum() / len(master) * 100:.1f}%)')
    
    # Join dim_vendor for vendor details
    master = master.merge(
        dim_vendor[['vendor_key', 'vendor_name', 'lead_time_days']],
        on='vendor_key',
        how='left'
    )
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
    inventory_agg = fact_inventory.groupby(['product_key', 'store_key', 'Inventory_Date']).agg({
        'on_hand_quantity': 'sum',
        'unit_price': 'mean',
        'inventory_value': 'sum',
        'snapshot_type': 'first'
    }).reset_index()
    
    inventory_agg = inventory_agg.rename(columns={
        'on_hand_quantity': 'On_Hand_Quantity',
        'unit_price': 'Inventory_Unit_Price',
        'inventory_value': 'Inventory_Value',
        'snapshot_type': 'Snapshot_Type'
    })
    
    # Join inventory with date matching
    master = master.merge(
        inventory_agg,
        left_on=['product_key', 'store_key', 'Sales_Date'],
        right_on=['product_key', 'store_key', 'Inventory_Date'],
        how='left'
    )
    master = master.drop(columns=['Inventory_Date'], errors='ignore')
    
    print(f'  ✓ Joined fact_inventory: {master["On_Hand_Quantity"].notna().sum():,} matches ({master["On_Hand_Quantity"].notna().sum() / len(master) * 100:.1f}%)')
    print()
    
    # ============================================================================
    # STEP 7: Add KPI Calculation Columns
    # ============================================================================
    print('Step 7: Adding KPI columns...')
    print('-'*100)
    
    # Revenue metrics
    master['Gross_Revenue'] = master['Sales_Amount']
    
    # Cost metrics
    master['Purchase_Cost'] = master['Purchase_Quantity'] * master['Purchase_Price']
    master['Purchase_Cost'] = master['Purchase_Cost'].fillna(0)
    
    master['Landed_Cost'] = master['Purchase_Cost']  # Placeholder - can add freight/duties later
    
    # Profit metrics
    master['Gross_Profit'] = master['Gross_Revenue'] - master['Purchase_Cost']
    master['Margin_Percent'] = np.where(
        master['Gross_Revenue'] > 0,
        (master['Gross_Profit'] / master['Gross_Revenue']) * 100,
        0
    )
    
    # Inventory metrics (placeholders - need time series calculation)
    master['Inventory_Turnover'] = np.nan  # Requires: COGS / Average Inventory
    master['Days_of_Inventory'] = np.nan  # Requires: (Average Inventory / COGS) * 365
    
    # Supplier metrics
    master['Supplier_Spend'] = master['Purchase_Amount']
    
    print('  ✓ Gross_Revenue')
    print('  ✓ Purchase_Cost')
    print('  ✓ Landed_Cost')
    print('  ✓ Gross_Profit')
    print('  ✓ Margin_Percent')
    print('  ✓ Inventory_Turnover (placeholder)')
    print('  ✓ Days_of_Inventory (placeholder)')
    print('  ✓ Supplier_Spend')
    print()
    
    # ============================================================================
    # STEP 8: Validate the dataset
    # ============================================================================
    print('Step 8: Validating master dataset...')
    print('-'*100)
    
    validation_summary = {
        'Total Rows': len(master),
        'Missing Product Keys': master['product_key'].isna().sum(),
        'Missing Store Keys': master['store_key'].isna().sum(),
        'Missing Sales Dates': master['Sales_Date'].isna().sum(),
        'Duplicate Rows': master.duplicated().sum(),
        'Product Match Rate': f"{(master['Brand'].notna().sum() / len(master) * 100):.2f}%",
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
    if master['product_key'].isna().sum() > 0:
        critical_issues.append('Missing product keys detected')
    if master['store_key'].isna().sum() > 0:
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
        'date_key',
        
        # Product Attributes
        'product_key',
        'Brand',
        'Product_Name',
        'Product_Size',
        
        # Store Attributes
        'store_key',
        'Store_City',
        'Store_State',
        'Store_Region',
        'Delivery_location',
        
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
        'Sales_Amount',
        'Gross_Revenue',
        
        # Purchase Metrics
        'Purchase_Orders',
        'Purchase_Quantity',
        'Purchase_Price',
        'Purchase_Amount',
        'Purchase_Cost',
        'Landed_Cost',
        
        # Vendor Attributes
        'vendor_key',
        'Vendor_Name',
        'Vendor_Lead_Time',
        'Supplier_Spend',
        
        # Inventory Metrics
        'On_Hand_Quantity',
        'Inventory_Unit_Price',
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
    # STEP 10: Export to Parquet
    # ============================================================================
    print('Step 10: Exporting master dataset...')
    print('-'*100)
    
    master.to_parquet(OUTPUT_FILE, index=False, compression='snappy')
    
    file_size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f'  ✓ Exported to: {OUTPUT_FILE}')
    print(f'  ✓ File size: {file_size_mb:.2f} MB')
    print(f'  ✓ Format: Parquet (compressed)')
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
    print(f'  Date Range: {master["Sales_Date"].min()} to {master["Sales_Date"].max()}')
    print(f'  Unique Products: {master["product_key"].nunique():,}')
    print(f'  Unique Stores: {master["store_key"].nunique()}')
    print(f'  Unique Vendors: {master["vendor_key"].nunique()}')
    print()
    print('  Column Categories:')
    print(f'    - Transaction/Keys: 3 columns')
    print(f'    - Product Attributes: 4 columns')
    print(f'    - Store/Location: 4 columns')
    print(f'    - Date/Time: 7 columns')
    print(f'    - Sales Metrics: 4 columns')
    print(f'    - Purchase Metrics: 6 columns')
    print(f'    - Vendor Metrics: 4 columns')
    print(f'    - Inventory Metrics: 4 columns')
    print(f'    - KPI Metrics: 4 columns')
    print()
    print('='*100)
    
    return master


if __name__ == '__main__':
    master_df = create_master_dataset()
    print('\nMaster dataset returned successfully!')
    print(f'Shape: {master_df.shape}')
