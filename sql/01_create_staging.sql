-- =============================================
-- Script: 01_create_staging.sql
-- Description: Create staging tables for raw data
-- =============================================

-- Drop staging schema if exists and create fresh
DROP SCHEMA IF EXISTS staging CASCADE;
CREATE SCHEMA staging;

-- Create staging table for sales data
-- This table mirrors the structure of the CSV file
CREATE TABLE staging.sales (
    order_id INTEGER,
    order_date DATE,
    customer_id INTEGER,
    customer_name VARCHAR(255),
    product_id INTEGER,
    product_name VARCHAR(255),
    category VARCHAR(100),
    country VARCHAR(100),
    quantity INTEGER,
    unit_price NUMERIC(10, 2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better performance during transformation
CREATE INDEX idx_staging_sales_order_date ON staging.sales(order_date);
CREATE INDEX idx_staging_sales_customer_id ON staging.sales(customer_id);
CREATE INDEX idx_staging_sales_product_id ON staging.sales(product_id);

COMMENT ON TABLE staging.sales IS 'Staging table for raw sales data from CSV';
COMMENT ON COLUMN staging.sales.loaded_at IS 'Timestamp when the record was loaded';
