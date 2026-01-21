# 🎯 Inventory Optimization & Procurement Strategy

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Project Overview

A comprehensive **end-to-end inventory optimization and procurement strategy project** that demonstrates advanced data analytics, strategic segmentation, and optimization techniques using Python and Power BI.

This project analyzes 2016 inventory, purchase, and sales data to:

- ✅ Optimize inventory levels and reduce carrying costs
- ✅ Implement ABC-XYZ product segmentation
- ✅ Apply Kraljic Matrix for supplier segmentation
- ✅ Calculate optimal Economic Order Quantity (EOQ) and Reorder Points (ROP)
- ✅ Develop data-driven procurement strategies
- ✅ Create interactive Power BI dashboards for decision-making

---

## 🎓 Skills Demonstrated

### **Technical Skills:**

- **Python Programming**: Pandas, NumPy, Matplotlib, Seaborn
- **Data Analysis**: EDA, statistical analysis, data cleaning
- **Optimization**: EOQ, ROP, safety stock calculations
- **Strategic Frameworks**: ABC-XYZ Analysis, Kraljic Matrix
- **Business Intelligence**: Power BI dashboard development
- **Documentation**: Professional project documentation

### **Business Skills:**

- Inventory Management & Optimization
- Procurement Strategy Development
- Supply Chain Analytics
- KPI Definition & Measurement
- Supplier Relationship Management
- Cost Reduction Initiatives

---

## 📊 Project Highlights

| Metric                 | Before Optimization | After Optimization | Improvement    |
| ---------------------- | ------------------- | ------------------ | -------------- |
| **Inventory Turnover** | TBD                 | TBD                | TBD%           |
| **Carrying Costs**     | TBD                 | TBD                | TBD% reduction |
| **Stockout Rate**      | TBD                 | TBD                | TBD% reduction |
| **Order Frequency**    | TBD                 | TBD                | TBD% optimized |
| **Total Cost Savings** | -                   | TBD                | $TBD           |

_Note: Metrics will be updated upon project completion_

---

## 🏗️ Project Structure

```
inventory-optimization/
│
├── README.md                     # Main project documentation
├── requirements.txt              # Python dependencies
├── .gitignore
│
├── data/
│   ├── raw/                      # Original data (unchanged)
│   ├── processed/                # Cleaned & merged datasets
│   └── segmentation/             # Product & supplier segmentation outputs
│
├── notebooks/
│   ├── 01_data_overview.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_kpi_calculation.ipynb
│   ├── 04_abc_xyz_segmentation.ipynb
│   ├── 05_supplier_segmentation_kraljic.ipynb
│   ├── 06_eoq_rop_safety_stock.ipynb
│   ├── 07_before_after_scenario.ipynb
│   └── 08_procurement_strategy.ipynb
│
├── src/
│   ├── load_data.py
│   ├── clean_data.py
│   ├── kpi_functions.py
│   ├── abc_xyz.py
│   ├── kraljic.py
│   ├── optimization.py
│   └── utils.py
│
├── procurement_strategy/
│   ├── product_segmentation.md
│   ├── supplier_segmentation.md
│   ├── kraljic_matrix.md
│   └── recommended_strategy.md
│
├── powerbi/
│   ├── inventory_dashboard.pbix
│   └── screenshots/
│
└── reports/
    ├── executive_summary.pdf
    ├── insights_presentation.pdf
    └── charts/
```

---

## 🚀 Getting Started

### **Prerequisites**

- Python 3.8 or higher
- Jupyter Notebook
- Power BI Desktop (for dashboard viewing)
- Git (for version control)

### **Installation**

1. **Clone the repository**

   ```bash
   git clone https://github.com/arifi89/Inventory-Optimization.git
   cd Inventory-Optimization
   ```

2. **Create virtual environment** (recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Place your data files**
   - Add your CSV files to the `data/raw/` directory
   - Ensure filenames match those in the project structure

5. **Launch Jupyter Notebook**

   ```bash
   jupyter notebook
   ```

6. **Start with notebook 01**
   - Open `notebooks/01_data_overview.ipynb`
   - Follow the notebooks sequentially (01 → 08)

---

## 📚 Project Workflow

### **Phase 1: Data Foundation (Notebooks 01-02)**

1. **Data Overview**: Load and explore all datasets
2. **Data Cleaning**: Handle missing values, duplicates, and data quality issues

### **Phase 2: KPI & Metrics (Notebook 03)**

3. **KPI Calculation**: Calculate inventory turnover, days of supply, fill rate, etc.

### **Phase 3: Strategic Segmentation (Notebooks 04-05)**

4. **ABC-XYZ Analysis**: Segment products by value and demand variability
5. **Kraljic Matrix**: Segment suppliers by profit impact and supply risk

### **Phase 4: Optimization (Notebook 06)**

6. **EOQ & ROP**: Calculate optimal order quantities and reorder points
7. **Safety Stock**: Determine appropriate safety stock levels

### **Phase 5: Strategy & Results (Notebooks 07-08)**

8. **Before/After Analysis**: Compare current vs. optimized scenarios
9. **Procurement Strategy**: Develop actionable procurement recommendations

### **Phase 6: Visualization (Power BI)**

10. **Dashboard Development**: Create interactive dashboards for stakeholders

---

## 🔑 Key Concepts & Frameworks

### **ABC-XYZ Analysis**

- **ABC Classification**: Products categorized by revenue contribution
  - **A items**: Top 20% of products = 80% of value (High priority)
  - **B items**: Next 30% of products = 15% of value (Medium priority)
  - **C items**: Bottom 50% of products = 5% of value (Low priority)

- **XYZ Classification**: Products categorized by demand variability
  - **X items**: Stable, predictable demand (CV < 0.5)
  - **Y items**: Moderate variability (0.5 ≤ CV < 1.0)
  - **Z items**: Erratic, unpredictable demand (CV ≥ 1.0)

### **Kraljic Matrix**

Supplier segmentation based on two dimensions:

- **Profit Impact**: Revenue contribution and cost significance
- **Supply Risk**: Market complexity, supplier availability, substitutability

Four categories:

1. **Strategic Items**: High impact, high risk → Partnership approach
2. **Leverage Items**: High impact, low risk → Competitive bidding
3. **Bottleneck Items**: Low impact, high risk → Ensure supply continuity
4. **Non-Critical Items**: Low impact, low risk → Simplify procurement

### **Inventory Optimization**

- **EOQ (Economic Order Quantity)**: Optimal order size minimizing total costs
- **ROP (Reorder Point)**: When to place a new order
- **Safety Stock**: Buffer inventory for demand/supply uncertainty
- **Service Level**: Target probability of not stocking out

---

## 📊 Sample Outputs

### **ABC-XYZ Matrix**

```
         X (Stable)    Y (Variable)   Z (Erratic)
A (High)    AX            AY             AZ
B (Med)     BX            BY             BZ
C (Low)     CX            CY             CZ
```

### **Procurement Strategies by Segment**

| Segment | Strategy           | Action                             |
| ------- | ------------------ | ---------------------------------- |
| **AX**  | Optimize inventory | Apply EOQ, reduce safety stock     |
| **AY**  | Monitor closely    | Dynamic safety stock               |
| **AZ**  | Strategic buffer   | High safety stock, frequent review |
| **CZ**  | Simplify           | Bulk orders, minimal monitoring    |

---

## Power BI Dashboard

The interactive dashboard includes:

1. ** Executive Overview**
   - Total inventory value
   - Inventory turnover rate
   - Key performance indicators
   - Cost savings summary

2. ** ABC-XYZ Analysis**
   - Product segmentation matrix
   - Value contribution by category
   - Demand variability charts

3. ** Supplier Analysis (Kraljic)**
   - Supplier segmentation quadrant
   - Performance metrics by supplier
   - Risk assessment

4. ** Optimization Results**
   - Current vs. optimized inventory levels
   - Cost savings breakdown
   - Before/after comparisons

5. ** Trends & Insights**
   - Purchase trends over time
   - Seasonal patterns
   - Forecast accuracy

---

## Documentation

Detailed documentation is available in the `procurement_strategy/` folder:

- **[Product Segmentation Strategy](procurement_strategy/product_segmentation.md)**: ABC-XYZ implementation guide
- **[Supplier Segmentation Strategy](procurement_strategy/supplier_segmentation.md)**: Kraljic Matrix application
- **[Kraljic Matrix Guide](procurement_strategy/kraljic_matrix.md)**: Detailed framework explanation
- **[Recommended Strategy](procurement_strategy/recommended_strategy.md)**: Final procurement recommendations

---

## Key Results & Insights

_This section will be updated with actual results after analysis_

### **Top Findings:**

1. TBD - Inventory optimization opportunities identified
2. TBD - Supplier consolidation recommendations
3. TBD - Cost savings potential quantified
4. TBD - Strategic procurement actions prioritized

### **Business Impact:**

- **Reduced carrying costs** by optimizing inventory levels
- **Improved service levels** through better demand planning
- **Enhanced supplier relationships** via strategic segmentation
- **Data-driven decision making** enabled by analytics

---

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Mohamed Abd Elaziz Abd Allah Osman**

- 🔗 LinkedIn: [Your LinkedIn Profile]: (www.linkedin.com/in/mohamed-osman-674b5580)
- 🐙 GitHub: [Your GitHub Profile](https://github.com/arifi89)
- 📧 Email: m.elarifi9@gmail.com

---

## 🙏 Acknowledgments

- Dataset source: [Kaggle Inventory Analysis Case Study](https://www.kaggle.com/datasets/bhanupratapbiswas/inventory-analysis-case-study)
- Inspired by best practices in supply chain analytics and procurement management
- Special thanks to the data science and supply chain communities

---

## 📚 References & Resources

- **ABC Analysis**:
- **Kraljic Matrix**: Kraljic, P. (1983). "Purchasing Must Become Supply Management"
- **EOQ Model**: Harris, F. W. (1913). "How Many Parts to Make at Once"
- **Inventory Optimization**: Silver, E. A., et al. (2016). "Inventory Management and Production Planning and Scheduling"

---

## 📊 Project Status

![Progress](https://img.shields.io/badge/Status-In%20Progress-yellow)

- [x] Project setup and structure
- [ ] Data loading and exploration
- [ ] Data cleaning and preprocessing
- [ ] KPI calculation
- [ ] ABC-XYZ segmentation
- [ ] Kraljic Matrix implementation
- [ ] EOQ/ROP optimization
- [ ] Before/after scenario analysis
- [ ] Power BI dashboard
- [ ] Final documentation

---

_Last Updated: January 2025_
