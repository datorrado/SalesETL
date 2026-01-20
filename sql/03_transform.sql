-- =============================================
-- Script: 03_transform.sql
-- Description: Transform data from staging to DWH
-- =============================================

-- =============================================
-- Step 1: Populate Date Dimension
-- =============================================

INSERT INTO dwh.dim_date (
    full_date,
    year,
    quarter,
    month,
    month_name,
    day,
    day_of_week,
    day_name,
    week_of_year,
    is_weekend
)
SELECT DISTINCT
    order_date AS full_date,
    EXTRACT(YEAR FROM order_date) AS year,
    EXTRACT(QUARTER FROM order_date) AS quarter,
    EXTRACT(MONTH FROM order_date) AS month,
    TO_CHAR(order_date, 'Month') AS month_name,
    EXTRACT(DAY FROM order_date) AS day,
    EXTRACT(DOW FROM order_date) AS day_of_week,
    TO_CHAR(order_date, 'Day') AS day_name,
    EXTRACT(WEEK FROM order_date) AS week_of_year,
    CASE WHEN EXTRACT(DOW FROM order_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM staging.sales
ON CONFLICT (full_date) DO NOTHING;

-- =============================================
-- Step 2: Populate Customer Dimension
-- =============================================

INSERT INTO dwh.dim_customer (
    customer_id,
    customer_name,
    country,
    first_order_date,
    last_order_date
)
SELECT
    customer_id,
    MAX(customer_name) AS customer_name,  -- Use MAX to handle any inconsistencies
    MAX(country) AS country,  -- Use MAX assuming customer has one country
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS last_order_date
FROM staging.sales
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE SET
    customer_name = EXCLUDED.customer_name,
    country = EXCLUDED.country,
    last_order_date = EXCLUDED.last_order_date,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================
-- Step 3: Populate Product Dimension
-- =============================================

INSERT INTO dwh.dim_product (
    product_id,
    product_name,
    category
)
SELECT DISTINCT
    product_id,
    product_name,
    category
FROM staging.sales
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name,
    category = EXCLUDED.category,
    updated_at = CURRENT_TIMESTAMP;

-- =============================================
-- Step 4: Populate Fact Table
-- =============================================

INSERT INTO dwh.fact_sales (
    date_key,
    customer_key,
    product_key,
    order_id,
    quantity,
    unit_price,
    total_amount
)
SELECT
    dd.date_id AS date_key,
    dc.customer_key,
    dp.product_key,
    s.order_id,
    s.quantity,
    s.unit_price,
    s.quantity * s.unit_price AS total_amount
FROM staging.sales s
INNER JOIN dwh.dim_date dd ON s.order_date = dd.full_date
INNER JOIN dwh.dim_customer dc ON s.customer_id = dc.customer_id
INNER JOIN dwh.dim_product dp ON s.product_id = dp.product_id;

-- =============================================
-- Verification Queries (for logging/debugging)
-- =============================================

-- Count records in each table
DO $$
DECLARE
    staging_count INTEGER;
    date_count INTEGER;
    customer_count INTEGER;
    product_count INTEGER;
    fact_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO staging_count FROM staging.sales;
    SELECT COUNT(*) INTO date_count FROM dwh.dim_date;
    SELECT COUNT(*) INTO customer_count FROM dwh.dim_customer;
    SELECT COUNT(*) INTO product_count FROM dwh.dim_product;
    SELECT COUNT(*) INTO fact_count FROM dwh.fact_sales;
    
    RAISE NOTICE 'Transformation Summary:';
    RAISE NOTICE '  Staging records: %', staging_count;
    RAISE NOTICE '  Date dimension: %', date_count;
    RAISE NOTICE '  Customer dimension: %', customer_count;
    RAISE NOTICE '  Product dimension: %', product_count;
    RAISE NOTICE '  Fact sales: %', fact_count;
END $$;
