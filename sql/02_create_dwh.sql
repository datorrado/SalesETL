-- =============================================
-- Script: 02_create_dwh.sql
-- Description: Create data warehouse star schema
-- =============================================

-- Drop dwh schema if exists and create fresh
DROP SCHEMA IF EXISTS dwh CASCADE;
CREATE SCHEMA dwh;

-- =============================================
-- Dimension Tables
-- =============================================

-- Date Dimension
CREATE TABLE dwh.dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE INDEX idx_dim_date_full_date ON dwh.dim_date(full_date);
CREATE INDEX idx_dim_date_year_month ON dwh.dim_date(year, month);

COMMENT ON TABLE dwh.dim_date IS 'Date dimension for time-based analysis';

-- Customer Dimension
CREATE TABLE dwh.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    first_order_date DATE,
    last_order_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_customer_id ON dwh.dim_customer(customer_id);
CREATE INDEX idx_dim_customer_country ON dwh.dim_customer(country);

COMMENT ON TABLE dwh.dim_customer IS 'Customer dimension with SCD Type 1';

-- Product Dimension
CREATE TABLE dwh.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id INTEGER UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_product_id ON dwh.dim_product(product_id);
CREATE INDEX idx_dim_product_category ON dwh.dim_product(category);

COMMENT ON TABLE dwh.dim_product IS 'Product dimension with SCD Type 1';

-- =============================================
-- Fact Table
-- =============================================

-- Sales Fact Table
CREATE TABLE dwh.fact_sales (
    sales_key SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dwh.dim_date(date_id),
    customer_key INTEGER NOT NULL REFERENCES dwh.dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dwh.dim_product(product_key),
    order_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_sales_date ON dwh.fact_sales(date_key);
CREATE INDEX idx_fact_sales_customer ON dwh.fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON dwh.fact_sales(product_key);
CREATE INDEX idx_fact_sales_order_id ON dwh.fact_sales(order_id);

COMMENT ON TABLE dwh.fact_sales IS 'Sales fact table with measures and foreign keys to dimensions';
COMMENT ON COLUMN dwh.fact_sales.total_amount IS 'Calculated as quantity * unit_price';
