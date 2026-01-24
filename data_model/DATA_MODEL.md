# 🗂️ Official Data Model - Star Schema Design

## Overview
This document defines the official analytical data model for inventory optimization analysis. This star schema design is **reusable for any company** and follows dimensional modeling best practices.

**Last Updated:** January 24, 2026  
**Model Type:** Star Schema (Kimball Methodology)  
**Status:** ✅ LOCKED & APPROVED

---

## 📊 Data Model Architecture

```
                    ┌─────────────────┐
                    │   Dim_Date      │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
         ┌──────────▼────────┐ ┌─────▼──────────┐ ┌──────────────────┐
         │  Fact_Sales       │ │ Fact_Purchases │ │ Fact_Inventory_  │
         │                   │ │                │ │    Snapshot      │
         └──┬────┬────┬──────┘ └──┬─────┬──────┘ └──┬────┬──────────┘
            │    │    │           │     │           │    │
    ┌───────┘    │    └───────┐   │     └───────┐   │    └────────┐
    │            │            │   │             │   │             │
┌───▼──────┐ ┌───▼──────┐ ┌──▼───▼────┐ ┌──────▼───▼──┐ ┌────────▼─────┐
│Dim_Store │ │Dim_Vendor│ │Dim_Product│ │ Dim_Product │ │  Dim_Store   │
└──────────┘ └──────────┘ └───────────┘ └─────────────┘ └──────────────┘
```

---

## 🎯 Table Definitions

### **FACT TABLES** (Transaction Data)

#### 1️⃣ **Fact_Sales**
**Purpose:** Records all sales transactions  
**Grain:** One row per product sold per store per transaction date

| Column Name | Data Type | Description | Key Type |
|-------------|-----------|-------------|----------|
| sale_id | VARCHAR(50) | Unique transaction identifier (PK) | Primary Key |
| date_key | INT | Date dimension foreign key | Foreign Key |
| product_key | VARCHAR(50) | Product dimension foreign key | Foreign Key |
| store_key | INT | Store dimension foreign key | Foreign Key |
| quantity_sold | INT | Number of units sold | Measure |
| sales_price | DECIMAL(10,2) | Price per unit | Measure |
| sales_amount | DECIMAL(12,2) | Total revenue (qty × price) | Measure |
| sales_dollars | DECIMAL(12,2) | Total sales value | Measure |

**Source:** cleaned_sales.csv  
**Refresh:** Daily (append only)

---

#### 2️⃣ **Fact_Purchases**
**Purpose:** Records all purchase transactions from vendors  
**Grain:** One row per product purchased per vendor per transaction date

| Column Name | Data Type | Description | Key Type |
|-------------|-----------|-------------|----------|
| purchase_id | VARCHAR(50) | Unique purchase identifier (PK) | Primary Key |
| date_key | INT | Date dimension foreign key | Foreign Key |
| product_key | VARCHAR(50) | Product dimension foreign key | Foreign Key |
| vendor_key | VARCHAR(50) | Vendor dimension foreign key | Foreign Key |
| quantity_purchased | INT | Number of units purchased | Measure |
| purchase_price | DECIMAL(10,2) | Cost per unit | Measure |
| purchase_amount | DECIMAL(12,2) | Total cost (qty × price) | Measure |
| po_number | VARCHAR(50) | Purchase order reference | Attribute |
| invoice_date | DATE | Invoice date | Attribute |

**Source:** cleaned_purchases.csv + cleaned_invoice_purchases.csv  
**Refresh:** Daily (append only)

---

#### 3️⃣ **Fact_Inventory_Snapshot**
**Purpose:** Records inventory levels at specific points in time  
**Grain:** One row per product per store per snapshot date

| Column Name | Data Type | Description | Key Type |
|-------------|-----------|-------------|----------|
| snapshot_id | VARCHAR(100) | Unique snapshot identifier (PK) | Primary Key |
| date_key | INT | Date dimension foreign key | Foreign Key |
| product_key | VARCHAR(50) | Product dimension foreign key | Foreign Key |
| store_key | INT | Store dimension foreign key | Foreign Key |
| on_hand_quantity | INT | Units available | Measure |
| inventory_value | DECIMAL(12,2) | Value at sales price | Measure |
| snapshot_type | VARCHAR(20) | Beginning/Ending/Daily | Attribute |

**Source:** cleaned_beginning_inventory.csv + cleaned_ending_inventory.csv  
**Refresh:** Daily (append), Monthly (full snapshot)

---

### **DIMENSION TABLES** (Reference/Lookup Data)

#### 4️⃣ **Dim_Product**
**Purpose:** Master list of all products with attributes  
**Type:** Type 2 SCD (Slowly Changing Dimension)

| Column Name | Data Type | Description | Attribute Type |
|-------------|-----------|-------------|----------------|
| product_key | VARCHAR(50) | Surrogate key (PK) | Primary Key |
| brand_code | VARCHAR(10) | Brand/vendor code | Business Key |
| description | VARCHAR(255) | Product description | Descriptor |
| size | VARCHAR(20) | Package size (e.g., 750mL) | Attribute |
| category | VARCHAR(50) | Product category | Hierarchy L1 |
| subcategory | VARCHAR(50) | Product subcategory | Hierarchy L2 |
| abc_class | CHAR(1) | ABC classification (A/B/C) | Analytics |
| xyz_class | CHAR(1) | XYZ classification (X/Y/Z) | Analytics |
| is_active | BOOLEAN | Active status | Control |
| effective_date | DATE | Start date for this version | SCD |
| expiration_date | DATE | End date for this version | SCD |

**Source:** Derived from all cleaned files (unique products)  
**Refresh:** Daily (incremental with SCD Type 2)

---

#### 5️⃣ **Dim_Store**
**Purpose:** Master list of all store locations  
**Type:** Type 1 SCD

| Column Name | Data Type | Description | Attribute Type |
|-------------|-----------|-------------|----------------|
| store_key | INT | Store number (PK) | Primary Key |
| store_name | VARCHAR(100) | Store name | Descriptor |
| city | VARCHAR(100) | City location | Geography |
| state | VARCHAR(50) | State location | Geography |
| region | VARCHAR(50) | Regional grouping | Hierarchy L1 |
| store_type | VARCHAR(50) | Retail/Warehouse/etc. | Classification |
| is_active | BOOLEAN | Active status | Control |

**Source:** Derived from cleaned_beginning_inventory.csv, cleaned_sales.csv  
**Refresh:** Weekly (full replace)

---

#### 6️⃣ **Dim_Vendor**
**Purpose:** Master list of all suppliers/vendors  
**Type:** Type 1 SCD

| Column Name | Data Type | Description | Attribute Type |
|-------------|-----------|-------------|----------------|
| vendor_key | VARCHAR(50) | Vendor code (PK) | Primary Key |
| vendor_name | VARCHAR(255) | Vendor name | Descriptor |
| vendor_classification | VARCHAR(50) | Kraljic matrix quadrant | Analytics |
| contact_info | VARCHAR(255) | Contact details | Attribute |
| lead_time_days | INT | Average lead time | Metric |
| is_preferred | BOOLEAN | Preferred vendor flag | Control |
| is_active | BOOLEAN | Active status | Control |

**Source:** Derived from cleaned_purchases.csv, cleaned_invoice_purchases.csv  
**Refresh:** Weekly (incremental)

---

#### 7️⃣ **Dim_Date**
**Purpose:** Standard date dimension for time-based analysis  
**Type:** Static (pre-populated)

| Column Name | Data Type | Description | Attribute Type |
|-------------|-----------|-------------|----------------|
| date_key | INT | Surrogate key YYYYMMDD (PK) | Primary Key |
| full_date | DATE | Actual date | Date |
| year | INT | Year (2016, 2017) | Hierarchy L1 |
| quarter | INT | Quarter (1-4) | Hierarchy L2 |
| month | INT | Month number (1-12) | Hierarchy L3 |
| month_name | VARCHAR(20) | Month name | Descriptor |
| week | INT | Week of year (1-53) | Time Period |
| day_of_week | INT | Day number (1-7) | Time Period |
| day_name | VARCHAR(20) | Day name | Descriptor |
| is_weekend | BOOLEAN | Weekend flag | Flag |
| is_holiday | BOOLEAN | Holiday flag | Flag |
| fiscal_year | INT | Fiscal year | Fiscal Calendar |
| fiscal_quarter | INT | Fiscal quarter | Fiscal Calendar |

**Source:** Generated programmatically  
**Refresh:** Annually (extend forward)

---

## 🔗 Relationships & Cardinality

| Fact Table | Dimension Table | Relationship | Cardinality |
|------------|-----------------|--------------|-------------|
| Fact_Sales | Dim_Date | date_key | Many-to-One |
| Fact_Sales | Dim_Product | product_key | Many-to-One |
| Fact_Sales | Dim_Store | store_key | Many-to-One |
| Fact_Purchases | Dim_Date | date_key | Many-to-One |
| Fact_Purchases | Dim_Product | product_key | Many-to-One |
| Fact_Purchases | Dim_Vendor | vendor_key | Many-to-One |
| Fact_Inventory_Snapshot | Dim_Date | date_key | Many-to-One |
| Fact_Inventory_Snapshot | Dim_Product | product_key | Many-to-One |
| Fact_Inventory_Snapshot | Dim_Store | store_key | Many-to-One |

---

## 📐 Data Model Rules

### ✅ **DO's:**
1. **Always use surrogate keys** for dimension tables
2. **Maintain grain consistency** - one fact row = one transaction/snapshot
3. **Denormalize dimensions** - include descriptive attributes
4. **Use Type 2 SCD** for products (track changes over time)
5. **Enforce referential integrity** with foreign keys
6. **Add audit columns**: created_date, modified_date, created_by

### ❌ **DON'Ts:**
1. **Don't snowflake** - keep dimensions denormalized
2. **Don't mix grains** in the same fact table
3. **Don't store nulls** in dimension keys
4. **Don't use natural keys** as primary keys
5. **Don't skip the date dimension** - always use it for temporal analysis

---

## 🎯 Key Metrics & Calculations

### **Inventory Metrics:**
- **Inventory Turnover** = Total COGS / Average Inventory Value
- **Days of Inventory** = (Average Inventory / COGS) × 365
- **Fill Rate** = Units Sold / (Units Sold + Stockouts)
- **Stock Coverage** = On Hand Quantity / Average Daily Sales

### **Purchasing Metrics:**
- **Purchase Order Accuracy** = Accurate POs / Total POs
- **Supplier Lead Time** = Invoice Date - PO Date
- **Cost Variance** = Actual Cost - Standard Cost

### **Sales Metrics:**
- **Revenue** = SUM(sales_amount)
- **Units Sold** = SUM(quantity_sold)
- **Average Transaction Value** = Revenue / COUNT(DISTINCT sale_id)

---

## 🔄 ETL Guidelines

### **Data Quality Rules:**
1. **Completeness**: No nulls in key columns
2. **Consistency**: Standardized formats across all tables
3. **Accuracy**: Validated against source systems
4. **Timeliness**: Updated according to refresh schedule

### **Transformation Steps:**
1. **Extract**: Load from cleaned CSVs
2. **Transform**: Apply business rules, generate keys
3. **Load**: Insert into fact/dimension tables
4. **Validate**: Check counts, totals, referential integrity

---

## 📁 File Mapping

| Table Name | Source File(s) | Output Location |
|------------|---------------|-----------------|
| Fact_Sales | cleaned_sales.csv | data/data_model/fact_sales.csv |
| Fact_Purchases | cleaned_purchases.csv, cleaned_invoice_purchases.csv | data/data_model/fact_purchases.csv |
| Fact_Inventory_Snapshot | cleaned_beginning_inventory.csv, cleaned_ending_inventory.csv | data/data_model/fact_inventory_snapshot.csv |
| Dim_Product | All cleaned files | data/data_model/dim_product.csv |
| Dim_Store | cleaned_beginning_inventory.csv, cleaned_sales.csv | data/data_model/dim_store.csv |
| Dim_Vendor | cleaned_purchases.csv | data/data_model/dim_vendor.csv |
| Dim_Date | Generated | data/data_model/dim_date.csv |

---

## ✅ Implementation Status

| Step | Status | Notes |
|------|--------|-------|
| Data Model Design | ✅ COMPLETE | This document |
| Table Creation Scripts | 🔄 NEXT | create_data_model.py |
| ETL Pipeline | ⏳ PENDING | transform_to_star_schema.py |
| Data Quality Checks | ⏳ PENDING | validate_data_model.py |
| Power BI Integration | ⏳ PENDING | Load dimensional model |

---

## 🚀 Next Steps

**Step 2:** Create Python scripts to build dimension and fact tables  
**Step 3:** Implement ETL pipeline with data quality checks  
**Step 4:** Load into analytical database or Power BI  
**Step 5:** Build consumption layer (views, reports)

---

## 📝 Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-01-24 | 1.0 | System | Initial data model locked |

---

**🔒 This data model is LOCKED and serves as the source of truth for all analytical work.**
