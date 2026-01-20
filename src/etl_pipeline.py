"""
Main ETL Pipeline Orchestrator
Coordinates the complete ETL process from CSV to Data Warehouse
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db_connection import DatabaseConnection
from load_staging import StagingLoader
from transform_warehouse import WarehouseTransformer


def print_banner(text):
    """Print a formatted banner."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_etl_pipeline():
    """Execute the complete ETL pipeline."""
    start_time = datetime.now()
    
    print_banner("SALES DATA WAREHOUSE - ETL PIPELINE")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize database connection
    db = DatabaseConnection()
    
    # Step 1: Create database
    print_banner("STEP 1: DATABASE INITIALIZATION")
    if not db.create_database(db.database):
        print("✗ Failed to create database. Exiting.")
        return False
    
    # Connect to database
    if not db.connect():
        print("✗ Failed to connect to database. Exiting.")
        return False
    
    try:
        # Step 2: Create staging tables and load data
        print_banner("STEP 2: STAGING LAYER - CREATE & LOAD")
        
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'sql', '01_create_staging_tables.sql'
        )
        
        print("Creating staging tables...")
        if not db.execute_script(script_path):
            print("✗ Failed to create staging tables")
            return False
        print()
        
        loader = StagingLoader(db)
        if not loader.load_all_staging():
            print("✗ Failed to load staging data")
            return False
        
        loader.verify_staging_data()
        
        # Step 3: Create warehouse schema
        print_banner("STEP 3: WAREHOUSE LAYER - CREATE SCHEMA")
        
        transformer = WarehouseTransformer(db)
        if not transformer.create_warehouse_schema():
            print("✗ Failed to create warehouse schema")
            return False
        
        # Step 4: Transform and load data to warehouse
        print_banner("STEP 4: WAREHOUSE LAYER - TRANSFORM & LOAD")
        
        if not transformer.transform_to_warehouse():
            print("✗ Failed to transform data to warehouse")
            return False
        
        # Step 5: Verify and show results
        print_banner("STEP 5: VERIFICATION & RESULTS")
        
        transformer.verify_warehouse_data()
        transformer.show_sample_data()
        
        # Success summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_banner("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration:.2f} seconds")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during ETL pipeline: {e}")
        return False
    
    finally:
        db.close()


def main():
    """Main entry point."""
    success = run_etl_pipeline()
    
    if success:
        print("=" * 70)
        print("  Next Steps:")
        print("  - Connect Power BI to PostgreSQL database")
        print("  - Use warehouse.fact_sales as your main data source")
        print("  - Join with dimension tables for rich analytics")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n✗ ETL pipeline failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
