-- Star Schema (Data Warehouse) Schema
-- This implements a dimensional model with fact and dimension tables

-- Drop existing warehouse tables if they exist
DROP TABLE IF EXISTS warehouse.fact_sales CASCADE;
DROP TABLE IF EXISTS warehouse.dim_customer CASCADE;
DROP TABLE IF EXISTS warehouse.dim_product CASCADE;
DROP TABLE IF EXISTS warehouse.dim_date CASCADE;
DROP TABLE IF EXISTS warehouse.dim_payment CASCADE;
DROP SCHEMA IF EXISTS warehouse CASCADE;

-- Create warehouse schema
CREATE SCHEMA IF NOT EXISTS warehouse;

-- Dimension: Customer
CREATE TABLE warehouse.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    signup_date DATE,
    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,
    UNIQUE(customer_id, is_current)
);

-- Dimension: Product
CREATE TABLE warehouse.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_price DECIMAL(10, 2),
    cost_price DECIMAL(10, 2),
    margin_amount DECIMAL(10, 2),
    margin_percent DECIMAL(5, 2),
    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,
    UNIQUE(product_id, is_current)
);

-- Dimension: Date
CREATE TABLE warehouse.dim_date (
    date_key SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    day INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    day_of_week INTEGER,
    day_name VARCHAR(20),
    month_name VARCHAR(20),
    is_weekend BOOLEAN,
    week_of_year INTEGER
);

-- Dimension: Payment Method
CREATE TABLE warehouse.dim_payment (
    payment_key SERIAL PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL UNIQUE,
    payment_type VARCHAR(50)
);

-- Fact Table: Sales
CREATE TABLE warehouse.fact_sales (
    sales_key SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    customer_key INTEGER NOT NULL REFERENCES warehouse.dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES warehouse.dim_product(product_key),
    date_key INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
    payment_key INTEGER NOT NULL REFERENCES warehouse.dim_payment(payment_key),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2),
    shipping_cost DECIMAL(10, 2),
    gross_amount DECIMAL(10, 2),
    net_amount DECIMAL(10, 2),
    cost_amount DECIMAL(10, 2),
    profit_amount DECIMAL(10, 2),
    order_status VARCHAR(50),
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_fact_sales_customer ON warehouse.fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON warehouse.fact_sales(product_key);
CREATE INDEX idx_fact_sales_date ON warehouse.fact_sales(date_key);
CREATE INDEX idx_fact_sales_payment ON warehouse.fact_sales(payment_key);
CREATE INDEX idx_fact_sales_order ON warehouse.fact_sales(order_id);

-- Create indexes on dimension tables
CREATE INDEX idx_dim_customer_id ON warehouse.dim_customer(customer_id);
CREATE INDEX idx_dim_product_id ON warehouse.dim_product(product_id);
CREATE INDEX idx_dim_date_date ON warehouse.dim_date(date);
