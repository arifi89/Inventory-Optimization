# Inventory Optimization Analysis - Current State (January 28, 2026)

## Executive Summary

This document describes the **current final state** of the inventory optimization analysis. The project transformed raw retail sales, purchase, and inventory data into a comprehensive Master Dataset using proper retail costing methodology (Weighted Average Cost), enabling accurate profitability and inventory analysis.

---

## 1. Project Scope & What We Built

### 1.1 Objective
Create a production-ready Master Dataset that:
- Accurately reflects retail costing practices (not direct PO-to-Sale links)
- Calculates realistic profit margins and cost of goods sold
- Matches inventory levels to sales transactions
- Provides foundation for ABC/XYZ segmentation and KPI analysis

### 1.2 Data Period
- **Date Range:** January 1, 2016 - February 29, 2016 (60 days)
- **Geographic Scope:** 79 retail store locations
- **Product Range:** 7,658 unique products

### 1.3 Data Volume
| Component | Count |
|-----------|-------|
| Sales Transactions | 1,048,575 |
| Purchase Orders | 2,372,471 |
| Inventory Snapshots | 431,018 |
| Unique Products | 7,658 |
| Unique Stores | 79 |

---

## 2. Data Architecture

### 2.1 Star Schema Model

```
FACT TABLES:
├── fact_sales (1,048,575 rows)
│   ├── Sales_Order, Sales_Date
│   ├── Product_Number, Store, Sales_Quantity, Sales_Price, Tax
│   └── Primary Keys: Sales_Order
│
├── fact_purchases (2,372,471 rows)
│   ├── Product_Number, Store, Purchase_Date, Vendor
│   ├── Quantity_Purchased, Unit_Cost, Freight_Cost
│   └── No primary key (aggregated purchase orders)
│
└── fact_inventory_snapshot (431,018 rows)
    ├── Product_Number, Store, Snapshot_Date, Snapshot_Type
    ├── On_Hand_Quantity, Inventory_Value
    └── Primary Key: Product_Number + Store + Snapshot_Date

DIMENSION TABLES:
├── dim_product (7,658 rows)
│   └── Product_Number (PK), Description, Size, Category
│
├── dim_store (79 rows)
│   └── Store (PK), Store_Name, City, State, Region
│
├── dim_vendor (various)
│   └── Vendor_ID (PK), Vendor_Name
│
└── dim_date (auxiliary)
    └── Date, Year, Quarter, Month, Week, Day_of_Week
```

### 2.2 Primary Key Strategy
- **Product_Number:** Consistent identifier across ALL tables (sales, purchases, inventory, dimensions)
- **Store:** Consistent store identifier (primary key in dim_store)
- **Sales_Order:** Unique transaction identifier (primary key in fact_sales)

---

## 3. Costing Methodology (What We Did)

### 3.1 Why Weighted Average Cost (WAC)?

**Problem with Original Approach:**
- Direct linking of individual Sales Orders to individual Purchase Orders
- Only 2.3% of sales got matched to inventory
- 88.22% of records showed 100% margins (data artifacts)
- Not how retail companies actually cost inventory

**Solution: Weighted Average Cost**
- Aligns with retail industry best practices
- Uses ALL purchase history for each product
- Distributes purchase costs fairly across all sales
- Results in realistic, defensible margin profiles

### 3.2 WAC Calculation

For each Product_Number across ALL purchase history (not limited by store or date):

```
WAC = Σ(Purchase_Quantity × Unit_Cost) / Σ(Purchase_Quantity)
```

**Example:**
```
Product #12345 - All Purchases (Period: Jan-Feb 2016)
─────────────────────────────────────────────
Purchase 1: 100 units @ $10.00 = $1,000
Purchase 2: 150 units @ $9.50  = $1,425
Purchase 3:  50 units @ $11.00 = $550
─────────────────────────────────────────────
Total: 300 units = $2,975
WAC = $2,975 / 300 = $9.92 per unit

All sales of Product #12345 in this period use WAC of $9.92
```

### 3.3 Freight Cost Allocation

Freight costs from purchase orders distributed across units purchased:

```
Freight_per_Unit = Total_Freight_Cost / Total_Quantity_Purchased
```

**Applied to Sales:**
```
Freight_Cost_on_Sale = Sales_Quantity × Freight_per_Unit
```

### 3.4 Cost of Goods Sold (COGS)

```
Purchase_Cost = Sales_Quantity × WAC
Freight_Cost = Sales_Quantity × Freight_per_Unit
COGS = Purchase_Cost + Freight_Cost
```

### 3.5 Profit Calculation

```
Revenue = Sales_Quantity × Sales_Price
Gross_Profit = Revenue - COGS
Margin_Percent = (Gross_Profit / Revenue) × 100
```

---

## 4. Inventory Matching Logic

### 4.1 Challenge
- Sales need to be matched to inventory levels to determine on-hand quantities
- Exact-date matching failed (most sales dates had no inventory snapshots)
- Need practical approach used in retail environments

### 4.2 Solution: Nearest-Prior-Snapshot Matching

For each sale transaction:
1. Identify all inventory snapshots BEFORE the sale date
2. Select the **most recent prior snapshot** for that Product-Store combination
3. Use that inventory level as "On_Hand_Quantity" before the sale
4. Use that snapshot's value as "Inventory_Value"

**Formula:**
```
For Sale at Product P, Store S, Date D:
  Match to Inventory Snapshot where:
    - Product_Number = P
    - Store = S
    - Snapshot_Date = MAX(Snapshot_Date < D)
```

### 4.3 Coverage
- Sales with inventory match: **1,039,816 / 1,048,575 (99.16%)**
- Unmatched: Early sales (before first inventory snapshot)

---

## 5. Master Dataset Structure

### 5.1 File Details
- **Format:** Parquet (columnar, compressed) + CSV (full export)
- **File Path:** `data/data_model/Master_Dataset.parquet` and `.csv`
- **Size:** 40.6 MB (parquet), 359.5 MB (CSV)
- **Rows:** 1,048,575 (one per sales transaction)
- **Columns:** 38

### 5.2 Column Groups (38 Total)

| Group | Columns | Count |
|-------|---------|-------|
| **Transaction ID** | Sales_Order, Sales_Date | 2 |
| **Product Info** | Product_Number, Description, Size | 3 |
| **Store Info** | Store, Store_Name, Store_City, Store_State, Store_Region | 5 |
| **Sales Metrics** | Sales_Quantity, Sales_Price, Revenue, Gross_Revenue, Net_Revenue, Tax | 6 |
| **Cost Metrics** | WAC, Freight_per_Unit, Purchase_Cost, Freight_Cost, Landed_Cost, COGS | 6 |
| **Profit Metrics** | Gross_Profit, Margin_Percent | 2 |
| **Inventory Metrics** | On_Hand_Quantity, Inventory_Value, Snapshot_Date, Snapshot_Type | 4 |
| **Segmentation** | ABC_Class, XYZ_Class, ABC_XYZ_Segment | 3 |
| **Time Dimensions** | Year, Quarter, Month, Month_Name, Week, Day_of_Week, Day_Name | 7 |

### 5.3 Key Columns (Alphabetically)

| Column | Type | Coverage | Description |
|--------|------|----------|-------------|
| ABC_Class | float64 | 0.00% | ABC inventory classification (A=High Value, B=Mid, C=Low) |
| ABC_XYZ_Segment | str | 0.00% | Combined ABC-XYZ classification (e.g., AX, BZ) |
| COGS | float64 | 99.82% | Cost of Goods Sold = Purchase_Cost + Freight_Cost |
| Day_Name | str | 100.00% | Day of week name (Monday, Tuesday, etc.) |
| Day_of_Week | int64 | 100.00% | Day of week number (0=Monday, 6=Sunday) |
| Description | str | 100.00% | Product name/description |
| Freight_Cost | float64 | 100.00% | Total freight allocated to this sale |
| Freight_per_Unit | float64 | 99.82% | Freight cost per unit from weighted purchases |
| Gross_Profit | float64 | 99.82% | Revenue - COGS |
| Gross_Revenue | float64 | 100.00% | Same as Revenue (backup field) |
| Inventory_Value | float64 | 99.16% | Dollar value of on-hand inventory before sale |
| Landed_Cost | float64 | 99.82% | WAC + Freight_per_Unit (total cost per unit) |
| Margin_Percent | float64 | 99.82% | (Gross_Profit / Revenue) × 100 |
| Month | int64 | 100.00% | Month number (1-12) |
| Month_Name | str | 100.00% | Month name (January, February) |
| Net_Revenue | float64 | 100.00% | Revenue - Tax |
| On_Hand_Quantity | float64 | 99.16% | Inventory on hand before this sale |
| Product_Number | int64 | 100.00% | Product identifier (consistent across all tables) |
| Purchase_Cost | float64 | 99.82% | Sales_Quantity × WAC |
| Quarter | int64 | 100.00% | Quarter (1-4) |
| Revenue | float64 | 100.00% | Sales_Quantity × Sales_Price |
| Sales_Date | datetime64 | 100.00% | Date of sale transaction |
| Sales_Order | str | 100.00% | Unique sales order identifier |
| Sales_Price | float64 | 100.00% | Price per unit sold |
| Sales_Quantity | int64 | 100.00% | Number of units sold |
| Size | str | 100.00% | Product size/variant |
| Snapshot_Date | datetime64 | 99.16% | Date of nearest-prior inventory snapshot |
| Snapshot_Type | str | 99.16% | Type of inventory count (Beginning, Ending) |
| Store | int64 | 100.00% | Store location code |
| Store_City | str | 100.00% | City where store is located |
| Store_Name | str | 100.00% | Store location name |
| Store_Region | str | 100.00% | Regional grouping |
| Store_State | str | 100.00% | State/province |
| Tax | float64 | 100.00% | Sales tax collected |
| WAC | float64 | 99.82% | Weighted Average Cost per unit |
| Week | int64 | 100.00% | Week number (1-52) |
| XYZ_Class | float64 | 0.00% | XYZ demand classification (X=Stable, Y=Variable, Z=Intermittent) |
| Year | int64 | 100.00% | Year (2016) |

---

## 6. Key Metrics & Validation

### 6.1 Coverage Metrics

| Metric | Value | Status |
|--------|-------|--------|
| WAC Coverage | 1,046,668 / 1,048,575 (99.82%) | ✅ Excellent |
| Inventory Coverage | 1,039,816 / 1,048,575 (99.16%) | ✅ Excellent |
| Freight with Purchases | 1,046,668 / 1,048,575 (99.82%) | ✅ Excellent |
| Tax Coverage | 1,048,575 / 1,048,575 (100.00%) | ✅ Perfect |

### 6.2 Financial Summary

| Metric | Value |
|--------|-------|
| **Total Revenue** | $33,139,375.29 |
| **Total COGS** | $22,343,550.70 |
| **Total Gross Profit** | $10,796,044.80 |
| **Overall Margin %** | 32.26% |
| **Average Margin %** | 32.36% |
| **Median Margin %** | 31.43% |
| **Min Margin %** | -193.30% |
| **Max Margin %** | 74.83% |

### 6.3 Data Quality Checks

| Check | Result | Status |
|-------|--------|--------|
| Duplicate Rows | 0 | ✅ Pass |
| Records with 100% Margin | 0 | ✅ Pass |
| Null Primary Keys | 0 | ✅ Pass |
| Product_Number Consistency | 100% | ✅ Pass |
| Date Range Validity | 2016-01-01 to 2016-02-29 | ✅ Pass |

---

## 7. Processing Steps (What We Did)

### 7.1 Data Pipeline

```
Step 1: Load Source Data
   ↓
Step 2: Validate Data Model
   ↓
Step 3: Calculate Weighted Average Cost (WAC) & Freight per Unit
   ├─ Group purchases by Product_Number
   ├─ Calculate weighted cost for each product
   ├─ Calculate freight per unit
   └─ Create WAC lookup table
   ↓
Step 4: Match Inventory Snapshots
   ├─ For each sale transaction
   ├─ Find nearest-prior inventory snapshot
   ├─ Preserve on-hand quantity and inventory value
   └─ Create inventory matching lookup
   ↓
Step 5: Enrich Sales Data
   ├─ Join dim_product (Description, Size)
   ├─ Join dim_store (Store_Name, City, State, Region)
   ├─ Join WAC lookup
   ├─ Join Freight_per_Unit lookup
   └─ Join Inventory snapshot data
   ↓
Step 6: Calculate Cost & Profit Metrics
   ├─ Purchase_Cost = Sales_Quantity × WAC
   ├─ Freight_Cost = Sales_Quantity × Freight_per_Unit
   ├─ Landed_Cost = WAC + Freight_per_Unit
   ├─ COGS = Purchase_Cost + Freight_Cost
   ├─ Gross_Profit = Revenue - COGS
   └─ Margin_Percent = (Gross_Profit / Revenue) × 100
   ↓
Step 7: Add Time Dimensions
   ├─ Extract Year, Quarter, Month, Week, Day_of_Week
   ├─ Add Month_Name, Day_Name
   └─ Create date lookups
   ↓
Step 8: Handle Segmentation (Placeholder)
   ├─ ABC_Class, XYZ_Class, ABC_XYZ_Segment columns created
   └─ Values: Not available in source data (0% coverage)
   ↓
Step 9: Reorder Columns
   └─ Logical grouping: Transaction → Product → Store → Sales → Costs → Profits → Inventory → Segmentation → Time
   ↓
Step 10: Validation Checks
   ├─ Verify no duplicate rows
   ├─ Verify coverage percentages
   ├─ Check margin distribution
   └─ Validate primary keys
   ↓
Step 11: Export
   ├─ Save as Master_Dataset.parquet (40.6 MB)
   ├─ Save as Master_Dataset.csv (359.5 MB)
   └─ Create structured output logs
```

### 7.2 Key Transformations Applied

| Transformation | Details | Impact |
|---|---|---|
| **Weighted Average Cost** | Product-level WAC across all purchases | 99.82% coverage, realistic margins |
| **Freight Allocation** | Per-unit freight from purchase orders | Accurate landed cost calculation |
| **Inventory Matching** | Nearest-prior-snapshot per product-store | 99.16% coverage, practical approach |
| **Tax Inclusion** | Direct from sales transaction data | 100% coverage, accurate revenue |
| **Time Dimension** | Extract date components for analysis | Full temporal decomposition |
| **Store Enrichment** | Join dim_store for location details | Complete store context available |
| **Margin Normalization** | Removed 100% margin artifacts | Realistic 32% average margin |

---

## 8. Core Processing Script

### 8.1 Script Location
- **File:** `src/create_master_dataset_corrected.py`
- **Purpose:** Generates Master_Dataset from source data
- **Output:** `data/data_model/Master_Dataset.parquet` and `.csv`

### 8.2 Main Functions

**`calculate_weighted_average_cost(fact_purchases, fact_sales)`**
- Computes WAC and freight per unit for each product
- Uses ALL purchase history (not limited by store/date)
- Returns DataFrame with Product_Number, WAC, Freight_per_Unit
- Coverage: 99.82% of sales transactions

**`match_nearest_prior_inventory(fact_sales, fact_inventory_snapshot)`**
- Matches each sale to nearest-prior inventory snapshot
- Groups by Product_Number and Store
- Uses most recent snapshot before sale date
- Returns DataFrame with On_Hand_Quantity, Inventory_Value, Snapshot_Date, Snapshot_Type
- Coverage: 99.16% of sales transactions

**`create_master_dataset_corrected()`**
- Main orchestration function
- Loads all source tables
- Performs all transformations in sequence
- Validates data quality
- Exports to parquet and CSV
- Runtime: ~60 seconds on standard hardware

### 8.3 Running the Script

```bash
# From project root directory
.\.venv\Scripts\python.exe src\create_master_dataset_corrected.py
```

**Expected Output:**
```
Step 1: Loading data model tables...
Step 2: Validating data...
Step 3: Computing Weighted Average Cost (WAC)...
Step 4: Matching inventory snapshots...
Step 5: Enriching sales transactions...
Step 6: Calculating cost and profit metrics...
Step 7: Adding time dimensions...
Step 8: Handling segmentation...
Step 9: Reordering columns...
Step 10: Validation checks...
Step 11: Exporting corrected dataset...

✓ Saved: Master_Dataset.parquet
✓ Saved: Master_Dataset.csv
✓ Shape: 1,048,575 rows × 38 columns
```

---

## 9. Data Lineage

### 9.1 Source Data
- `fact_sales.csv` → 1,048,575 sales transactions
- `fact_purchases.csv` → 2,372,471 purchase records
- `fact_inventory_snapshot.csv` → 431,018 inventory snapshots
- `dim_product.csv` → 7,658 product definitions
- `dim_store.csv` → 79 store locations
- `dim_vendor.csv` → Vendor information
- `dim_date.csv` → Date reference table

### 9.2 Transformation Path
```
Source Data
    ↓
Data Validation
    ↓
WAC Calculation + Freight Allocation
    ↓
Inventory Matching
    ↓
Dimension Joins (Product, Store, Vendor, Date)
    ↓
Cost & Profit Metrics
    ↓
Time Dimension Extraction
    ↓
Data Quality Validation
    ↓
Master_Dataset (Final Output)
```

### 9.3 Output Files
- **Master_Dataset.parquet** — Compressed columnar format (primary analysis file)
- **Master_Dataset.csv** — Full CSV export (compatibility/portability)

---

## 10. Usage & Analysis Possibilities

### 10.1 Recommended Analyses

1. **Profitability Analysis**
   - Margin% by Product, Store, Time Period
   - Identify high/low margin items
   - Cost drivers (freight, product cost)

2. **Inventory Management**
   - Stock levels by product/store
   - Inventory value concentration
   - Slow-moving vs. fast-moving items

3. **Sales Performance**
   - Revenue by product, store, time period
   - Volume trends
   - Product mix analysis

4. **Supplier/Vendor Analysis**
   - Cost by vendor
   - Freight cost comparison
   - Purchase volume patterns

5. **Segmentation (Future)**
   - ABC analysis: Value distribution (A=20%, B=30%, C=50%)
   - XYZ analysis: Demand variability (X=Stable, Y=Variable, Z=Intermittent)
   - Strategic sourcing by segment

### 10.2 Loading the Dataset

**Python:**
```python
import pandas as pd

# Load parquet (recommended - faster)
df = pd.read_parquet('data/data_model/Master_Dataset.parquet')

# Or load CSV
df = pd.read_csv('data/data_model/Master_Dataset.csv')

# Check structure
print(df.shape)        # (1048575, 38)
print(df.columns)      # List all columns
print(df.head())       # First 5 rows
print(df.dtypes)       # Column data types
```

**SQL (if imported):**
```sql
SELECT TOP 10
    Sales_Order,
    Sales_Date,
    Product_Number,
    Description,
    Store_Name,
    Sales_Quantity,
    Revenue,
    COGS,
    Margin_Percent
FROM Master_Dataset
ORDER BY Sales_Date DESC;
```

---

## 11. Documentation Standards

### 11.1 Code Documentation
All scripts follow Python best practices:
- **Module docstring:** Purpose, approach, key methodology
- **Function docstring:** Description, parameters, return values
- **Inline comments:** Complex logic, business rules
- **Type hints:** Input/output types where applicable

### 11.2 Supporting Documentation
- `README.md` — Project overview and quick start
- `requirements.txt` — Python dependencies
- `data_model/README.md` — Data model description
- `data_model/DATA_MODEL.md` — Detailed schema documentation
- `data_model/PRIMARY_KEYS_FINAL.md` — Key definitions
- `data_model/QUICK_START.md` — How to get started

---

## 12. Project Status

### 12.1 Completed Tasks
✅ Data validation and quality checks  
✅ Weighted Average Cost calculation (99.82% coverage)  
✅ Freight cost allocation and tracking  
✅ Inventory snapshot matching (99.16% coverage)  
✅ Tax column inclusion (100% coverage)  
✅ Store name enrichment  
✅ Profit margin calculation  
✅ Time dimension extraction  
✅ Data quality validation  
✅ Master Dataset creation and export  
✅ Code documentation  
✅ Supporting documentation  

### 12.2 Future Enhancements (Optional)
- [ ] ABC/XYZ classification (columns ready, logic to implement)
- [ ] Supplier/vendor analysis models
- [ ] Seasonality analysis
- [ ] Forecasting models
- [ ] PowerBI/Tableau dashboards
- [ ] Additional KPI calculations

---

## 13. Technical Specifications

### 13.1 Requirements
- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.21.0
- pyarrow >= 5.0.0 (for parquet support)

### 13.2 Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 13.3 Performance Notes
- Script execution: ~60 seconds (one full dataset regeneration)
- Parquet I/O: ~2-3 seconds load/save
- CSV I/O: ~30-40 seconds load (much slower than parquet)
- Memory usage: ~2-3 GB during processing

---

## 14. Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-28 | 1.0 Final | Added Store_Name column, renamed to Master_Dataset, comprehensive documentation |
| 2026-01-25 | 0.9 | Verified freight calculation, validated tax inclusion |
| 2026-01-20 | 0.8 | Initial corrected dataset with WAC methodology |

---

## 15. Contact & Support

For questions about:
- **Data methodology:** See Section 3 (Costing Methodology)
- **Data structure:** See Section 5 (Master Dataset Structure)
- **Processing details:** See Section 7 (Processing Steps)
- **Code:** See Section 8 (Core Processing Script)
- **Usage examples:** See Section 10 (Usage & Analysis Possibilities)

---

**Document Last Updated:** January 28, 2026  
**Analysis Period:** January 1 - February 29, 2016  
**Primary Analyst:** Inventory Analysis System  
**Status:** ✅ Complete & Production Ready
