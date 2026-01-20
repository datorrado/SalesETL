# Sales Data Warehouse ETL Pipeline

A junior data engineering project demonstrating a complete ETL pipeline for a retail/e-commerce sales data warehouse using PostgreSQL, SQL, and Python.

## 📋 Project Overview

This project implements a dimensional data warehouse for sales analytics using a star schema design. It includes:

- **Sample retail/e-commerce datasets** (customers, products, orders)
- **Staging layer** for raw data ingestion
- **Star schema warehouse** with fact and dimension tables
- **Python ETL pipeline** for automated data loading and transformation
- **Power BI connectivity** for business intelligence reporting

## 🏗️ Architecture

```
CSV Files (data/)
    ↓
Staging Tables (staging schema)
    ↓
Transformations (SQL)
    ↓
Data Warehouse (warehouse schema)
    ↓
Power BI / Analytics Tools
```

### Data Model

**Star Schema Components:**

**Fact Table:**
- `fact_sales` - Contains sales transactions with measures (quantity, amounts, profit)

**Dimension Tables:**
- `dim_customer` - Customer information
- `dim_product` - Product catalog with pricing and margins
- `dim_date` - Date dimension with calendar attributes
- `dim_payment` - Payment method types

## 📁 Project Structure

```
SalesETL/
├── data/                          # Sample CSV datasets
│   ├── customers.csv             # Customer information
│   ├── products.csv              # Product catalog
│   └── orders.csv                # Order transactions
├── sql/                           # SQL scripts
│   ├── 01_create_staging_tables.sql      # Staging schema
│   ├── 02_create_warehouse_schema.sql    # Star schema
│   └── 03_transform_to_warehouse.sql     # ETL transformations
├── src/                           # Python ETL code
│   ├── db_connection.py          # Database utilities
│   ├── load_staging.py           # Staging loader
│   ├── transform_warehouse.py    # Warehouse transformer
│   └── etl_pipeline.py           # Main orchestrator
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment configuration template
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites

- **PostgreSQL** 12+ installed and running
- **Python** 3.8+ installed
- **pip** package manager

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/datorrado/SalesETL.git
cd SalesETL
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure database connection:**
```bash
cp .env.example .env
```

Edit `.env` file with your PostgreSQL credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_dw
DB_USER=postgres
DB_PASSWORD=your_password
```

### Running the ETL Pipeline

**Option 1: Run complete pipeline (recommended)**
```bash
python src/etl_pipeline.py
```

This will:
1. Create the database (if it doesn't exist)
2. Create staging tables and load CSV data
3. Create warehouse schema (star schema)
4. Transform and load data into warehouse
5. Verify data and show sample results

**Option 2: Run individual steps**

Load staging tables only:
```bash
python src/load_staging.py
```

Transform to warehouse only (after staging is loaded):
```bash
python src/transform_warehouse.py
```

## 📊 Sample Data

The project includes realistic sample data:

- **20 customers** across various US cities
- **20 products** in categories (Electronics, Furniture, Stationery)
- **50 orders** with transactions from July-August 2023

You can modify the CSV files in the `data/` directory to use your own data.

## 🔍 Querying the Data Warehouse

### Connect to PostgreSQL

```bash
psql -h localhost -U postgres -d sales_dw
```

### Example Queries

**Total sales by product category:**
```sql
SELECT 
    dp.category,
    SUM(fs.net_amount) as total_sales,
    SUM(fs.profit_amount) as total_profit,
    COUNT(*) as order_count
FROM warehouse.fact_sales fs
JOIN warehouse.dim_product dp ON fs.product_key = dp.product_key
GROUP BY dp.category
ORDER BY total_sales DESC;
```

**Monthly sales trend:**
```sql
SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    SUM(fs.net_amount) as monthly_sales,
    COUNT(DISTINCT fs.order_id) as order_count
FROM warehouse.fact_sales fs
JOIN warehouse.dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;
```

**Top customers by revenue:**
```sql
SELECT 
    dc.full_name,
    dc.city,
    dc.state,
    SUM(fs.net_amount) as total_spent,
    COUNT(DISTINCT fs.order_id) as order_count
FROM warehouse.fact_sales fs
JOIN warehouse.dim_customer dc ON fs.customer_key = dc.customer_key
GROUP BY dc.full_name, dc.city, dc.state
ORDER BY total_spent DESC
LIMIT 10;
```

## 📈 Connecting Power BI

### Step 1: Install PostgreSQL Connector

In Power BI Desktop:
1. Go to **Get Data** → **Database** → **PostgreSQL database**
2. If prompted, install the PostgreSQL connector

### Step 2: Connect to Database

1. **Server:** `localhost:5432`
2. **Database:** `sales_dw`
3. **Data Connectivity mode:** Import (recommended) or DirectQuery

### Step 3: Authenticate

- **User name:** `postgres` (or your DB user)
- **Password:** Your PostgreSQL password

### Step 4: Load Tables

Select tables from the `warehouse` schema:
- ✅ `fact_sales` (main fact table)
- ✅ `dim_customer`
- ✅ `dim_product`
- ✅ `dim_date`
- ✅ `dim_payment`

### Step 5: Create Relationships (if not auto-detected)

Power BI should automatically detect relationships based on foreign keys:

```
fact_sales.customer_key → dim_customer.customer_key
fact_sales.product_key  → dim_product.product_key
fact_sales.date_key     → dim_date.date_key
fact_sales.payment_key  → dim_payment.payment_key
```

### Step 6: Build Visualizations

**Suggested measures to create:**
- Total Sales: `SUM(fact_sales[net_amount])`
- Total Profit: `SUM(fact_sales[profit_amount])`
- Profit Margin: `SUM(fact_sales[profit_amount]) / SUM(fact_sales[net_amount])`
- Order Count: `DISTINCTCOUNT(fact_sales[order_id])`

**Suggested visualizations:**
- Sales by Category (Column Chart)
- Monthly Sales Trend (Line Chart)
- Top Products by Revenue (Bar Chart)
- Customer Geographic Distribution (Map)
- Profit Margin by Product (KPI Cards)

## 🛠️ Database Schema Details

### Staging Schema (`staging`)

Raw data landing zone with minimal transformation:
- `staging.customers` - Customer master data
- `staging.products` - Product catalog
- `staging.orders` - Order transactions

### Warehouse Schema (`warehouse`)

Optimized star schema for analytics:

**Dimensions:**
- `dim_customer` - SCD Type 1 customer dimension
- `dim_product` - Product dimension with margin calculations
- `dim_date` - Calendar dimension with attributes
- `dim_payment` - Payment method lookup

**Fact:**
- `fact_sales` - Grain: One row per order line
  - Measures: quantity, amounts, costs, profit
  - Foreign keys to all dimensions

## 🔄 ETL Process Details

### Extract
- Reads CSV files from `data/` directory
- Uses pandas for data handling
- Validates data structure

### Load (Staging)
- Truncates existing staging tables
- Bulk loads data into PostgreSQL
- Creates indexes for transformation performance

### Transform
- Populates dimension tables with business logic
- Calculates derived metrics (margins, profits)
- Loads fact table with denormalized measures
- Enforces referential integrity

## 📝 Notes for Developers

### Extending the Pipeline

**Add new data sources:**
1. Create new CSV file in `data/`
2. Add staging table in `01_create_staging_tables.sql`
3. Update `load_staging.py` to include new file
4. Modify warehouse schema if needed

**Add new dimensions/facts:**
1. Update `02_create_warehouse_schema.sql`
2. Add transformation logic in `03_transform_to_warehouse.sql`
3. Test queries before running pipeline

### Error Handling

The ETL pipeline includes:
- Database connection validation
- Transaction rollback on errors
- Detailed error messages
- Step-by-step progress tracking

## 🎯 Learning Objectives

This project demonstrates:

✅ **Data Modeling** - Star schema design for analytics  
✅ **SQL Skills** - DDL, DML, joins, aggregations, window functions  
✅ **Python ETL** - pandas, psycopg2, modular code design  
✅ **Database Design** - Schemas, indexes, constraints  
✅ **Data Pipeline** - Staging → Transformation → Warehouse  
✅ **BI Integration** - Connecting analytics tools to data warehouse

## 🤝 Contributing

This is a learning project. Feel free to:
- Add more sample data
- Extend the data model
- Add data quality checks
- Implement scheduling (Airflow, cron)
- Add unit tests

## 📄 License

This project is open source and available for educational purposes.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Happy Data Engineering! 🚀**