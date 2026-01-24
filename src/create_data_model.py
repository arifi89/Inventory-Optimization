"""
================================================================================
CREATE DATA MODEL - Star Schema Builder
================================================================================
Purpose: Transform cleaned data into dimensional model (Star Schema)
Author: System
Date: January 24, 2026
Version: 1.0

This script creates the official analytical data model with:
- 3 Fact Tables: Fact_Sales, Fact_Purchases, Fact_Inventory_Snapshot
- 4 Dimension Tables: Dim_Product, Dim_Store, Dim_Vendor, Dim_Date

REUSABLE FOR ANY COMPANY - Just update the file paths!
================================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION - UPDATE THESE PATHS FOR YOUR COMPANY
# ============================================================================

class Config:
    """Configuration for data model creation - REUSABLE"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    INPUT_DIR = BASE_DIR / 'data' / 'processed'
    OUTPUT_DIR = BASE_DIR / 'data' / 'data_model'
    
    # Input files (cleaned data)
    SALES_FILE = INPUT_DIR / 'cleaned_sales.csv'
    PURCHASES_FILE = INPUT_DIR / 'cleaned_purchases.csv'
    INVOICE_PURCHASES_FILE = INPUT_DIR / 'cleaned_invoice_purchases.csv'
    BEGIN_INV_FILE = INPUT_DIR / 'cleaned_beginning_inventory.csv'
    END_INV_FILE = INPUT_DIR / 'cleaned_ending_inventory.csv'
    FUTURE_PRICES_FILE = INPUT_DIR / 'cleaned_future_prices.csv'
    
    # Output files (dimensional model)
    FACT_SALES = OUTPUT_DIR / 'fact_sales.csv'
    FACT_PURCHASES = OUTPUT_DIR / 'fact_purchases.csv'
    FACT_INVENTORY = OUTPUT_DIR / 'fact_inventory_snapshot.csv'
    DIM_PRODUCT = OUTPUT_DIR / 'dim_product.csv'
    DIM_STORE = OUTPUT_DIR / 'dim_store.csv'
    DIM_VENDOR = OUTPUT_DIR / 'dim_vendor.csv'
    DIM_DATE = OUTPUT_DIR / 'dim_date.csv'
    
    # Date range for date dimension
    DATE_START = '2015-01-01'  # Extended to capture all data
    DATE_END = '2018-12-31'
    
    # Company-specific settings
    COMPANY_NAME = 'Inventory Optimization Co.'
    FISCAL_YEAR_START_MONTH = 1  # January = 1


# ============================================================================
# DIMENSION TABLE BUILDERS
# ============================================================================

def create_dim_date(start_date, end_date):
    """
    Create comprehensive date dimension
    
    Parameters:
    -----------
    start_date : str
        Start date in YYYY-MM-DD format
    end_date : str
        End date in YYYY-MM-DD format
    
    Returns:
    --------
    pd.DataFrame : Date dimension table
    """
    print("📅 Building Dim_Date...")
    
    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df = pd.DataFrame({'full_date': dates})
    
    # Create date attributes
    df['date_key'] = df['full_date'].dt.strftime('%Y%m%d').astype(int)
    df['year'] = df['full_date'].dt.year
    df['quarter'] = df['full_date'].dt.quarter
    df['month'] = df['full_date'].dt.month
    df['month_name'] = df['full_date'].dt.strftime('%B')
    df['week'] = df['full_date'].dt.isocalendar().week
    df['day_of_week'] = df['full_date'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
    df['day_name'] = df['full_date'].dt.strftime('%A')
    df['day_of_month'] = df['full_date'].dt.day
    df['day_of_year'] = df['full_date'].dt.dayofyear
    
    # Flags
    df['is_weekend'] = df['day_of_week'].isin([6, 7])
    df['is_month_start'] = df['full_date'].dt.is_month_start
    df['is_month_end'] = df['full_date'].dt.is_month_end
    df['is_quarter_start'] = df['full_date'].dt.is_quarter_start
    df['is_quarter_end'] = df['full_date'].dt.is_quarter_end
    df['is_year_start'] = df['full_date'].dt.is_year_start
    df['is_year_end'] = df['full_date'].dt.is_year_end
    
    # Fiscal calendar (configurable)
    fiscal_month_offset = Config.FISCAL_YEAR_START_MONTH - 1
    df['fiscal_year'] = df['full_date'].apply(
        lambda x: x.year if x.month >= Config.FISCAL_YEAR_START_MONTH else x.year - 1
    )
    df['fiscal_quarter'] = ((df['month'] - Config.FISCAL_YEAR_START_MONTH) % 12 // 3) + 1
    
    # US Federal Holidays (basic list - customize for your company)
    df['is_holiday'] = False
    for year in df['year'].unique():
        holidays = [
            f'{year}-01-01',  # New Year's Day
            f'{year}-07-04',  # Independence Day
            f'{year}-12-25',  # Christmas
        ]
        df.loc[df['full_date'].isin(pd.to_datetime(holidays)), 'is_holiday'] = True
    
    # Reorder columns
    cols = ['date_key', 'full_date', 'year', 'quarter', 'month', 'month_name', 
            'week', 'day_of_week', 'day_name', 'day_of_month', 'day_of_year',
            'is_weekend', 'is_month_start', 'is_month_end', 'is_quarter_start',
            'is_quarter_end', 'is_year_start', 'is_year_end', 'is_holiday',
            'fiscal_year', 'fiscal_quarter']
    
    df = df[cols]
    
    print(f"   ✅ Created {len(df):,} date records from {start_date} to {end_date}")
    return df


def create_dim_product(sales_df, purchases_df, begin_inv_df, end_inv_df):
    """
    Create product dimension from all source files
    
    Returns:
    --------
    pd.DataFrame : Product dimension table
    """
    print("📦 Building Dim_Product...")
    
    # Collect all unique products from all sources
    product_sources = []
    
    # From sales
    if 'Brand' in sales_df.columns and 'Description' in sales_df.columns:
        sales_products = sales_df[['Brand', 'Description', 'Size']].drop_duplicates()
        sales_products['source'] = 'sales'
        product_sources.append(sales_products)
    
    # From purchases
    if 'Brand' in purchases_df.columns and 'Description' in purchases_df.columns:
        purch_products = purchases_df[['Brand', 'Description', 'Size']].drop_duplicates()
        purch_products['source'] = 'purchases'
        product_sources.append(purch_products)
    
    # From beginning inventory
    if 'Brand' in begin_inv_df.columns:
        begin_products = begin_inv_df[['Brand', 'Description', 'Size']].drop_duplicates()
        begin_products['source'] = 'begin_inv'
        product_sources.append(begin_products)
    
    # From ending inventory
    if 'Brand' in end_inv_df.columns:
        end_products = end_inv_df[['Brand', 'Description', 'Size']].drop_duplicates()
        end_products['source'] = 'end_inv'
        product_sources.append(end_products)
    
    # Combine all product sources
    all_products = pd.concat(product_sources, ignore_index=True)
    
    # Get unique products
    dim_product = all_products[['Brand', 'Description', 'Size']].drop_duplicates().reset_index(drop=True)
    
    # Rename columns
    dim_product.rename(columns={
        'Brand': 'brand_code',
        'Description': 'description',
        'Size': 'size'
    }, inplace=True)
    
    # Create surrogate key (product_key) - ensure uniqueness
    dim_product['product_key'] = (
        dim_product['brand_code'].astype(str) + '_' + 
        dim_product['size'].astype(str)
    )
    
    # Remove any duplicates in product_key
    dim_product = dim_product.drop_duplicates(subset=['product_key'], keep='first').reset_index(drop=True)
    
    # Add product attributes (placeholders - to be enriched later)
    dim_product['category'] = 'Beverage'  # Update with actual categorization logic
    dim_product['subcategory'] = 'Unknown'
    dim_product['abc_class'] = None  # Will be populated from ABC analysis
    dim_product['xyz_class'] = None  # Will be populated from XYZ analysis
    
    # SCD Type 2 fields
    dim_product['is_active'] = True
    dim_product['effective_date'] = datetime.now().date()
    dim_product['expiration_date'] = pd.to_datetime('2099-12-31').date()
    
    # Audit fields
    dim_product['created_date'] = datetime.now()
    dim_product['modified_date'] = datetime.now()
    
    # Reorder columns
    cols = ['product_key', 'brand_code', 'description', 'size', 'category', 
            'subcategory', 'abc_class', 'xyz_class', 'is_active', 
            'effective_date', 'expiration_date', 'created_date', 'modified_date']
    dim_product = dim_product[cols]
    
    print(f"   ✅ Created {len(dim_product):,} unique products")
    return dim_product


def create_dim_store(sales_df, inventory_df):
    """
    Create store dimension with city, state, and region information
    
    Returns:
    --------
    pd.DataFrame : Store dimension table
    """
    print("🏪 Building Dim_Store...")
    
    # Prioritize inventory data as it has complete city information
    if 'Store' in inventory_df.columns and 'City' in inventory_df.columns:
        # Get stores from inventory (primary source)
        dim_store = inventory_df[['Store', 'City']].drop_duplicates().copy()
    elif 'Store' in sales_df.columns and 'City' in sales_df.columns:
        # Fallback to sales if inventory doesn't have city
        dim_store = sales_df[['Store', 'City']].drop_duplicates().copy()
    else:
        # Last resort - just store numbers
        stores = []
        if 'Store' in inventory_df.columns:
            stores.append(inventory_df[['Store']].drop_duplicates())
        if 'Store' in sales_df.columns:
            stores.append(sales_df[['Store']].drop_duplicates())
        dim_store = pd.concat(stores, ignore_index=True).drop_duplicates()
        dim_store['City'] = 'Unknown'
    
    # Remove duplicates based on Store number (keep first occurrence)
    dim_store = dim_store.drop_duplicates(subset=['Store'], keep='first').reset_index(drop=True)
    
    # Rename columns
    dim_store.rename(columns={
        'Store': 'store_key',
        'City': 'city'
    }, inplace=True)
    
    # Clean city names (capitalize properly)
    dim_store['city'] = dim_store['city'].str.title()
    
    # Comprehensive city-to-state and region mapping for all UK locations
    # Based on UK administrative divisions and regions
    city_mapping = {
        # Major Cities
        'Aberdeen': {'state': 'Aberdeenshire', 'region': 'Scotland'},
        'Blackpool': {'state': 'Lancashire', 'region': 'North West'},
        'Doncaster': {'state': 'South Yorkshire', 'region': 'North'},
        'Hartlepool': {'state': 'County Durham', 'region': 'North East'},
        'Kilmarnock': {'state': 'Ayrshire', 'region': 'Scotland'},
        'Lewes': {'state': 'East Sussex', 'region': 'South East'},
        'Luton': {'state': 'Bedfordshire', 'region': 'East'},
        'Norfolk': {'state': 'Norfolk', 'region': 'East'},
        'Oldham': {'state': 'Greater Manchester', 'region': 'North West'},
        'Tamworth': {'state': 'Staffordshire', 'region': 'Midlands'},
        'Aylesbury': {'state': 'Buckinghamshire', 'region': 'South East'},
        
        # Yorkshire & The Humber
        'Hardersfield': {'state': 'Yorkshire', 'region': 'North'},
        'Cesterfield': {'state': 'Derbyshire', 'region': 'Midlands'},
        
        # Scotland
        'Eanverness': {'state': 'Highlands', 'region': 'Scotland'},
        'Balerno': {'state': 'Midlothian', 'region': 'Scotland'},
        'Pitmerden': {'state': 'Aberdeenshire', 'region': 'Scotland'},
        'Guthram': {'state': 'Highlands', 'region': 'Scotland'},
        'Halivaara': {'state': 'Highlands', 'region': 'Scotland'},
        
        # London & South East
        'Hornsey': {'state': 'Greater London', 'region': 'London'},
        'Sutton': {'state': 'Greater London', 'region': 'London'},
        'Stanmore': {'state': 'Greater London', 'region': 'London'},
        'Arbington': {'state': 'Greater London', 'region': 'London'},
        
        # South West
        'Goulcrest': {'state': 'Somerset', 'region': 'South West'},
        'Wanborne': {'state': 'Dorset', 'region': 'South West'},
        'Lundy': {'state': 'Devon', 'region': 'South West'},
        'Lanteglos': {'state': 'Cornwall', 'region': 'South West'},
        'Tywardreath': {'state': 'Cornwall', 'region': 'South West'},
        'Porthcrawl': {'state': 'Cornwall', 'region': 'South West'},
        'Paethsmouth': {'state': 'Devon', 'region': 'South West'},
        'Aethelney': {'state': 'Somerset', 'region': 'South West'},
        
        # North West
        'Furness': {'state': 'Cumbria', 'region': 'North West'},
        'Wintervale': {'state': 'Cheshire', 'region': 'North West'},
        'Culcheth': {'state': 'Cheshire', 'region': 'North West'},
        'Garigill': {'state': 'Cumbria', 'region': 'North West'},
        'Keld': {'state': 'Cumbria', 'region': 'North West'},
        
        # Midlands
        'Bromwich': {'state': 'West Midlands', 'region': 'Midlands'},
        'Tarmsworth': {'state': 'Staffordshire', 'region': 'Midlands'},
        'Ashborne': {'state': 'Derbyshire', 'region': 'Midlands'},
        'Bredwardine': {'state': 'Herefordshire', 'region': 'West Midlands'},
        'Graycott': {'state': 'Warwickshire', 'region': 'Midlands'},
        'Mountmend': {'state': 'Worcestershire', 'region': 'Midlands'},
        'Wolford': {'state': 'Warwickshire', 'region': 'Midlands'},
        
        # North East
        'Alnerwick': {'state': 'Northumberland', 'region': 'North East'},
        'Larnwick': {'state': 'Northumberland', 'region': 'North East'},
        'Sharnwick': {'state': 'Northumberland', 'region': 'North East'},
        
        # Wales
        'Cardend': {'state': 'South Wales', 'region': 'Wales'},
        'Caershire': {'state': 'Mid Wales', 'region': 'Wales'},
        'Paentmarwy': {'state': 'North Wales', 'region': 'Wales'},
        'Ballymena': {'state': 'North Wales', 'region': 'Wales'},
        
        # Ireland
        'Leeside': {'state': 'Cork', 'region': 'Ireland'},
        'Irragin': {'state': 'Connacht', 'region': 'Ireland'},
        
        # East England
        'Claethorpes': {'state': 'Lincolnshire', 'region': 'East Midlands'},
        'Barncombe': {'state': 'Norfolk', 'region': 'East'},
        'Clarcton': {'state': 'Essex', 'region': 'East'},
        'Easthaven': {'state': 'Suffolk', 'region': 'East'},
        'Easthallow': {'state': 'Norfolk', 'region': 'East'},
        
        # Other Notable Locations
        'Hillfar': {'state': 'Northamptonshire', 'region': 'Midlands'},
        'Bullmar': {'state': 'Gloucestershire', 'region': 'South West'},
        'Palperroth': {'state': 'Pembrokeshire', 'region': 'Wales'},
        'Solaris': {'state': 'Kent', 'region': 'South East'},
        'Veritas': {'state': 'Hampshire', 'region': 'South East'},
        'Swordbreak': {'state': 'Northumberland', 'region': 'North East'},
        
        # Fantasy/Fictional Towns (assign to nearest real regions)
        "Beggar'S Hole": {'state': 'Yorkshire', 'region': 'North'},
        'Black Hollow': {'state': 'Derbyshire', 'region': 'Midlands'},
        'Dry Gulch': {'state': 'Lincolnshire', 'region': 'East Midlands'},
        "Knife'S Edge": {'state': 'Cumbria', 'region': 'North West'},
        "Pella'S Wish": {'state': 'Cornwall', 'region': 'South West'},
    }
    
    # Apply mapping to get state and region
    dim_store['state'] = dim_store['city'].map(lambda x: city_mapping.get(x, {}).get('state', 'Unknown'))
    dim_store['region'] = dim_store['city'].map(lambda x: city_mapping.get(x, {}).get('region', 'Unknown'))
    
    # Add store attributes
    dim_store['store_name'] = dim_store['city'] + ' Store #' + dim_store['store_key'].astype(str)
    dim_store['store_type'] = 'Retail'
    dim_store['is_active'] = True
    
    # Audit fields
    dim_store['created_date'] = datetime.now()
    dim_store['modified_date'] = datetime.now()
    
    # Reorder columns
    cols = ['store_key', 'store_name', 'city', 'state', 'region', 
            'store_type', 'is_active', 'created_date', 'modified_date']
    dim_store = dim_store[cols]
    
    print(f"   ✅ Created {len(dim_store):,} stores")
    return dim_store


def create_dim_vendor(purchases_df):
    """
    Create vendor dimension with calculated lead times
    
    Returns:
    --------
    pd.DataFrame : Vendor dimension table
    """
    print("🏭 Building Dim_Vendor...")
    
    # Calculate lead times from purchases data
    lead_times = None
    if 'Po_Date' in purchases_df.columns and 'Receiving_Date' in purchases_df.columns:
        # Create a copy for lead time calculation
        lead_time_df = purchases_df.copy()
        
        # Convert dates to datetime
        lead_time_df['Po_Date'] = pd.to_datetime(lead_time_df['Po_Date'], errors='coerce')
        lead_time_df['Receiving_Date'] = pd.to_datetime(lead_time_df['Receiving_Date'], errors='coerce')
        
        # Calculate lead time in days
        lead_time_df['lead_time'] = (lead_time_df['Receiving_Date'] - lead_time_df['Po_Date']).dt.days
        
        # Remove negative or invalid lead times
        lead_time_df = lead_time_df[lead_time_df['lead_time'] >= 0]
        lead_time_df = lead_time_df[lead_time_df['lead_time'].notna()]
        
        # Get vendor number column name
        vendor_col = 'Vendor_Number' if 'Vendor_Number' in lead_time_df.columns else 'VendorNumber'
        
        if vendor_col in lead_time_df.columns:
            # Calculate average lead time per vendor
            lead_times = lead_time_df.groupby(vendor_col)['lead_time'].agg(['mean', 'median', 'min', 'max', 'count']).round(1)
            lead_times.columns = ['avg_lead_time', 'median_lead_time', 'min_lead_time', 'max_lead_time', 'order_count']
            lead_times = lead_times.reset_index()
            print(f"   📊 Calculated lead times for {len(lead_times)} vendors")
    
    # Get unique vendors - check for actual column names
    if 'Vendor_Name' in purchases_df.columns and 'Vendor_Number' in purchases_df.columns:
        dim_vendor = purchases_df[['Vendor_Number', 'Vendor_Name']].drop_duplicates()
    elif 'VendorName' in purchases_df.columns and 'VendorNumber' in purchases_df.columns:
        dim_vendor = purchases_df[['VendorNumber', 'VendorName']].drop_duplicates()
    elif 'Vendor_Number' in purchases_df.columns:
        dim_vendor = purchases_df[['Vendor_Number']].drop_duplicates()
        dim_vendor['Vendor_Name'] = 'Vendor ' + dim_vendor['Vendor_Number'].astype(str)
    elif 'VendorNumber' in purchases_df.columns:
        dim_vendor = purchases_df[['VendorNumber']].drop_duplicates()
        dim_vendor['VendorName'] = 'Vendor ' + dim_vendor['VendorNumber'].astype(str)
    else:
        # Create placeholder if no vendor info
        dim_vendor = pd.DataFrame({'Vendor_Number': ['UNKNOWN'], 'Vendor_Name': ['Unknown Vendor']})
    
    # Rename columns
    rename_map = {
        'VendorNumber': 'vendor_key',
        'VendorName': 'vendor_name',
        'Vendor_Number': 'vendor_key',
        'Vendor_Name': 'vendor_name'
    }
    
    for old_col, new_col in rename_map.items():
        if old_col in dim_vendor.columns:
            dim_vendor.rename(columns={old_col: new_col}, inplace=True)
    
    # Remove duplicates based on vendor_key
    dim_vendor = dim_vendor.drop_duplicates(subset=['vendor_key'], keep='first').reset_index(drop=True)
    
    # Merge lead time data if available
    if lead_times is not None:
        # Ensure vendor_key column name matches
        lead_time_col = 'Vendor_Number' if 'Vendor_Number' in lead_times.columns else 'VendorNumber'
        if lead_time_col in lead_times.columns:
            lead_times.rename(columns={lead_time_col: 'vendor_key'}, inplace=True)
        
        # Merge lead times
        dim_vendor = dim_vendor.merge(lead_times, on='vendor_key', how='left')
        print(f"   ✅ Added lead time metrics to vendor dimension")
    else:
        # Add empty columns if no lead time data
        dim_vendor['avg_lead_time'] = None
        dim_vendor['median_lead_time'] = None
        dim_vendor['min_lead_time'] = None
        dim_vendor['max_lead_time'] = None
        dim_vendor['order_count'] = None
    
    # Rename avg_lead_time to lead_time_days for consistency
    if 'avg_lead_time' in dim_vendor.columns:
        dim_vendor['lead_time_days'] = dim_vendor['avg_lead_time']
    else:
        dim_vendor['lead_time_days'] = None
    
    # Add other attributes (placeholders - to be enriched from Kraljic analysis)
    dim_vendor['vendor_classification'] = None  # Strategic/Leverage/Bottleneck/Non-critical
    dim_vendor['contact_info'] = None
    dim_vendor['is_preferred'] = False
    dim_vendor['is_active'] = True
    
    # Audit fields
    dim_vendor['created_date'] = datetime.now()
    dim_vendor['modified_date'] = datetime.now()
    
    # Reorder columns
    cols = ['vendor_key', 'vendor_name', 'lead_time_days', 'avg_lead_time', 'median_lead_time', 
            'min_lead_time', 'max_lead_time', 'order_count', 'vendor_classification', 
            'contact_info', 'is_preferred', 'is_active', 'created_date', 'modified_date']
    
    # Only include columns that exist
    cols = [col for col in cols if col in dim_vendor.columns]
    dim_vendor = dim_vendor[cols]
    
    print(f"   ✅ Created {len(dim_vendor):,} vendors")
    return dim_vendor


# ============================================================================
# FACT TABLE BUILDERS
# ============================================================================

def create_fact_sales(sales_df, dim_product, dim_store, dim_date):
    """
    Create sales fact table
    
    Returns:
    --------
    pd.DataFrame : Sales fact table
    """
    print("💰 Building Fact_Sales...")
    
    fact = sales_df.copy()
    
    # Create product_key for joining
    if 'Brand' in fact.columns and 'Size' in fact.columns:
        fact['product_key'] = (
            fact['Brand'].astype(str) + '_' + 
            fact['Size'].astype(str)
        )
    
    # Create date_key from actual column name
    if 'Sales_Date' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['Sales_Date']).dt.strftime('%Y%m%d').astype(int)
    elif 'SalesDate' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['SalesDate']).dt.strftime('%Y%m%d').astype(int)
    elif 'Date' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['Date']).dt.strftime('%Y%m%d').astype(int)
    
    # Rename columns to match fact table schema
    column_mapping = {
        'Store': 'store_key',
        'Sales_Quantity': 'quantity_sold',
        'Unit_Price': 'sales_price',
        'Total_Price': 'sales_amount',
        'SalesQuantity': 'quantity_sold',
        'SalesPrice': 'sales_price',
        'SalesDollars': 'sales_amount',
        'Sales_Order': 'sale_id'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in fact.columns:
            fact.rename(columns={old_col: new_col}, inplace=True)
    
    # Calculate sales_amount if not present
    if 'sales_amount' not in fact.columns and 'quantity_sold' in fact.columns and 'sales_price' in fact.columns:
        fact['sales_amount'] = fact['quantity_sold'] * fact['sales_price']
    
    # Create unique sale_id if Sales_Order column wasn't present
    if 'sale_id' not in fact.columns:
        fact['sale_id'] = (
            fact['store_key'].astype(str) + '_' +
            fact['date_key'].astype(str) + '_' +
            fact['product_key'].astype(str) + '_' +
            fact.groupby(['store_key', 'date_key', 'product_key']).cumcount().astype(str)
        )
    
    # Select final columns
    final_cols = ['sale_id', 'date_key', 'product_key', 'store_key', 
                  'quantity_sold', 'sales_price', 'sales_amount']
    
    # Keep only columns that exist
    final_cols = [col for col in final_cols if col in fact.columns]
    fact_sales = fact[final_cols]
    
    print(f"   ✅ Created {len(fact_sales):,} sales transactions")
    return fact_sales


def create_fact_purchases(purchases_df, invoice_df, dim_product, dim_vendor, dim_date):
    """
    Create purchases fact table
    
    Returns:
    --------
    pd.DataFrame : Purchases fact table
    """
    print("🛒 Building Fact_Purchases...")
    
    fact = purchases_df.copy()
    
    # Create product_key
    if 'Brand' in fact.columns and 'Size' in fact.columns:
        fact['product_key'] = (
            fact['Brand'].astype(str) + '_' + 
            fact['Size'].astype(str)
        )
    
    # Create date_key from actual column names
    if 'Po_Date' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['Po_Date']).dt.strftime('%Y%m%d').astype(int)
    elif 'Receiving_Date' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['Receiving_Date']).dt.strftime('%Y%m%d').astype(int)
    elif 'PurchaseDate' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['PurchaseDate']).dt.strftime('%Y%m%d').astype(int)
    elif 'ReceivingDate' in fact.columns:
        fact['date_key'] = pd.to_datetime(fact['ReceivingDate']).dt.strftime('%Y%m%d').astype(int)
    
    # Rename columns
    column_mapping = {
        'Vendor_Number': 'vendor_key',
        'VendorNumber': 'vendor_key',
        'Quantity': 'quantity_purchased',
        'Total_Price': 'purchase_amount',
        'Dollars': 'purchase_amount',
        'Po_Number': 'po_number',
        'PONumber': 'po_number',
        'Invoice_Date': 'invoice_date',
        'InvoiceDate': 'invoice_date'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in fact.columns:
            fact.rename(columns={old_col: new_col}, inplace=True)
    
    # Calculate purchase_price if possible
    if 'purchase_amount' in fact.columns and 'quantity_purchased' in fact.columns:
        fact['purchase_price'] = fact['purchase_amount'] / fact['quantity_purchased'].replace(0, 1)
    
    # Create unique purchase_id
    fact['purchase_id'] = (
        fact['vendor_key'].astype(str) + '_' +
        fact['date_key'].astype(str) + '_' +
        fact['product_key'].astype(str) + '_' +
        fact.groupby(['vendor_key', 'date_key', 'product_key']).cumcount().astype(str)
    )
    
    # Select final columns
    final_cols = ['purchase_id', 'date_key', 'product_key', 'vendor_key',
                  'quantity_purchased', 'purchase_price', 'purchase_amount', 
                  'po_number', 'invoice_date']
    
    final_cols = [col for col in final_cols if col in fact.columns]
    fact_purchases = fact[final_cols]
    
    print(f"   ✅ Created {len(fact_purchases):,} purchase transactions")
    return fact_purchases


def create_fact_inventory_snapshot(begin_inv_df, end_inv_df, dim_product, dim_store, dim_date):
    """
    Create inventory snapshot fact table
    
    Returns:
    --------
    pd.DataFrame : Inventory snapshot fact table
    """
    print("📊 Building Fact_Inventory_Snapshot...")
    
    # Process beginning inventory
    begin = begin_inv_df.copy()
    begin['snapshot_type'] = 'Beginning'
    if 'Start_Date' in begin.columns:
        begin['snapshot_date'] = pd.to_datetime(begin['Start_Date'])
    else:
        begin['snapshot_date'] = pd.to_datetime('2016-01-01')
    
    # Process ending inventory
    end = end_inv_df.copy()
    end['snapshot_type'] = 'Ending'
    if 'End_Date' in end.columns:
        end['snapshot_date'] = pd.to_datetime(end['End_Date'])
    else:
        end['snapshot_date'] = pd.to_datetime('2016-12-31')
    
    # Combine snapshots
    fact = pd.concat([begin, end], ignore_index=True)
    
    # Create product_key
    if 'Brand' in fact.columns and 'Size' in fact.columns:
        fact['product_key'] = (
            fact['Brand'].astype(str) + '_' + 
            fact['Size'].astype(str)
        )
    
    # Create date_key
    fact['date_key'] = fact['snapshot_date'].dt.strftime('%Y%m%d').astype(int)
    
    # Rename columns
    column_mapping = {
        'Store': 'store_key',
        'On_Hand': 'on_hand_quantity',
        'Sales_Price': 'unit_price'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in fact.columns:
            fact.rename(columns={old_col: new_col}, inplace=True)
    
    # Calculate inventory value
    if 'on_hand_quantity' in fact.columns and 'unit_price' in fact.columns:
        fact['inventory_value'] = fact['on_hand_quantity'] * fact['unit_price']
    
    # Create unique snapshot_id
    fact['snapshot_id'] = (
        fact['store_key'].astype(str) + '_' +
        fact['product_key'].astype(str) + '_' +
        fact['date_key'].astype(str)
    )
    
    # Select final columns
    final_cols = ['snapshot_id', 'date_key', 'product_key', 'store_key',
                  'on_hand_quantity', 'inventory_value', 'snapshot_type']
    
    final_cols = [col for col in final_cols if col in fact.columns]
    fact_inventory = fact[final_cols]
    
    print(f"   ✅ Created {len(fact_inventory):,} inventory snapshots")
    return fact_inventory


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("="*80)
    print("🚀 STAR SCHEMA DATA MODEL BUILDER")
    print("="*80)
    print(f"Company: {Config.COMPANY_NAME}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    # Create output directory
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {Config.OUTPUT_DIR}")
    print()
    
    # ========================================================================
    # STEP 1: LOAD CLEANED DATA
    # ========================================================================
    print("STEP 1: Loading Cleaned Data")
    print("-" * 80)
    
    try:
        sales_df = pd.read_csv(Config.SALES_FILE, low_memory=False)
        print(f"   ✅ Loaded sales: {len(sales_df):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load sales: {e}")
        sales_df = pd.DataFrame()
    
    try:
        purchases_df = pd.read_csv(Config.PURCHASES_FILE, low_memory=False)
        print(f"   ✅ Loaded purchases: {len(purchases_df):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load purchases: {e}")
        purchases_df = pd.DataFrame()
    
    try:
        invoice_df = pd.read_csv(Config.INVOICE_PURCHASES_FILE, low_memory=False)
        print(f"   ✅ Loaded invoice purchases: {len(invoice_df):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load invoice purchases: {e}")
        invoice_df = pd.DataFrame()
    
    try:
        begin_inv_df = pd.read_csv(Config.BEGIN_INV_FILE, low_memory=False)
        print(f"   ✅ Loaded beginning inventory: {len(begin_inv_df):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load beginning inventory: {e}")
        begin_inv_df = pd.DataFrame()
    
    try:
        end_inv_df = pd.read_csv(Config.END_INV_FILE, low_memory=False)
        print(f"   ✅ Loaded ending inventory: {len(end_inv_df):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load ending inventory: {e}")
        end_inv_df = pd.DataFrame()
    
    print()
    
    # ========================================================================
    # STEP 2: CREATE DIMENSION TABLES
    # ========================================================================
    print("STEP 2: Creating Dimension Tables")
    print("-" * 80)
    
    # Dim_Date
    dim_date = create_dim_date(Config.DATE_START, Config.DATE_END)
    dim_date.to_csv(Config.DIM_DATE, index=False)
    print(f"   💾 Saved to: {Config.DIM_DATE.name}")
    print()
    
    # Dim_Product
    dim_product = create_dim_product(sales_df, purchases_df, begin_inv_df, end_inv_df)
    dim_product.to_csv(Config.DIM_PRODUCT, index=False)
    print(f"   💾 Saved to: {Config.DIM_PRODUCT.name}")
    print()
    
    # Dim_Store
    dim_store = create_dim_store(sales_df, begin_inv_df)
    dim_store.to_csv(Config.DIM_STORE, index=False)
    print(f"   💾 Saved to: {Config.DIM_STORE.name}")
    print()
    
    # Dim_Vendor
    dim_vendor = create_dim_vendor(purchases_df)
    dim_vendor.to_csv(Config.DIM_VENDOR, index=False)
    print(f"   💾 Saved to: {Config.DIM_VENDOR.name}")
    print()
    
    # ========================================================================
    # STEP 3: CREATE FACT TABLES
    # ========================================================================
    print("STEP 3: Creating Fact Tables")
    print("-" * 80)
    
    # Fact_Sales
    if not sales_df.empty:
        fact_sales = create_fact_sales(sales_df, dim_product, dim_store, dim_date)
        fact_sales.to_csv(Config.FACT_SALES, index=False)
        print(f"   💾 Saved to: {Config.FACT_SALES.name}")
        print()
    
    # Fact_Purchases
    if not purchases_df.empty:
        fact_purchases = create_fact_purchases(purchases_df, invoice_df, dim_product, dim_vendor, dim_date)
        fact_purchases.to_csv(Config.FACT_PURCHASES, index=False)
        print(f"   💾 Saved to: {Config.FACT_PURCHASES.name}")
        print()
    
    # Fact_Inventory_Snapshot
    if not begin_inv_df.empty and not end_inv_df.empty:
        fact_inventory = create_fact_inventory_snapshot(begin_inv_df, end_inv_df, dim_product, dim_store, dim_date)
        fact_inventory.to_csv(Config.FACT_INVENTORY, index=False)
        print(f"   💾 Saved to: {Config.FACT_INVENTORY.name}")
        print()
    
    # ========================================================================
    # STEP 4: SUMMARY
    # ========================================================================
    print("="*80)
    print("✅ DATA MODEL CREATION COMPLETE!")
    print("="*80)
    print()
    print("📊 SUMMARY:")
    print(f"   Dimension Tables: 4")
    print(f"   Fact Tables: 3")
    print(f"   Total Files Created: 7")
    print(f"   Output Location: {Config.OUTPUT_DIR}")
    print()
    print("🔗 NEXT STEPS:")
    print("   1. Validate data quality and referential integrity")
    print("   2. Enrich dimensions with additional attributes (ABC/XYZ, Kraljic)")
    print("   3. Load into Power BI or analytical database")
    print("   4. Build reports and dashboards")
    print()
    print("="*80)


if __name__ == "__main__":
    main()
