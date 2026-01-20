"""
ETL module for loading data from CSV files into staging tables.
Handles the Extract and Load phases of the ETL pipeline.
"""

import pandas as pd
import os
from psycopg2.extras import execute_batch
from db_connection import DatabaseConnection


class StagingLoader:
    """Loads CSV data into staging tables."""
    
    def __init__(self, db_connection):
        """
        Initialize staging loader.
        
        Args:
            db_connection: DatabaseConnection object
        """
        self.db = db_connection
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    def load_csv_to_staging(self, csv_file, table_name):
        """
        Load data from CSV file into staging table.
        
        Args:
            csv_file: Name of CSV file
            table_name: Name of staging table (without schema)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            csv_path = os.path.join(self.data_dir, csv_file)
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            print(f"✓ Read {len(df)} rows from {csv_file}")
            
            # Clear existing data in staging table
            clear_query = f"TRUNCATE TABLE staging.{table_name} CASCADE;"
            self.db.execute_query(clear_query)
            
            # Insert data into staging table
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO staging.{table_name} ({columns}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples
            records = [tuple(row) for row in df.values]
            
            # Batch insert using execute_batch for better performance
            execute_batch(self.db.cursor, insert_query, records, page_size=100)
            
            self.db.connection.commit()
            print(f"✓ Loaded {len(records)} rows into staging.{table_name}")
            return True
            
        except Exception as e:
            print(f"✗ Error loading {csv_file} to staging.{table_name}: {e}")
            self.db.connection.rollback()
            return False
    
    def load_all_staging(self):
        """Load all CSV files into their respective staging tables."""
        print("\n" + "="*60)
        print("LOADING DATA INTO STAGING TABLES")
        print("="*60 + "\n")
        
        files_and_tables = [
            ('customers.csv', 'customers'),
            ('products.csv', 'products'),
            ('orders.csv', 'orders')
        ]
        
        success_count = 0
        for csv_file, table_name in files_and_tables:
            if self.load_csv_to_staging(csv_file, table_name):
                success_count += 1
            print()
        
        print(f"✓ Successfully loaded {success_count}/{len(files_and_tables)} staging tables")
        return success_count == len(files_and_tables)
    
    def verify_staging_data(self):
        """Verify data loaded in staging tables."""
        print("\n" + "="*60)
        print("VERIFYING STAGING DATA")
        print("="*60 + "\n")
        
        tables = ['customers', 'products', 'orders']
        
        for table in tables:
            query = f"SELECT COUNT(*) FROM staging.{table}"
            result = self.db.fetch_all(query)
            if result:
                count = result[0][0]
                print(f"✓ staging.{table}: {count} rows")
        
        print()


def main():
    """Main function to run staging load."""
    print("\n" + "="*60)
    print("ETL PIPELINE - STAGING LOAD")
    print("="*60 + "\n")
    
    # Create database connection
    db = DatabaseConnection()
    
    # Create database if it doesn't exist
    db.create_database(db.database)
    
    # Connect to database
    if not db.connect():
        print("✗ Failed to connect to database")
        return
    
    try:
        # Create staging schema and tables
        script_path = os.path.join(
            os.path.dirname(__file__), '..', 'sql', '01_create_staging_tables.sql'
        )
        print("Creating staging tables...")
        if not db.execute_script(script_path):
            print("✗ Failed to create staging tables")
            return
        print()
        
        # Load data into staging
        loader = StagingLoader(db)
        if loader.load_all_staging():
            loader.verify_staging_data()
            print("✓ Staging load completed successfully!")
        else:
            print("✗ Staging load failed")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
