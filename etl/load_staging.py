"""
load_staging.py

Loads CSV data into PostgreSQL staging tables.
"""

import os
import sys
import logging
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Create and return a database connection using environment variables.
    
    Returns:
        psycopg2.connection: Database connection object
    
    Raises:
        Exception: If connection fails
    """
    try:
        # Load environment variables
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'sales_dwh'),
            user=os.getenv('DB_USER', 'etl_user'),
            password=os.getenv('DB_PASSWORD', 'etl_password')
        )
        logger.info("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def load_csv_to_staging(csv_path, conn):
    """
    Load CSV data into staging.sales table.
    
    Args:
        csv_path (str): Path to the CSV file
        conn: Database connection object
    
    Returns:
        int: Number of records loaded
    
    Raises:
        Exception: If loading fails
    """
    try:
        # Read CSV file
        logger.info(f"Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"CSV file loaded with {len(df)} records")
        
        # Convert order_date to proper date format
        df['order_date'] = pd.to_datetime(df['order_date']).dt.date
        
        # Create cursor
        cursor = conn.cursor()
        
        # Truncate staging table before loading
        logger.info("Truncating staging.sales table")
        cursor.execute("TRUNCATE TABLE staging.sales;")
        
        # Insert data row by row (for small datasets)
        # For larger datasets, consider using COPY command
        insert_query = """
            INSERT INTO staging.sales (
                order_id, order_date, customer_id, customer_name,
                product_id, product_name, category, country,
                quantity, unit_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records_loaded = 0
        for idx, row in df.iterrows():
            cursor.execute(insert_query, (
                int(row['order_id']),
                row['order_date'],
                int(row['customer_id']),
                row['customer_name'],
                int(row['product_id']),
                row['product_name'],
                row['category'],
                row['country'],
                int(row['quantity']),
                float(row['unit_price'])
            ))
            records_loaded += 1
            
            # Log progress every 10 records
            if records_loaded % 10 == 0:
                logger.debug(f"Loaded {records_loaded} records...")
        
        # Commit transaction
        conn.commit()
        logger.info(f"Successfully loaded {records_loaded} records into staging.sales")
        
        cursor.close()
        return records_loaded
        
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV to staging: {e}")
        conn.rollback()
        raise


def main():
    """
    Main function to execute the staging load process.
    """
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(project_root, 'data', 'sales.csv')
        
        logger.info("=" * 60)
        logger.info("Starting ETL - Load Staging Process")
        logger.info("=" * 60)
        
        # Check if CSV file exists
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found at: {csv_path}")
            sys.exit(1)
        
        # Connect to database
        conn = get_db_connection()
        
        # Load CSV to staging
        records_loaded = load_csv_to_staging(csv_path, conn)
        
        # Close connection
        conn.close()
        logger.info("Database connection closed")
        
        logger.info("=" * 60)
        logger.info(f"ETL Load Staging completed successfully! {records_loaded} records loaded.")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"ETL Load Staging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
