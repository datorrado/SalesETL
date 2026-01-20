-- ETL Transformations: Load data from staging to warehouse
-- This script transforms and loads data into the star schema

-- =====================================================
-- 1. Load Dimension: Customer
-- =====================================================
INSERT INTO warehouse.dim_customer (
    customer_id,
    first_name,
    last_name,
    full_name,
    email,
    phone,
    city,
    state,
    country,
    signup_date
)
SELECT DISTINCT
    customer_id,
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) AS full_name,
    email,
    phone,
    city,
    state,
    country,
    signup_date
FROM staging.customers
ON CONFLICT (customer_id, is_current) 
DO NOTHING;

-- =====================================================
-- 2. Load Dimension: Product
-- =====================================================
INSERT INTO warehouse.dim_product (
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    cost_price,
    margin_amount,
    margin_percent
)
SELECT DISTINCT
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    cost_price,
    unit_price - cost_price AS margin_amount,
    CASE 
        WHEN unit_price > 0 THEN ((unit_price - cost_price) / unit_price) * 100
        ELSE 0
    END AS margin_percent
FROM staging.products
ON CONFLICT (product_id, is_current) 
DO NOTHING;

-- =====================================================
-- 3. Load Dimension: Date
-- =====================================================
INSERT INTO warehouse.dim_date (
    date,
    day,
    month,
    quarter,
    year,
    day_of_week,
    day_name,
    month_name,
    is_weekend,
    week_of_year
)
SELECT DISTINCT
    order_date AS date,
    EXTRACT(DAY FROM order_date) AS day,
    EXTRACT(MONTH FROM order_date) AS month,
    EXTRACT(QUARTER FROM order_date) AS quarter,
    EXTRACT(YEAR FROM order_date) AS year,
    EXTRACT(DOW FROM order_date) AS day_of_week,
    TO_CHAR(order_date, 'Day') AS day_name,
    TO_CHAR(order_date, 'Month') AS month_name,
    CASE WHEN EXTRACT(DOW FROM order_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend,
    EXTRACT(WEEK FROM order_date) AS week_of_year
FROM staging.orders
ON CONFLICT (date) 
DO NOTHING;

-- =====================================================
-- 4. Load Dimension: Payment Method
-- =====================================================
INSERT INTO warehouse.dim_payment (
    payment_method,
    payment_type
)
SELECT DISTINCT
    payment_method,
    CASE 
        WHEN payment_method IN ('Credit Card', 'Debit Card') THEN 'Card'
        WHEN payment_method = 'PayPal' THEN 'Digital Wallet'
        ELSE 'Other'
    END AS payment_type
FROM staging.orders
ON CONFLICT (payment_method) 
DO NOTHING;

-- =====================================================
-- 5. Load Fact Table: Sales
-- =====================================================
INSERT INTO warehouse.fact_sales (
    order_id,
    customer_key,
    product_key,
    date_key,
    payment_key,
    quantity,
    unit_price,
    discount_percent,
    discount_amount,
    shipping_cost,
    gross_amount,
    net_amount,
    cost_amount,
    profit_amount,
    order_status
)
SELECT 
    o.order_id,
    dc.customer_key,
    dp.product_key,
    dd.date_key,
    dpm.payment_key,
    o.quantity,
    p.unit_price,
    o.discount_percent,
    (p.unit_price * o.quantity * o.discount_percent / 100) AS discount_amount,
    o.shipping_cost,
    (p.unit_price * o.quantity) AS gross_amount,
    (p.unit_price * o.quantity * (1 - o.discount_percent / 100)) + o.shipping_cost AS net_amount,
    (p.cost_price * o.quantity) AS cost_amount,
    ((p.unit_price * o.quantity * (1 - o.discount_percent / 100)) - (p.cost_price * o.quantity)) AS profit_amount,
    o.order_status
FROM staging.orders o
INNER JOIN warehouse.dim_customer dc ON o.customer_id = dc.customer_id AND dc.is_current = TRUE
INNER JOIN warehouse.dim_product dp ON o.product_id = dp.product_id AND dp.is_current = TRUE
INNER JOIN warehouse.dim_date dd ON o.order_date = dd.date
INNER JOIN warehouse.dim_payment dpm ON o.payment_method = dpm.payment_method
INNER JOIN staging.products p ON o.product_id = p.product_id
WHERE NOT EXISTS (
    SELECT 1 FROM warehouse.fact_sales fs WHERE fs.order_id = o.order_id
);
