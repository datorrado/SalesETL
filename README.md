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

Default configuration:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_dwh
DB_USER=etl_user
DB_PASSWORD=etl_password
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start PostgreSQL

Using Make:
```bash
make up
```

Or using Docker Compose directly:
```bash
docker-compose up -d
```

Wait a few seconds for PostgreSQL to be ready.

### Step 5: Run the ETL Pipeline

Using Make:
```bash
make etl
```

Or run Python directly:
```bash
python3 etl/run_pipeline.py
```

## 📊 Pipeline Steps

The ETL pipeline executes the following steps:

1. **Create Staging Tables** - Creates `staging.sales` table
2. **Create Data Warehouse Schema** - Creates dimension and fact tables
3. **Load Staging** - Loads CSV data into staging tables
4. **Transform Data** - Transforms and loads data into the star schema

## ✅ Verify Results

### Using PostgreSQL Client

Connect to the database:
```bash
docker exec -it sales_etl_postgres psql -U etl_user -d sales_dwh
```

### Sample Queries

#### Check Record Counts
```sql
-- Staging table
SELECT COUNT(*) FROM staging.sales;

-- Dimensions
SELECT COUNT(*) FROM dwh.dim_date;
SELECT COUNT(*) FROM dwh.dim_customer;
SELECT COUNT(*) FROM dwh.dim_product;

-- Fact table
SELECT COUNT(*) FROM dwh.fact_sales;
```

#### Sales by Category
```sql
SELECT 
    p.category,
    COUNT(*) as order_count,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_amount) as total_revenue
FROM dwh.fact_sales f
JOIN dwh.dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;
```

#### Sales by Country
```sql
SELECT 
    c.country,
    COUNT(DISTINCT c.customer_key) as customer_count,
    SUM(f.total_amount) as total_revenue
FROM dwh.fact_sales f
JOIN dwh.dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
ORDER BY total_revenue DESC;
```

#### Monthly Sales Trend
```sql
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(*) as order_count,
    SUM(f.total_amount) as total_revenue
FROM dwh.fact_sales f
JOIN dwh.dim_date d ON f.date_key = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;
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
