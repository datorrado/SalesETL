# SalesETL - E-Commerce Data Warehouse ETL Pipeline

A complete end-to-end ETL (Extract, Transform, Load) pipeline that loads e-commerce sales data from CSV files into a PostgreSQL data warehouse with a star schema design.

## 🎯 Project Overview

This project demonstrates a Junior Data Engineering workflow that includes:
- Loading raw CSV data into staging tables
- Transforming data into a star schema (dimensional model)
- Data quality checks and logging
- Dockerized PostgreSQL database
- Automated pipeline execution

## 📁 Project Structure

```
SalesETL/
├── data/
│   └── sales.csv              # Sample e-commerce sales dataset
├── sql/
│   ├── 01_create_staging.sql  # Create staging tables
│   ├── 02_create_dwh.sql      # Create data warehouse schema
│   └── 03_transform.sql       # Transform staging to DWH
├── etl/
│   ├── load_staging.py        # Load CSV into staging tables
│   └── run_pipeline.py        # Main ETL orchestrator
├── notebooks/                  # For ad-hoc analysis (empty)
├── docker-compose.yml         # PostgreSQL container setup
├── requirements.txt           # Python dependencies
├── Makefile                   # Automation commands
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🗄️ Data Warehouse Schema

The data warehouse follows a **star schema** design:

### Dimension Tables
- **dim_date**: Date dimension with year, month, day, quarter, etc.
- **dim_customer**: Customer information (SCD Type 1)
- **dim_product**: Product catalog with categories
  
### Fact Table
- **fact_sales**: Sales transactions with measures (quantity, unit_price, total_amount)

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Make (optional, but recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/datorrado/SalesETL.git
cd SalesETL
```

### Step 2: Set Up Environment Variables

Copy the example environment file and update if needed:

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

To connect Power BI Desktop to the fact_sales table:

1. **Open Power BI Desktop**

2. **Get Data** → **PostgreSQL database**

3. **Enter Connection Details**:
   - Server: `localhost:5432`
   - Database: `sales_dwh`

4. **Database Credentials**:
   - User: `etl_user`
   - Password: `etl_password`

5. **Navigator**: Select tables from `dwh` schema:
   - `dim_date`
   - `dim_customer`
   - `dim_product`
   - `fact_sales`

6. **Load or Transform** the data

7. **Create Relationships** (if not auto-detected):
   - `fact_sales[date_key]` → `dim_date[date_id]`
   - `fact_sales[customer_key]` → `dim_customer[customer_key]`
   - `fact_sales[product_key]` → `dim_product[product_key]`

### Recommended Power BI Visualizations

- **Sales Over Time**: Line chart with date hierarchy
- **Sales by Category**: Pie or bar chart
- **Top Customers**: Table with customer name and revenue
- **Geographic Distribution**: Map visual with country and revenue
- **KPI Cards**: Total Revenue, Total Orders, Average Order Value

## 🛠️ Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make up` | Start PostgreSQL container |
| `make down` | Stop PostgreSQL container |
| `make etl` | Run the complete ETL pipeline |
| `make clean` | Stop containers and remove volumes |
| `make logs` | Show PostgreSQL logs |
| `make status` | Check container status |

## 🧹 Cleanup

To stop the database and remove all data:

```bash
make clean
```

Or using Docker Compose:
```bash
docker-compose down -v
```

## 📝 Sample Data

The `data/sales.csv` file contains 50 sample e-commerce orders with:
- **Order Information**: order_id, order_date
- **Customer Data**: customer_id, customer_name, country
- **Product Data**: product_id, product_name, category
- **Sales Metrics**: quantity, unit_price

## 🔧 Troubleshooting

### PostgreSQL Connection Issues

If you can't connect to PostgreSQL:

1. Check if the container is running:
   ```bash
   make status
   ```

2. Check logs:
   ```bash
   make logs
   ```

3. Verify the port 5432 is not in use:
   ```bash
   lsof -i :5432
   ```

### ETL Pipeline Errors

- Ensure `.env` file exists with correct credentials
- Verify PostgreSQL is running and healthy
- Check Python dependencies are installed
- Review logs for detailed error messages

## 📚 Technologies Used

- **Python 3.12**: ETL scripting and data processing
- **PostgreSQL 15**: Data warehouse database
- **Docker**: Containerization
- **pandas**: CSV data handling
- **psycopg2**: PostgreSQL database adapter
- **python-dotenv**: Environment variable management

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ ETL pipeline development
- ✅ Star schema design (dimensional modeling)
- ✅ SQL DDL and DML operations
- ✅ Python database connectivity
- ✅ Docker containerization
- ✅ Environment configuration
- ✅ Logging and error handling
- ✅ Automation with Makefiles

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Created as a Junior Data Engineering portfolio project.