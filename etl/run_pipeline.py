"""
run_pipeline.py

Main ETL pipeline orchestrator that executes the full ETL process:
1. Creates staging tables
2. Creates data warehouse schema
3. Loads CSV data into staging
4. Transforms data from staging to DWH
"""

import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv
from load_staging import load_csv_to_staging

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


def execute_sql_file(conn, sql_file_path):
    """
    Execute a SQL file against the database.
    
    Args:
        conn: Database connection object
        sql_file_path (str): Path to the SQL file
    
    Raises:
        Exception: If SQL execution fails
    """
    try:
        logger.info(f"Executing SQL file: {os.path.basename(sql_file_path)}")
        
        # Read SQL file
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Create cursor
        cursor = conn.cursor()
        
        # Execute SQL
        cursor.execute(sql_content)
        
        # Commit transaction
        conn.commit()
        
        cursor.close()
        logger.info(f"Successfully executed: {os.path.basename(sql_file_path)}")
        
    except FileNotFoundError:
        logger.error(f"SQL file not found: {sql_file_path}")
        raise
    except Exception as e:
        logger.error(f"Error executing SQL file {sql_file_path}: {e}")
        conn.rollback()
        raise


def run_pipeline():
    """
    Execute the complete ETL pipeline.
    """
    conn = None
    
    try:
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sql_dir = os.path.join(project_root, 'sql')
        csv_path = os.path.join(project_root, 'data', 'sales.csv')
        
        logger.info("=" * 70)
        logger.info("STARTING ETL PIPELINE")
        logger.info("=" * 70)
        
        # Connect to database
        conn = get_db_connection()
        
        # Step 1: Create staging tables
        logger.info("\n[STEP 1/4] Creating staging tables...")
        staging_sql = os.path.join(sql_dir, '01_create_staging.sql')
        execute_sql_file(conn, staging_sql)
        
        # Step 2: Create data warehouse schema
        logger.info("\n[STEP 2/4] Creating data warehouse schema...")
        dwh_sql = os.path.join(sql_dir, '02_create_dwh.sql')
        execute_sql_file(conn, dwh_sql)
        
        # Step 3: Load CSV into staging
        logger.info("\n[STEP 3/4] Loading CSV data into staging...")
        records_loaded = load_csv_to_staging(csv_path, conn)
        
        # Step 4: Transform data into DWH
        logger.info("\n[STEP 4/4] Transforming data into data warehouse...")
        transform_sql = os.path.join(sql_dir, '03_transform.sql')
        execute_sql_file(conn, transform_sql)
        
        # Verify results
        logger.info("\n[VERIFICATION] Checking record counts...")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM staging.sales")
        staging_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dwh.dim_date")
        date_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dwh.dim_customer")
        customer_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dwh.dim_product")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM dwh.fact_sales")
        fact_count = cursor.fetchone()[0]
        
        cursor.close()
        
        logger.info("\n" + "=" * 70)
        logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info(f"  Staging records:      {staging_count}")
        logger.info(f"  Date dimension:       {date_count}")
        logger.info(f"  Customer dimension:   {customer_count}")
        logger.info(f"  Product dimension:    {product_count}")
        logger.info(f"  Fact sales records:   {fact_count}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"\nETL PIPELINE FAILED: {e}")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            logger.info("\nDatabase connection closed")


def main():
    """
    Main entry point for the ETL pipeline.
    """
    try:
        run_pipeline()
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
