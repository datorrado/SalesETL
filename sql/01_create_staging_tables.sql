-- Staging Tables Schema
-- These tables will hold raw data loaded from CSV files

-- Drop existing staging tables if they exist
DROP TABLE IF EXISTS staging.orders CASCADE;
DROP TABLE IF EXISTS staging.customers CASCADE;
DROP TABLE IF EXISTS staging.products CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;

-- Create staging schema
CREATE SCHEMA IF NOT EXISTS staging;

-- Staging table for customers
CREATE TABLE staging.customers (
    customer_id INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    signup_date DATE
);

-- Staging table for products
CREATE TABLE staging.products (
    product_id INTEGER,
    product_name VARCHAR(255),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_price DECIMAL(10, 2),
    cost_price DECIMAL(10, 2),
    stock_quantity INTEGER
);

-- Staging table for orders
CREATE TABLE staging.orders (
    order_id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    order_date DATE,
    quantity INTEGER,
    discount_percent DECIMAL(5, 2),
    shipping_cost DECIMAL(10, 2),
    payment_method VARCHAR(50),
    order_status VARCHAR(50)
);

-- Create indexes on staging tables for better performance during transformation
CREATE INDEX idx_staging_orders_customer ON staging.orders(customer_id);
CREATE INDEX idx_staging_orders_product ON staging.orders(product_id);
CREATE INDEX idx_staging_orders_date ON staging.orders(order_date);
