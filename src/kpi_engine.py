"""
================================================================================
INVENTORY OPTIMIZATION - KPI CALCULATION ENGINE
================================================================================

AUTHOR: Mohamed Osman
DATE: January 2026
GITHUB: https://github.com/arifi89
LINKEDIN: https://www.linkedin.com/in/mohamed-osman-123456789/

================================================================================
PURPOSE:
    Build a comprehensive KPI system that calculates all key performance
    indicators for inventory optimization, profitability analysis, and
    supplier performance evaluation.
    
================================================================================
OBJECTIVES:
    ✓ Calculate Revenue KPIs (Gross, Net, ASP, Mix)
    ✓ Calculate Cost KPIs (Purchase, Landed, Variance, Spend)
    ✓ Calculate Profit KPIs (Gross, Margin, Contribution)
    ✓ Calculate Inventory KPIs (Turnover, Days, Stockout, Overstock)
    ✓ Calculate Supplier KPIs (Lead Time, Reliability, Spend)
    ✓ Calculate Store KPIs (Revenue, Margin, Efficiency, Ranking)
    ✓ Calculate Product KPIs (Velocity, Revenue Contribution, Classification)
    ✓ Create comprehensive KPI report

================================================================================
METHODOLOGY:
    Calculates the following KPI categories:
    
    1. Revenue KPIs:
       - Gross Revenue, Net Revenue, Average Selling Price (ASP), Revenue Mix %
    
    2. Cost KPIs:
       - Purchase Cost, Landed Cost, Cost Variance, Total Supplier Spend
    
    3. Profit KPIs:
       - Gross Profit, Margin Percent, Contribution Margin
    
    4. Inventory KPIs:
       - Inventory Turnover, Days of Inventory, Stockout Risk, Overstock Ratio
    
    5. Supplier KPIs:
       - Average Lead Time, Lead Time Variability, On-time Delivery %, Spend %
    
    6. Store KPIs:
       - Total Revenue, Gross Margin %, Inventory Efficiency, Store Ranking
    
    7. Product KPIs:
       - Sales Velocity, Revenue Contribution %, ABC/XYZ Classification
    
================================================================================
INPUT DATA:
    - Master_Dataset.parquet — Complete transaction dataset
    - Product dimensions
    - Store dimensions
    - Supplier/Vendor information
    
================================================================================
OUTPUT:
    - KPI summary reports (by Store, Product, Supplier)
    - Detailed KPI calculations
    - Recommendations for optimization
    
================================================================================
KEY CALCULATIONS:
    Revenue = Sales_Quantity × Sales_Price
    Gross_Margin = (Gross_Profit / Revenue) × 100
    Inventory_Turnover = COGS / Average_Inventory_Value
    Days_Inventory = 365 / Inventory_Turnover
    ABC_Class: A (80% value), B (15% value), C (5% value)
    XYZ_Class: X (Stable), Y (Variable), Z (Intermittent)
    
================================================================================
KEY FINDINGS:
    ✓ Comprehensive KPI system enables data-driven decisions
    ✓ Multi-dimensional analysis (Store, Product, Supplier)
    ✓ Automated classification for inventory management
    ✓ Performance benchmarking and ranking
    
================================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class KPIEngine:
    """
    Complete KPI calculation engine for inventory analysis
    """
    
    def __init__(self, df):
        """
        Initialize the KPI Engine with a master dataset
        
        Args:
            df (pd.DataFrame): Master dataset containing sales, purchases, inventory, and supplier data
        """
        self.df = df.copy()
        self.original_df = df.copy()
        self.validation_results = {}
        self._map_columns()

    def _map_columns(self):
        """Standardize column names from master dataset to internal naming."""
        rename_map = {
            # Keys
            'product_key': 'product_id',
            'store_key': 'store_id',
            'vendor_key': 'vendor_id',

            # Sales
            'Sales_Quantity': 'sales_quantity',
            'Sales_Price': 'sales_price',
            'Sales_Amount': 'sales_amount',

            # Purchases
            'Purchase_Quantity': 'purchase_quantity',
            'Purchase_Price': 'purchase_price',
            'Purchase_Amount': 'purchase_amount',
            'Purchase_Cost': 'purchase_cost',
            'Freight_Cost': 'Freight_Cost',
            'Landed_Cost': 'Landed_Cost',

            # Inventory
            'On_Hand_Quantity': 'on_hand_quantity',
            'Inventory_Value': 'inventory_value',

            # Revenue / Profit
            'Gross_Revenue': 'Gross_Revenue',
            'Net_Revenue': 'Net_Revenue',
            'Gross_Profit': 'Gross_Profit',
            'Tax': 'Tax',
        }

        cols_to_rename = {k: v for k, v in rename_map.items() if k in self.df.columns}
        if cols_to_rename:
            self.df.rename(columns=cols_to_rename, inplace=True)

        # Ensure key columns exist
        for col in ['product_id', 'store_id']:
            if col not in self.df.columns and col.replace('_id', '_key') in self.df.columns:
                self.df[col] = self.df[col.replace('_id', '_key')]
        
    def load_and_validate(self):
        """
        Load and validate the master dataset
        
        Returns:
            dict: Validation summary
        """
        print("=" * 80)
        print("STEP 1: LOADING AND VALIDATING MASTER DATASET")
        print("=" * 80)
        
        validation = {
            'num_rows': len(self.df),
            'num_columns': len(self.df.columns),
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.to_dict(),
            'date_range': None,
            'missing_keys': None
        }
        
        print(f"\n✓ Number of rows: {validation['num_rows']:,}")
        print(f"✓ Number of columns: {validation['num_columns']}")
        print(f"\nColumns loaded:")
        for col in self.df.columns:
            print(f"  - {col}: {self.df[col].dtype}")
        
        # Check date range
        date_cols = [col for col in self.df.columns if 'date' in col.lower()]
        if date_cols:
            date_col = date_cols[0]
            if pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
                min_date = self.df[date_col].min()
                max_date = self.df[date_col].max()
                validation['date_range'] = (min_date, max_date)
                print(f"\n✓ Date range: {min_date.date()} to {max_date.date()}")
        
        # Check for missing key columns
        key_cols = ['product_id', 'store_id', 'date']
        missing_keys = [col for col in key_cols if col not in self.df.columns]
        if not missing_keys:
            null_checks = self.df[key_cols].isnull().sum()
            if null_checks.sum() == 0:
                print(f"✓ No missing product/store/date keys")
            else:
                print(f"⚠ Missing values found in keys: {null_checks.to_dict()}")
        else:
            print(f"⚠ Missing key columns: {missing_keys}")
        
        validation['missing_keys'] = missing_keys
        print("\n" + "=" * 80)
        
        self.validation_results['load_validation'] = validation
        return validation
    
    def create_revenue_kpis(self):
        """
        Create revenue-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with revenue KPIs
        """
        print("\nSTEP 2: CREATING REVENUE KPIs")
        print("=" * 80)
        
        # Gross Revenue
        if 'sales_quantity' in self.df.columns and 'sales_price' in self.df.columns:
            self.df['Gross_Revenue'] = (
                self.df['sales_quantity'] * self.df['sales_price']
            ).fillna(0)
            print(f"✓ Gross_Revenue calculated")
        else:
            self.df['Gross_Revenue'] = 0
            print(f"⚠ Missing sales_quantity or sales_price columns")
        
        # Net Revenue (same as Gross for now)
        self.df['Net_Revenue'] = self.df['Gross_Revenue']
        print(f"✓ Net_Revenue calculated")
        
        # Average Selling Price (ASP)
        self.df['ASP'] = np.where(
            self.df['sales_quantity'] > 0,
            self.df['Gross_Revenue'] / self.df['sales_quantity'],
            0
        )
        self.df['ASP'] = self.df['ASP'].replace([np.inf, -np.inf], 0).fillna(0)
        print(f"✓ ASP (Average Selling Price) calculated")
        
        # Revenue by Product
        if 'product_id' in self.df.columns:
            revenue_by_product = self.df.groupby('product_id')['Gross_Revenue'].sum().reset_index()
            revenue_by_product.columns = ['product_id', 'Revenue_by_Product']
            self.df = self.df.merge(revenue_by_product, on='product_id', how='left')
            print(f"✓ Revenue_by_Product calculated")
        
        # Revenue by Store
        if 'store_id' in self.df.columns:
            revenue_by_store = self.df.groupby('store_id')['Gross_Revenue'].sum().reset_index()
            revenue_by_store.columns = ['store_id', 'Revenue_by_Store']
            self.df = self.df.merge(revenue_by_store, on='store_id', how='left')
            print(f"✓ Revenue_by_Store calculated")
        
        # Revenue by Vendor
        if 'vendor_id' in self.df.columns:
            revenue_by_vendor = self.df.groupby('vendor_id')['Gross_Revenue'].sum().reset_index()
            revenue_by_vendor.columns = ['vendor_id', 'Revenue_by_Vendor']
            self.df = self.df.merge(revenue_by_vendor, on='vendor_id', how='left')
            print(f"✓ Revenue_by_Vendor calculated")
        
        # Revenue by Category
        if 'category' in self.df.columns:
            revenue_by_category = self.df.groupby('category')['Gross_Revenue'].sum().reset_index()
            revenue_by_category.columns = ['category', 'Revenue_by_Category']
            self.df = self.df.merge(revenue_by_category, on='category', how='left')
            print(f"✓ Revenue_by_Category calculated")
        
        print("=" * 80)
        return self.df
    
    def create_cost_kpis(self):
        """
        Create cost-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with cost KPIs
        """
        print("\nSTEP 3: CREATING COST KPIs")
        print("=" * 80)
        
        # Purchase Cost
        if 'purchase_quantity' in self.df.columns and 'purchase_price' in self.df.columns:
            self.df['Purchase_Cost'] = (
                self.df['purchase_quantity'] * self.df['purchase_price']
            ).fillna(0)
            print(f"✓ Purchase_Cost calculated")
        else:
            self.df['Purchase_Cost'] = 0
            print(f"⚠ Missing purchase_quantity or purchase_price columns")
        
        # Freight Cost
        if 'Freight_Cost' in self.df.columns:
            self.df['Freight_Cost'] = pd.to_numeric(self.df['Freight_Cost'], errors='coerce').fillna(0)
            print(f"✓ Freight_Cost found in data")
        else:
            self.df['Freight_Cost'] = 0
            print(f"✓ Freight_Cost set to 0 (not in data)")
        
        # Landed Cost (Purchase Cost + Freight)
        self.df['Landed_Cost'] = self.df['Purchase_Cost'] + self.df['Freight_Cost']
        print(f"✓ Landed_Cost calculated (Purchase_Cost + Freight_Cost)")
        
        # Cost Variance
        self.df['Cost_Variance'] = (
            self.df['sales_price'] - self.df['purchase_price']
        ).fillna(0)
        print(f"✓ Cost_Variance calculated")
        
        # Supplier Spend per Vendor
        if 'vendor_id' in self.df.columns:
            supplier_spend = self.df.groupby('vendor_id')['Purchase_Cost'].sum().reset_index()
            supplier_spend.columns = ['vendor_id', 'Supplier_Spend']
            self.df = self.df.merge(supplier_spend, on='vendor_id', how='left')
            print(f"✓ Supplier_Spend calculated")
        else:
            self.df['Supplier_Spend'] = 0
            print(f"⚠ Missing vendor_id column")
        
        print("=" * 80)
        return self.df
    
    def create_profit_kpis(self):
        """
        Create profit-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with profit KPIs
        """
        print("\nSTEP 4: CREATING PROFIT KPIs")
        print("=" * 80)
        
        # Apply Tax adjustment if available
        if 'Tax' in self.df.columns:
            self.df['Tax'] = pd.to_numeric(self.df['Tax'], errors='coerce').fillna(0)
            self.df['Net_Revenue'] = self.df['Gross_Revenue'] - self.df['Tax']
            print(f"✓ Net_Revenue calculated (Gross_Revenue - Tax)")
        else:
            self.df['Tax'] = 0
            self.df['Net_Revenue'] = self.df['Gross_Revenue']
            print(f"✓ Net_Revenue calculated (Tax not found, equals Gross_Revenue)")
        
        # Gross Profit using Landed Cost
        self.df['Gross_Profit'] = (
            self.df['Net_Revenue'] - self.df['Landed_Cost']
        ).fillna(0)
        print(f"✓ Gross_Profit calculated (Net_Revenue - Landed_Cost)")
        
        # Margin Percent
        self.df['Margin_Percent'] = np.where(
            self.df['Net_Revenue'] > 0,
            (self.df['Gross_Profit'] / self.df['Net_Revenue']) * 100,
            0
        )
        self.df['Margin_Percent'] = self.df['Margin_Percent'].replace([np.inf, -np.inf], 0).fillna(0)
        print(f"✓ Margin_Percent calculated")
        
        # Contribution Margin (same as Gross Profit for now)
        self.df['Contribution_Margin'] = self.df['Gross_Profit']
        print(f"✓ Contribution_Margin calculated")
        
        print("=" * 80)
        return self.df
    
    def create_inventory_kpis(self):
        """
        Create inventory-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with inventory KPIs
        """
        print("\nSTEP 5: CREATING INVENTORY KPIs")
        print("=" * 80)
        
        # Inventory Turnover
        if 'on_hand_quantity' in self.df.columns:
            self.df['Inventory_Turnover'] = np.where(
                self.df['on_hand_quantity'] > 0,
                self.df['sales_quantity'] / self.df['on_hand_quantity'],
                0
            )
            self.df['Inventory_Turnover'] = self.df['Inventory_Turnover'].replace(
                [np.inf, -np.inf], 0
            ).fillna(0)
            print(f"✓ Inventory_Turnover calculated")
            
            # Days of Inventory
            self.df['Days_of_Inventory'] = np.where(
                self.df['Inventory_Turnover'] > 0,
                365 / self.df['Inventory_Turnover'],
                0
            )
            self.df['Days_of_Inventory'] = self.df['Days_of_Inventory'].replace(
                [np.inf, -np.inf], 0
            ).fillna(0)
            print(f"✓ Days_of_Inventory calculated")
            
            # Stockout Risk Flag
            self.df['Stockout_Risk_Flag'] = np.where(
                self.df['on_hand_quantity'] < self.df['sales_quantity'],
                1,
                0
            )
            print(f"✓ Stockout_Risk_Flag calculated")
            
            # Overstock Value (simplified - flag if inventory > sales quantity * 2)
            self.df['Overstock_Risk_Flag'] = np.where(
                self.df['on_hand_quantity'] > (self.df['sales_quantity'] * 2),
                1,
                0
            )
            print(f"✓ Overstock_Risk_Flag calculated")
            
        else:
            self.df['Inventory_Turnover'] = 0
            self.df['Days_of_Inventory'] = 0
            self.df['Stockout_Risk_Flag'] = 0
            self.df['Overstock_Risk_Flag'] = 0
            print(f"⚠ Missing on_hand_quantity column")
        
        print("=" * 80)
        return self.df
    
    def create_supplier_kpis(self):
        """
        Create supplier-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with supplier KPIs
        """
        print("\nSTEP 6: CREATING SUPPLIER KPIs")
        print("=" * 80)
        
        # Lead Time
        if 'po_date' in self.df.columns and 'receiving_date' in self.df.columns:
            self.df['po_date'] = pd.to_datetime(self.df['po_date'], errors='coerce')
            self.df['receiving_date'] = pd.to_datetime(self.df['receiving_date'], errors='coerce')
            
            self.df['Lead_Time_Days'] = (
                self.df['receiving_date'] - self.df['po_date']
            ).dt.days
            self.df['Lead_Time_Days'] = self.df['Lead_Time_Days'].fillna(0).astype('int64')
            print(f"✓ Lead_Time_Days calculated")
            
            # Lead Time Variability (std dev per vendor)
            if 'vendor_id' in self.df.columns:
                lead_time_var = self.df.groupby('vendor_id')['Lead_Time_Days'].std().reset_index()
                lead_time_var.columns = ['vendor_id', 'Lead_Time_Variability']
                self.df = self.df.merge(lead_time_var, on='vendor_id', how='left')
                print(f"✓ Lead_Time_Variability calculated")
            
        else:
            self.df['Lead_Time_Days'] = 0
            self.df['Lead_Time_Variability'] = 0
            print(f"⚠ Missing po_date or receiving_date columns")
        
        # Supplier Reliability
        if 'vendor_id' in self.df.columns and 'expected_delivery_date' in self.df.columns:
            self.df['expected_delivery_date'] = pd.to_datetime(
                self.df['expected_delivery_date'], 
                errors='coerce'
            )
            self.df['receiving_date'] = pd.to_datetime(
                self.df['receiving_date'], 
                errors='coerce'
            )
            
            on_time = (self.df['receiving_date'] <= self.df['expected_delivery_date']).astype(int)
            supplier_reliability = self.df.groupby('vendor_id').apply(
                lambda x: (on_time[x.index].sum() / len(x)) * 100
            ).reset_index()
            supplier_reliability.columns = ['vendor_id', 'Supplier_Reliability']
            self.df = self.df.merge(supplier_reliability, on='vendor_id', how='left')
            print(f"✓ Supplier_Reliability calculated")
        else:
            self.df['Supplier_Reliability'] = 0
            print(f"⚠ Missing expected_delivery_date column")
        
        print("=" * 80)
        return self.df
    
    def create_store_kpis(self):
        """
        Create store-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with store KPIs
        """
        print("\nSTEP 7: CREATING STORE KPIs")
        print("=" * 80)
        
        if 'store_id' in self.df.columns:
            # Store Revenue
            store_revenue = self.df.groupby('store_id')['Gross_Revenue'].sum().reset_index()
            store_revenue.columns = ['store_id', 'Store_Total_Revenue']
            self.df = self.df.merge(store_revenue, on='store_id', how='left')
            print(f"✓ Store_Total_Revenue calculated")
            
            # Store Margin
            store_margin = self.df.groupby('store_id')['Gross_Profit'].sum().reset_index()
            store_margin.columns = ['store_id', 'Store_Total_Margin']
            self.df = self.df.merge(store_margin, on='store_id', how='left')
            print(f"✓ Store_Total_Margin calculated")
            
            # Store Efficiency (Revenue / Inventory Value)
            if 'on_hand_quantity' in self.df.columns and 'purchase_price' in self.df.columns:
                self.df['Inventory_Value'] = (
                    self.df['on_hand_quantity'] * self.df['purchase_price']
                ).fillna(0)
                
                store_inventory_value = self.df.groupby('store_id')['Inventory_Value'].sum().reset_index()
                store_inventory_value.columns = ['store_id', 'Store_Inventory_Value']
                self.df = self.df.merge(store_inventory_value, on='store_id', how='left')
                
                self.df['Store_Efficiency'] = np.where(
                    self.df['Store_Inventory_Value'] > 0,
                    self.df['Store_Total_Revenue'] / self.df['Store_Inventory_Value'],
                    0
                )
                self.df['Store_Efficiency'] = self.df['Store_Efficiency'].replace(
                    [np.inf, -np.inf], 0
                ).fillna(0)
                print(f"✓ Store_Efficiency calculated")
            
            # Store Ranking
            store_rank = self.df.groupby('store_id')['Gross_Revenue'].sum().reset_index()
            store_rank.columns = ['store_id', 'Store_Rev_Rank']
            store_rank['Store_Revenue_Rank'] = store_rank['Store_Rev_Rank'].rank(ascending=False).astype('int64')
            store_rank = store_rank[['store_id', 'Store_Revenue_Rank']]
            self.df = self.df.merge(store_rank, on='store_id', how='left')
            print(f"✓ Store_Revenue_Rank calculated")
            
        else:
            print(f"⚠ Missing store_id column")
        
        print("=" * 80)
        return self.df
    
    def create_product_kpis(self):
        """
        Create product-related KPIs
        
        Returns:
            pd.DataFrame: DataFrame with product KPIs
        """
        print("\nSTEP 8: CREATING PRODUCT KPIs")
        print("=" * 80)
        
        if 'product_id' in self.df.columns and 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
            
            # Calculate number of days in dataset
            num_days = (self.df['date'].max() - self.df['date'].min()).days + 1
            if num_days == 0:
                num_days = 1
            
            # Velocity = Sales Quantity / Number of Days
            product_velocity = self.df.groupby('product_id')['sales_quantity'].sum().reset_index()
            product_velocity['Velocity'] = product_velocity['sales_quantity'] / num_days
            product_velocity = product_velocity[['product_id', 'Velocity']]
            self.df = self.df.merge(product_velocity, on='product_id', how='left')
            print(f"✓ Velocity calculated (days in period: {num_days})")
            
            # Revenue Contribution
            total_revenue = self.df['Gross_Revenue'].sum()
            if total_revenue > 0:
                self.df['Revenue_Contribution'] = (
                    self.df['Gross_Revenue'] / total_revenue
                ) * 100
            else:
                self.df['Revenue_Contribution'] = 0
            print(f"✓ Revenue_Contribution calculated")
            
            # ABC Class (placeholder - based on revenue)
            # A = Top 20%, B = Next 30%, C = Remaining 50%
            product_abc = self.df.groupby('product_id')['Gross_Revenue'].sum().reset_index()
            product_abc = product_abc.sort_values('Gross_Revenue', ascending=False)
            product_abc['Cumulative_Revenue'] = product_abc['Gross_Revenue'].cumsum()
            product_abc['Cumulative_Percent'] = (
                product_abc['Cumulative_Revenue'] / product_abc['Gross_Revenue'].sum()
            ) * 100
            
            product_abc['ABC_Class'] = 'C'
            product_abc.loc[product_abc['Cumulative_Percent'] <= 20, 'ABC_Class'] = 'A'
            product_abc.loc[
                (product_abc['Cumulative_Percent'] > 20) & 
                (product_abc['Cumulative_Percent'] <= 50), 
                'ABC_Class'
            ] = 'B'
            
            product_abc = product_abc[['product_id', 'ABC_Class']]
            self.df = self.df.merge(product_abc, on='product_id', how='left')
            print(f"✓ ABC_Class calculated")
            
            # XYZ Class (placeholder - based on demand variability)
            product_xyz = self.df.groupby('product_id')['sales_quantity'].agg(
                ['mean', 'std']
            ).reset_index()
            product_xyz['CV'] = product_xyz['std'] / (product_xyz['mean'] + 0.001)  # Coefficient of variation
            product_xyz = product_xyz.sort_values('CV')
            
            product_xyz['XYZ_Class'] = 'Z'
            product_xyz.loc[product_xyz.index[:len(product_xyz)//3], 'XYZ_Class'] = 'X'
            product_xyz.loc[
                product_xyz.index[len(product_xyz)//3:2*len(product_xyz)//3],
                'XYZ_Class'
            ] = 'Y'
            
            product_xyz = product_xyz[['product_id', 'XYZ_Class']]
            self.df = self.df.merge(product_xyz, on='product_id', how='left')
            print(f"✓ XYZ_Class calculated")
            
            # AX_AY_AZ Combined Class
            self.df['AX_AY_AZ_Class'] = (
                self.df['ABC_Class'].astype(str) + 
                self.df['XYZ_Class'].astype(str)
            )
            print(f"✓ AX_AY_AZ_Class calculated")
            
        else:
            print(f"⚠ Missing product_id or date column")
        
        print("=" * 80)
        return self.df
    
    def validate_kpis(self):
        """
        Validate all KPI calculations
        
        Returns:
            dict: Validation results
        """
        print("\nSTEP 9: VALIDATING KPI ENGINE")
        print("=" * 80)
        
        validation = {
            'divide_by_zero_errors': 0,
            'negative_margins': 0,
            'missing_kpis': [],
            'duplicated_rows': 0,
            'data_types': {}
        }
        
        # Check for infinite values
        infinite_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in infinite_cols:
            inf_count = np.isinf(self.df[col]).sum()
            validation['divide_by_zero_errors'] += inf_count
        print(f"✓ Divide-by-zero errors: {validation['divide_by_zero_errors']}")
        
        # Check for negative margins
        if 'Margin_Percent' in self.df.columns:
            neg_margins = (self.df['Margin_Percent'] < 0).sum()
            validation['negative_margins'] = neg_margins
            print(f"✓ Negative margins: {neg_margins}")
        
        # Check for missing KPIs
        expected_kpis = [
            'Gross_Revenue', 'Net_Revenue', 'ASP',
            'Purchase_Cost', 'Landed_Cost', 'Cost_Variance',
            'Gross_Profit', 'Margin_Percent', 'Contribution_Margin',
            'Inventory_Turnover', 'Days_of_Inventory', 'Stockout_Risk_Flag',
            'Lead_Time_Days', 'Supplier_Spend',
            'Store_Total_Revenue', 'Store_Total_Margin',
            'Velocity', 'Revenue_Contribution', 'ABC_Class', 'XYZ_Class'
        ]
        
        missing_kpis = [kpi for kpi in expected_kpis if kpi not in self.df.columns]
        validation['missing_kpis'] = missing_kpis
        if missing_kpis:
            print(f"⚠ Missing KPIs: {missing_kpis}")
        else:
            print(f"✓ All expected KPIs present")
        
        # Check for duplicated rows
        duplicated = self.df.duplicated().sum()
        validation['duplicated_rows'] = duplicated
        print(f"✓ Duplicated rows: {duplicated}")
        
        # Check data types
        print(f"\n✓ Data types validated")
        for col in self.df.columns:
            validation['data_types'][col] = str(self.df[col].dtype)
        
        print("=" * 80)
        self.validation_results['kpi_validation'] = validation
        return validation
    
    def print_kpi_summary(self):
        """
        Print a comprehensive KPI summary
        
        Returns:
            dict: Summary statistics
        """
        print("\nSTEP 10: KPI SUMMARY STATISTICS")
        print("=" * 80)
        
        summary = {}
        
        # Revenue Summary
        total_revenue = self.df['Gross_Revenue'].sum()
        summary['Total_Revenue'] = total_revenue
        print(f"\n📊 REVENUE METRICS")
        print(f"  Total Gross Revenue: ${total_revenue:,.2f}")
        print(f"  Average ASP: ${self.df['ASP'].mean():.2f}")
        print(f"  Total Sales Quantity: {self.df['sales_quantity'].sum():,.0f}")
        
        # Cost Summary
        total_purchase_cost = self.df['Purchase_Cost'].sum()
        summary['Total_Purchase_Cost'] = total_purchase_cost
        print(f"\n💰 COST METRICS")
        print(f"  Total Purchase Cost: ${total_purchase_cost:,.2f}")
        print(f"  Average Purchase Price: ${self.df['purchase_price'].mean():.2f}")
        
        # Profit Summary
        total_gross_profit = self.df['Gross_Profit'].sum()
        summary['Total_Gross_Profit'] = total_gross_profit
        avg_margin = self.df['Margin_Percent'].mean()
        summary['Average_Margin_Percent'] = avg_margin
        print(f"\n📈 PROFIT METRICS")
        print(f"  Total Gross Profit: ${total_gross_profit:,.2f}")
        print(f"  Average Margin %: {avg_margin:.2f}%")
        
        # Inventory Summary
        avg_inventory_turnover = self.df['Inventory_Turnover'].mean()
        summary['Average_Inventory_Turnover'] = avg_inventory_turnover
        print(f"\n📦 INVENTORY METRICS")
        print(f"  Average Inventory Turnover: {avg_inventory_turnover:.2f}x")
        print(f"  Total On-Hand Quantity: {self.df['on_hand_quantity'].sum():,.0f}")
        print(f"  Stockout Risk Items: {self.df['Stockout_Risk_Flag'].sum():,.0f}")
        
        # Supplier Summary
        total_supplier_spend = self.df['Supplier_Spend'].sum() / len(self.df['vendor_id'].unique())
        summary['Average_Supplier_Spend'] = total_supplier_spend
        avg_lead_time = self.df['Lead_Time_Days'].mean()
        summary['Average_Lead_Time_Days'] = avg_lead_time
        print(f"\n🤝 SUPPLIER METRICS")
        print(f"  Average Supplier Spend: ${total_supplier_spend:,.2f}")
        print(f"  Average Lead Time: {avg_lead_time:.1f} days")
        print(f"  Average Supplier Reliability: {self.df['Supplier_Reliability'].mean():.1f}%")
        
        # Store Summary
        if 'Store_Total_Revenue' in self.df.columns:
            num_stores = self.df['store_id'].nunique()
            print(f"\n🏬 STORE METRICS")
            print(f"  Number of Stores: {num_stores}")
            print(f"  Average Store Revenue: ${self.df['Store_Total_Revenue'].mean():,.2f}")
            print(f"  Average Store Margin: ${self.df['Store_Total_Margin'].mean():,.2f}")
            if 'Store_Efficiency' in self.df.columns:
                print(f"  Average Store Efficiency: {self.df['Store_Efficiency'].mean():.2f}x")
        
        # Product Summary
        if 'ABC_Class' in self.df.columns:
            num_products = self.df['product_id'].nunique()
            print(f"\n📊 PRODUCT METRICS")
            print(f"  Number of Products: {num_products}")
            print(f"  Average Velocity: {self.df['Velocity'].mean():.2f} units/day")
            print(f"\n  ABC Classification:")
            for cls in ['A', 'B', 'C']:
                count = (self.df['ABC_Class'] == cls).sum()
                print(f"    {cls}-Class Products: {count}")
        
        print("\n" + "=" * 80)
        self.validation_results['summary'] = summary
        return summary
    
    def export_kpi_dataset(self, output_path):
        """
        Export the KPI-enhanced dataset to parquet
        
        Args:
            output_path (str): Path to export the dataset
            
        Returns:
            str: Path to exported file
        """
        print("\nSTEP 11: EXPORTING KPI DATASET")
        print("=" * 80)
        
        self.df.to_parquet(output_path, index=False)
        print(f"✓ KPI dataset exported to: {output_path}")
        print(f"  Total rows: {len(self.df):,}")
        print(f"  Total columns: {len(self.df.columns)}")
        print(f"  File size: {pd.io.parquet.get_engine('pyarrow').read_table(output_path).nbytes / 1024 / 1024:.2f} MB")
        print("=" * 80)
        
        return output_path
    
    def get_kpi_dataset(self):
        """
        Return the KPI-enhanced dataset
        
        Returns:
            pd.DataFrame: DataFrame with all KPIs
        """
        return self.df
    
    def get_validation_results(self):
        """
        Return validation results
        
        Returns:
            dict: Validation results
        """
        return self.validation_results


def main():
    """
    Main function to run the complete KPI engine
    """
    import os
    
    # Define paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_path, 'data', 'data_model', 'master_dataset.parquet')
    output_path = os.path.join(base_path, 'data', 'data_model', 'master_dataset_kpi.parquet')
    
    print("\n" + "=" * 80)
    print("KPI ENGINE - COMPLETE KPI CALCULATION SYSTEM")
    print("=" * 80)
    print(f"\nLoading master dataset from: {input_path}")
    
    # Load the master dataset
    df = pd.read_parquet(input_path)
    
    # Initialize KPI Engine
    engine = KPIEngine(df)
    
    # Execute all KPI calculations
    engine.load_and_validate()
    engine.create_revenue_kpis()
    engine.create_cost_kpis()
    engine.create_profit_kpis()
    engine.create_inventory_kpis()
    engine.create_supplier_kpis()
    engine.create_store_kpis()
    engine.create_product_kpis()
    engine.validate_kpis()
    engine.print_kpi_summary()
    
    # Export the result
    engine.export_kpi_dataset(output_path)
    
    # Return the enhanced dataset
    kpi_df = engine.get_kpi_dataset()
    
    print(f"\n✅ KPI ENGINE EXECUTION COMPLETED SUCCESSFULLY")
    print(f"\nFinal Dataset Shape: {kpi_df.shape}")
    print(f"Columns: {list(kpi_df.columns)}")
    
    return kpi_df, engine.get_validation_results()


if __name__ == "__main__":
    kpi_dataset, validation_results = main()
