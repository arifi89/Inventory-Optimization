"""
================================================================================
VALIDATE DATA MODEL - Data Quality & Integrity Checks
================================================================================
Purpose: Validate the star schema data model for quality and integrity
Author: System
Date: January 24, 2026
Version: 1.0

This script performs comprehensive validation:
- Data quality checks (nulls, duplicates, outliers)
- Referential integrity (foreign key validation)
- Business rule validation
- Summary statistics

REUSABLE FOR ANY COMPANY
================================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for validation"""
    
    BASE_DIR = Path(__file__).parent.parent
    MODEL_DIR = BASE_DIR / 'data' / 'data_model'
    REPORT_DIR = BASE_DIR / 'reports'
    
    # Model files
    FACT_SALES = MODEL_DIR / 'fact_sales.csv'
    FACT_PURCHASES = MODEL_DIR / 'fact_purchases.csv'
    FACT_INVENTORY = MODEL_DIR / 'fact_inventory_snapshot.csv'
    DIM_PRODUCT = MODEL_DIR / 'dim_product.csv'
    DIM_STORE = MODEL_DIR / 'dim_store.csv'
    DIM_VENDOR = MODEL_DIR / 'dim_vendor.csv'
    DIM_DATE = MODEL_DIR / 'dim_date.csv'


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_nulls(df, table_name, critical_columns):
    """Check for null values in critical columns"""
    print(f"\n   🔍 Checking nulls in {table_name}...")
    
    issues = []
    for col in critical_columns:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                pct = (null_count / len(df)) * 100
                issues.append(f"      ❌ {col}: {null_count:,} nulls ({pct:.2f}%)")
        else:
            issues.append(f"      ⚠️  {col}: Column not found")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"      ✅ No nulls in critical columns")
        return True


def check_duplicates(df, table_name, key_column):
    """Check for duplicate keys"""
    print(f"\n   🔍 Checking duplicates in {table_name}...")
    
    if key_column not in df.columns:
        print(f"      ⚠️  Key column '{key_column}' not found")
        return False
    
    dup_count = df[key_column].duplicated().sum()
    if dup_count > 0:
        print(f"      ❌ Found {dup_count:,} duplicate keys")
        return False
    else:
        print(f"      ✅ No duplicates found")
        return True


def check_referential_integrity(fact_df, dim_df, fact_fk, dim_pk, fact_name, dim_name):
    """Check foreign key integrity"""
    print(f"\n   🔗 Checking {fact_name}.{fact_fk} → {dim_name}.{dim_pk}...")
    
    if fact_fk not in fact_df.columns:
        print(f"      ⚠️  Foreign key '{fact_fk}' not found in {fact_name}")
        return False
    
    if dim_pk not in dim_df.columns:
        print(f"      ⚠️  Primary key '{dim_pk}' not found in {dim_name}")
        return False
    
    # Find orphaned records
    orphans = ~fact_df[fact_fk].isin(dim_df[dim_pk])
    orphan_count = orphans.sum()
    
    if orphan_count > 0:
        pct = (orphan_count / len(fact_df)) * 100
        print(f"      ❌ Found {orphan_count:,} orphaned records ({pct:.2f}%)")
        return False
    else:
        print(f"      ✅ All foreign keys valid")
        return True


def check_business_rules(df, table_name, rules):
    """Check business rules"""
    print(f"\n   📏 Checking business rules for {table_name}...")
    
    issues = []
    for rule_name, rule_func in rules.items():
        try:
            violations = rule_func(df)
            if violations > 0:
                issues.append(f"      ❌ {rule_name}: {violations:,} violations")
        except Exception as e:
            issues.append(f"      ⚠️  {rule_name}: Error - {e}")
    
    if issues:
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"      ✅ All business rules passed")
        return True


def generate_summary_stats(df, table_name):
    """Generate summary statistics"""
    stats = {
        'Table': table_name,
        'Row Count': f"{len(df):,}",
        'Column Count': len(df.columns),
        'Memory Usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
    }
    
    # Add numeric column stats
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        stats['Numeric Columns'] = len(numeric_cols)
    
    return stats


# ============================================================================
# MAIN VALIDATION
# ============================================================================

def main():
    """Main validation function"""
    
    print("="*80)
    print("🔍 DATA MODEL VALIDATION")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    validation_results = {}
    all_passed = True
    
    # ========================================================================
    # LOAD DATA
    # ========================================================================
    print("STEP 1: Loading Data Model")
    print("-" * 80)
    
    try:
        dim_date = pd.read_csv(Config.DIM_DATE)
        print(f"   ✅ Loaded Dim_Date: {len(dim_date):,} rows")
    except Exception as e:
        print(f"   ❌ Failed to load Dim_Date: {e}")
        return
    
    try:
        dim_product = pd.read_csv(Config.DIM_PRODUCT)
        print(f"   ✅ Loaded Dim_Product: {len(dim_product):,} rows")
    except Exception as e:
        print(f"   ❌ Failed to load Dim_Product: {e}")
        return
    
    try:
        dim_store = pd.read_csv(Config.DIM_STORE)
        print(f"   ✅ Loaded Dim_Store: {len(dim_store):,} rows")
    except Exception as e:
        print(f"   ❌ Failed to load Dim_Store: {e}")
        return
    
    try:
        dim_vendor = pd.read_csv(Config.DIM_VENDOR)
        print(f"   ✅ Loaded Dim_Vendor: {len(dim_vendor):,} rows")
    except Exception as e:
        print(f"   ❌ Failed to load Dim_Vendor: {e}")
        return
    
    try:
        fact_sales = pd.read_csv(Config.FACT_SALES)
        print(f"   ✅ Loaded Fact_Sales: {len(fact_sales):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load Fact_Sales: {e}")
        fact_sales = pd.DataFrame()
    
    try:
        fact_purchases = pd.read_csv(Config.FACT_PURCHASES)
        print(f"   ✅ Loaded Fact_Purchases: {len(fact_purchases):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load Fact_Purchases: {e}")
        fact_purchases = pd.DataFrame()
    
    try:
        fact_inventory = pd.read_csv(Config.FACT_INVENTORY)
        print(f"   ✅ Loaded Fact_Inventory_Snapshot: {len(fact_inventory):,} rows")
    except Exception as e:
        print(f"   ⚠️  Could not load Fact_Inventory_Snapshot: {e}")
        fact_inventory = pd.DataFrame()
    
    print()
    
    # ========================================================================
    # DIMENSION TABLE VALIDATION
    # ========================================================================
    print("STEP 2: Validating Dimension Tables")
    print("-" * 80)
    
    # Dim_Date
    print("\n📅 Validating Dim_Date")
    validation_results['Dim_Date'] = []
    validation_results['Dim_Date'].append(
        check_nulls(dim_date, 'Dim_Date', ['date_key', 'full_date', 'year', 'month'])
    )
    validation_results['Dim_Date'].append(
        check_duplicates(dim_date, 'Dim_Date', 'date_key')
    )
    
    # Dim_Product
    print("\n📦 Validating Dim_Product")
    validation_results['Dim_Product'] = []
    validation_results['Dim_Product'].append(
        check_nulls(dim_product, 'Dim_Product', ['product_key', 'brand_code', 'description'])
    )
    validation_results['Dim_Product'].append(
        check_duplicates(dim_product, 'Dim_Product', 'product_key')
    )
    
    # Dim_Store
    print("\n🏪 Validating Dim_Store")
    validation_results['Dim_Store'] = []
    validation_results['Dim_Store'].append(
        check_nulls(dim_store, 'Dim_Store', ['store_key', 'store_name'])
    )
    validation_results['Dim_Store'].append(
        check_duplicates(dim_store, 'Dim_Store', 'store_key')
    )
    
    # Dim_Vendor
    print("\n🏭 Validating Dim_Vendor")
    validation_results['Dim_Vendor'] = []
    validation_results['Dim_Vendor'].append(
        check_nulls(dim_vendor, 'Dim_Vendor', ['vendor_key', 'vendor_name'])
    )
    validation_results['Dim_Vendor'].append(
        check_duplicates(dim_vendor, 'Dim_Vendor', 'vendor_key')
    )
    
    print()
    
    # ========================================================================
    # FACT TABLE VALIDATION
    # ========================================================================
    print("STEP 3: Validating Fact Tables")
    print("-" * 80)
    
    # Fact_Sales
    if not fact_sales.empty:
        print("\n💰 Validating Fact_Sales")
        validation_results['Fact_Sales'] = []
        validation_results['Fact_Sales'].append(
            check_nulls(fact_sales, 'Fact_Sales', ['sale_id', 'date_key', 'product_key', 'store_key'])
        )
        validation_results['Fact_Sales'].append(
            check_duplicates(fact_sales, 'Fact_Sales', 'sale_id')
        )
        
        # Business rules for Fact_Sales
        sales_rules = {
            'Quantity > 0': lambda df: (df['quantity_sold'] <= 0).sum() if 'quantity_sold' in df.columns else 0,
            'Price > 0': lambda df: (df['sales_price'] <= 0).sum() if 'sales_price' in df.columns else 0,
            'Amount = Qty × Price': lambda df: (
                abs(df['sales_amount'] - (df['quantity_sold'] * df['sales_price'])) > 0.01
            ).sum() if all(c in df.columns for c in ['sales_amount', 'quantity_sold', 'sales_price']) else 0
        }
        validation_results['Fact_Sales'].append(
            check_business_rules(fact_sales, 'Fact_Sales', sales_rules)
        )
    
    # Fact_Purchases
    if not fact_purchases.empty:
        print("\n🛒 Validating Fact_Purchases")
        validation_results['Fact_Purchases'] = []
        validation_results['Fact_Purchases'].append(
            check_nulls(fact_purchases, 'Fact_Purchases', ['purchase_id', 'date_key', 'product_key', 'vendor_key'])
        )
        validation_results['Fact_Purchases'].append(
            check_duplicates(fact_purchases, 'Fact_Purchases', 'purchase_id')
        )
    
    # Fact_Inventory_Snapshot
    if not fact_inventory.empty:
        print("\n📊 Validating Fact_Inventory_Snapshot")
        validation_results['Fact_Inventory'] = []
        validation_results['Fact_Inventory'].append(
            check_nulls(fact_inventory, 'Fact_Inventory_Snapshot', ['snapshot_id', 'date_key', 'product_key', 'store_key'])
        )
        validation_results['Fact_Inventory'].append(
            check_duplicates(fact_inventory, 'Fact_Inventory_Snapshot', 'snapshot_id')
        )
    
    print()
    
    # ========================================================================
    # REFERENTIAL INTEGRITY
    # ========================================================================
    print("STEP 4: Validating Referential Integrity")
    print("-" * 80)
    
    if not fact_sales.empty:
        check_referential_integrity(fact_sales, dim_date, 'date_key', 'date_key', 
                                   'Fact_Sales', 'Dim_Date')
        check_referential_integrity(fact_sales, dim_product, 'product_key', 'product_key',
                                   'Fact_Sales', 'Dim_Product')
        check_referential_integrity(fact_sales, dim_store, 'store_key', 'store_key',
                                   'Fact_Sales', 'Dim_Store')
    
    if not fact_purchases.empty:
        check_referential_integrity(fact_purchases, dim_date, 'date_key', 'date_key',
                                   'Fact_Purchases', 'Dim_Date')
        check_referential_integrity(fact_purchases, dim_product, 'product_key', 'product_key',
                                   'Fact_Purchases', 'Dim_Product')
        check_referential_integrity(fact_purchases, dim_vendor, 'vendor_key', 'vendor_key',
                                   'Fact_Purchases', 'Dim_Vendor')
    
    if not fact_inventory.empty:
        check_referential_integrity(fact_inventory, dim_date, 'date_key', 'date_key',
                                   'Fact_Inventory_Snapshot', 'Dim_Date')
        check_referential_integrity(fact_inventory, dim_product, 'product_key', 'product_key',
                                   'Fact_Inventory_Snapshot', 'Dim_Product')
        check_referential_integrity(fact_inventory, dim_store, 'store_key', 'store_key',
                                   'Fact_Inventory_Snapshot', 'Dim_Store')
    
    print()
    
    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    print("STEP 5: Summary Statistics")
    print("-" * 80)
    print()
    
    summary_data = []
    summary_data.append(generate_summary_stats(dim_date, 'Dim_Date'))
    summary_data.append(generate_summary_stats(dim_product, 'Dim_Product'))
    summary_data.append(generate_summary_stats(dim_store, 'Dim_Store'))
    summary_data.append(generate_summary_stats(dim_vendor, 'Dim_Vendor'))
    
    if not fact_sales.empty:
        summary_data.append(generate_summary_stats(fact_sales, 'Fact_Sales'))
    if not fact_purchases.empty:
        summary_data.append(generate_summary_stats(fact_purchases, 'Fact_Purchases'))
    if not fact_inventory.empty:
        summary_data.append(generate_summary_stats(fact_inventory, 'Fact_Inventory_Snapshot'))
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    print()
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print("="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    
    for table, results in validation_results.items():
        passed = sum(results)
        total = len(results)
        status = "✅ PASS" if passed == total else "❌ FAIL"
        print(f"{status} {table}: {passed}/{total} checks passed")
    
    print()
    
    overall_pass = all(all(results) for results in validation_results.values())
    if overall_pass:
        print("✅ ALL VALIDATIONS PASSED - Data model is ready for use!")
    else:
        print("⚠️  SOME VALIDATIONS FAILED - Review issues above")
    
    print("="*80)


if __name__ == "__main__":
    main()
