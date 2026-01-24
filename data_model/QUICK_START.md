# 🎯 Quick Reference Guide - Data Model Implementation

## 📋 Overview
This guide shows you how to implement the locked star schema data model for **any company**.

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Understand the Model**
Read the full data model specification:
- 📄 [DATA_MODEL.md](./DATA_MODEL.md)

**Core Structure:**
- **3 Fact Tables:** Sales, Purchases, Inventory Snapshots
- **4 Dimension Tables:** Product, Store, Vendor, Date

---

### **Step 2: Create the Tables**
Run the data model builder script:

```bash
# Navigate to project root
cd "c:\Users\Asim\Music\Inventory Analysis Case Study📈🕵🏼‍♂️👨🏼‍💻\inventory-optimization"

# Run the builder
python src/create_data_model.py
```

**What it does:**
1. ✅ Loads your cleaned data files
2. ✅ Creates 4 dimension tables
3. ✅ Creates 3 fact tables
4. ✅ Saves everything to `data/data_model/`

**Output Files:**
```
data/data_model/
├── dim_date.csv
├── dim_product.csv
├── dim_store.csv
├── dim_vendor.csv
├── fact_sales.csv
├── fact_purchases.csv
└── fact_inventory_snapshot.csv
```

---

### **Step 3: Validate Quality**
Run the validation script:

```bash
python src/validate_data_model.py
```

**What it checks:**
- ✅ No nulls in critical columns
- ✅ No duplicate keys
- ✅ Valid foreign key relationships
- ✅ Business rule compliance
- ✅ Summary statistics

---

## 🔧 Customization for Your Company

### **Edit Configuration (create_data_model.py)**

```python
class Config:
    # Update file paths for your data
    SALES_FILE = INPUT_DIR / 'your_sales_file.csv'
    PURCHASES_FILE = INPUT_DIR / 'your_purchases_file.csv'
    
    # Set your date range
    DATE_START = '2020-01-01'  # Your start date
    DATE_END = '2025-12-31'    # Your end date
    
    # Company settings
    COMPANY_NAME = 'Your Company Name'
    FISCAL_YEAR_START_MONTH = 4  # April fiscal year = 4
```

### **Column Mapping**
Update column name mappings to match your data:

```python
# Example: If your sales file has different column names
column_mapping = {
    'Order_Date': 'date_key',        # Your column → Standard name
    'Product_ID': 'product_key',
    'Store_Number': 'store_key',
    'Qty': 'quantity_sold',
    'Price': 'sales_price',
}
```

---

## 📊 Table Relationships

### **Visual Schema**
```
Dim_Date ──┬─→ Fact_Sales ←── Dim_Product
           │                  ↑
           ├─→ Fact_Purchases ←── Dim_Vendor
           │                  ↑
           └─→ Fact_Inventory ←── Dim_Store
```

### **Join Examples**

**Get sales by product:**
```python
sales_by_product = fact_sales.merge(
    dim_product, 
    on='product_key', 
    how='left'
)
```

**Get monthly sales:**
```python
monthly_sales = fact_sales.merge(
    dim_date[['date_key', 'year', 'month']], 
    on='date_key', 
    how='left'
).groupby(['year', 'month'])['sales_amount'].sum()
```

---

## 📐 Key Metrics Formulas

### **Inventory Turnover**
```python
turnover = total_cogs / average_inventory_value
```

### **Days of Inventory**
```python
days_inventory = (average_inventory / cogs) * 365
```

### **Fill Rate**
```python
fill_rate = units_sold / (units_sold + stockouts)
```

### **Stock Coverage**
```python
stock_coverage = on_hand_quantity / average_daily_sales
```

---

## 🔍 Common Queries

### **Q1: Top 10 Products by Revenue**
```python
top_products = fact_sales.groupby('product_key')['sales_amount'].sum()\
    .sort_values(ascending=False).head(10)
```

### **Q2: Monthly Purchase Trend**
```python
monthly_purchases = fact_purchases.merge(dim_date, on='date_key')\
    .groupby(['year', 'month'])['purchase_amount'].sum()
```

### **Q3: Current Inventory Value by Store**
```python
current_inv = fact_inventory[fact_inventory['snapshot_type'] == 'Ending']\
    .groupby('store_key')['inventory_value'].sum()
```

---

## 🎨 Power BI Integration

### **Load Tables**
1. Open Power BI Desktop
2. Get Data → Text/CSV
3. Load all 7 CSV files from `data/data_model/`

### **Create Relationships**
```
Fact_Sales[date_key] → Dim_Date[date_key]
Fact_Sales[product_key] → Dim_Product[product_key]
Fact_Sales[store_key] → Dim_Store[store_key]

Fact_Purchases[date_key] → Dim_Date[date_key]
Fact_Purchases[product_key] → Dim_Product[product_key]
Fact_Purchases[vendor_key] → Dim_Vendor[vendor_key]

Fact_Inventory[date_key] → Dim_Date[date_key]
Fact_Inventory[product_key] → Dim_Product[product_key]
Fact_Inventory[store_key] → Dim_Store[store_key]
```

### **Create Measures**
```dax
Total Revenue = SUM(Fact_Sales[sales_amount])
Total Units Sold = SUM(Fact_Sales[quantity_sold])
Average Price = DIVIDE([Total Revenue], [Total Units Sold])
Inventory Value = SUM(Fact_Inventory[inventory_value])
```

---

## 🔄 Update Process

### **Daily Updates**
1. Receive new transaction data
2. Clean and preprocess
3. Run `create_data_model.py` with new data
4. Run `validate_data_model.py` to verify
5. Refresh Power BI reports

### **Monthly Inventory Snapshots**
1. Take inventory count
2. Add to inventory snapshot file
3. Rerun data model creation
4. Update analytics

---

## 📝 Checklist for New Company

- [ ] Update `Config` class with your file paths
- [ ] Map your column names to standard names
- [ ] Set your fiscal year start month
- [ ] Update date range for your data period
- [ ] Customize product categories/hierarchies
- [ ] Add company-specific holidays to Dim_Date
- [ ] Configure store regions/classifications
- [ ] Set up vendor classifications (Kraljic)
- [ ] Run builder script
- [ ] Run validation script
- [ ] Load into Power BI
- [ ] Create relationships
- [ ] Build initial reports

---

## 🆘 Troubleshooting

### **"Column not found" errors**
→ Update the column mapping in the builder script to match your data

### **"Foreign key violations"**
→ Check that all products/stores/vendors exist in dimension tables before creating facts

### **"File not found"**
→ Verify file paths in `Config` class match your directory structure

### **"Date parsing errors"**
→ Ensure date columns are in consistent format (YYYY-MM-DD recommended)

---

## 📚 Resources

- **Full Documentation:** [DATA_MODEL.md](./DATA_MODEL.md)
- **Builder Script:** [create_data_model.py](../src/create_data_model.py)
- **Validation Script:** [validate_data_model.py](../src/validate_data_model.py)

---

## ✅ Success Criteria

Your data model is ready when:
- ✅ All 7 files created in `data/data_model/`
- ✅ Validation script shows 100% pass rate
- ✅ No null values in key columns
- ✅ No duplicate keys
- ✅ All foreign keys valid
- ✅ Business rules passing
- ✅ Power BI relationships established

---

**🎉 You now have a production-ready star schema data model!**
