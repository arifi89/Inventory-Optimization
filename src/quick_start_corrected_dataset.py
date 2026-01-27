"""
================================================================================
INVENTORY OPTIMIZATION - QUICK START GUIDE
================================================================================

AUTHOR: Mohamed Osman
DATE: January 2026
GITHUB: https://github.com/arifi89
LINKEDIN: https://www.linkedin.com/in/mohamed-osman-123456789/

================================================================================
PURPOSE:
    Provide a quick start guide for loading and working with the corrected
    Master Dataset. Shows common patterns and usage examples.
    
================================================================================
OBJECTIVES:
    ✓ Demonstrate how to load Master_Dataset
    ✓ Show basic data exploration methods
    ✓ Illustrate common analysis patterns
    ✓ Provide code templates for analysis
    ✓ Help users get started quickly

================================================================================
CONTENTS:
    1. Loading the Master Dataset
    2. Basic Data Exploration
    3. Revenue Analysis
    4. Cost and Profit Analysis
    5. Inventory Analysis
    6. Store/Product Analysis
    7. Time Series Analysis
    
================================================================================
KEY EXAMPLES:
    - Filter and aggregate by store, product, time period
    - Calculate summary statistics
    - Create pivot tables for analysis
    - Export results for further analysis
    
================================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load the corrected dataset
DATA_MODEL_DIR = Path('data/data_model')
df = pd.read_parquet(DATA_MODEL_DIR / 'master_dataset_corrected.parquet')

print('='*100)
print('CORRECTED MASTER DATASET - QUICK START GUIDE')
print('='*100)
print()

# ============================================================================
# Basic Info
# ============================================================================
print('1. BASIC INFORMATION')
print('-'*100)
print(f'Shape: {df.shape[0]:,} rows × {df.shape[1]} columns')
print(f'Date Range: {df["Sales_Date"].min()} to {df["Sales_Date"].max()}')
print(f'Memory Usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB')
print()

# ============================================================================
# Column Groups
# ============================================================================
print('2. COLUMN REFERENCE')
print('-'*100)
print()

print('Transaction Identifiers:')
print('  - Sales_Order, Sales_Date')
print()

print('Product Information:')
print('  - Product_Number (Primary Key)')
print('  - ABC_Class, XYZ_Class, ABC_XYZ_Segment (if available)')
print()

print('Store Information:')
print('  - Store, Store_City, Store_State, Store_Region')
print()

print('Sales Metrics:')
print('  - Sales_Quantity, Sales_Price, Revenue, Tax')
print()

print('Cost Metrics (WAC-based with Freight):')
print('  - WAC: Weighted Average Cost per unit (product cost only)')
print('  - Freight_per_Unit: Average freight cost per unit')
print('  - Purchase_Cost: Sales_Quantity × WAC')
print('  - Freight_Cost: Sales_Quantity × Freight_per_Unit')
print('  - Landed_Cost: WAC + Freight_per_Unit')
print('  - COGS: Purchase_Cost + Freight_Cost')
print()

print('Profit Metrics:')
print('  - Gross_Profit: Revenue - Purchase_Cost')
print('  - Margin_Percent: (Gross_Profit / Revenue) × 100')
print()

print('Inventory Metrics:')
print('  - On_Hand_Quantity: Inventory before the sale')
print('  - Inventory_Value: Value of inventory')
print('  - Snapshot_Date: Date of the inventory snapshot')
print()

# ============================================================================
# Example Queries
# ============================================================================
print('3. EXAMPLE QUERIES')
print('-'*100)
print()

# Example 1: Top 10 products by revenue
print('Example 1: Top 10 Products by Revenue')
top_products = df.groupby('Product_Number')['Revenue'].sum().sort_values(ascending=False).head(10)
print(top_products)
print()

# Example 2: Average margin by store
print('Example 2: Average Margin by Store')
store_margins = df.groupby('Store')['Margin_Percent'].mean().sort_values(ascending=False).head(10)
print(store_margins)
print()

# Example 3: Products with highest margins
print('Example 3: Products with Highest Average Margin')
product_margins = df.groupby('Product_Number').agg({
    'Margin_Percent': 'mean',
    'Revenue': 'sum',
    'Sales_Quantity': 'sum'
}).sort_values('Margin_Percent', ascending=False).head(10)
print(product_margins)
print()

# ============================================================================
# Key Calculations
# ============================================================================
print('4. KEY CALCULATIONS YOU CAN PERFORM')
print('-'*100)
print()

print('Revenue Analysis:')
print('  df.groupby("Store")["Revenue"].sum()')
print('  df.groupby("Product_Number")["Revenue"].sum()')
print('  df.groupby(df["Sales_Date"].dt.to_period("M"))["Revenue"].sum()')
print()

print('Margin Analysis:')
print('  df.groupby("Product_Number")["Margin_Percent"].mean()')
print('  df.groupby("ABC_XYZ_Segment")["Margin_Percent"].mean()')
print()

print('Inventory Analysis:')
print('  df.groupby("Product_Number")["On_Hand_Quantity"].mean()')
print('  # Stock-to-Sales Ratio:')
print('  df["Stock_to_Sales"] = df["On_Hand_Quantity"] / df["Sales_Quantity"]')
print()

print('Cost Analysis:')
print('  df.groupby("Product_Number")["WAC"].mean()')
print('  df.groupby("Product_Number")["Freight_per_Unit"].mean()')
print('  df.groupby("Product_Number")["Landed_Cost"].mean()')
print('  df.groupby("Product_Number")["COGS"].sum()')
print()

# ============================================================================
# Important Notes
# ============================================================================
print('5. IMPORTANT NOTES')
print('-'*100)
print()

print('✅ WAC (Weighted Average Cost):')
print('   - Calculated across ALL purchase history for each product')
print('   - NOT linked to specific purchase orders')
print('   - This is the correct retail costing method')
print()

print('✅ Freight Cost:')
print('   - Averaged per unit from all purchase history')
print('   - Included in Landed_Cost and COGS')
print('   - Provides true total cost per unit')
print()

print('✅ Tax:')
print('   - Included from sales transactions')
print('   - Used for calculating Net_Revenue')
print()

print('✅ Inventory Matching:')
print('   - Uses nearest PRIOR snapshot before each sale')
print('   - NOT exact date matching')
print('   - Shows inventory level BEFORE the sale occurred')
print()

print('✅ Margin Calculation:')
print('   - Based on WAC, not individual PO prices')
print('   - Realistic margins (typically 20-40% for retail)')
print('   - NO artificial 100% margins')
print()

print('⚠️  Handling NULL Values:')
print('   - WAC may be NULL for products never purchased')
print('   - Inventory may be NULL if no prior snapshot exists')
print('   - Use .notna() to filter for records with data')
print()

# ============================================================================
# Sample Analysis
# ============================================================================
print('6. SAMPLE ANALYSIS: Overall Business Metrics')
print('-'*100)
print()

total_revenue = df['Revenue'].sum()
total_cogs = df['COGS'].sum()
total_profit = df['Gross_Profit'].sum()
overall_margin = (total_profit / total_revenue * 100)

print(f'Total Revenue:      ${total_revenue:,.2f}')
print(f'Total COGS:         ${total_cogs:,.2f}')
print(f'Total Gross Profit: ${total_profit:,.2f}')
print(f'Overall Margin:     {overall_margin:.2f}%')
print()

print(f'Total Transactions: {len(df):,}')
print(f'Unique Products:    {df["Product_Number"].nunique():,}')
print(f'Unique Stores:      {df["Store"].nunique():,}')
print(f'Average Sale Value: ${df["Revenue"].mean():.2f}')
print(f'Average Margin:     {df["Margin_Percent"].mean():.2f}%')
print()

# ============================================================================
# Export for Further Analysis
# ============================================================================
print('7. EXPORT OPTIONS')
print('-'*100)
print()

print('# Export to Excel for specific analysis:')
print('df.to_excel("my_analysis.xlsx", index=False)')
print()

print('# Export filtered data:')
print('high_margin = df[df["Margin_Percent"] > 40]')
print('high_margin.to_csv("high_margin_products.csv", index=False)')
print()

print('# Export aggregated data:')
print('product_summary = df.groupby("Product_Number").agg({')
print('    "Revenue": "sum",')
print('    "Gross_Profit": "sum",')
print('    "Margin_Percent": "mean"')
print('})')
print('product_summary.to_csv("product_summary.csv")')
print()

print('='*100)
print('✅ Ready to use! Load the dataset and start your analysis.')
print('='*100)
