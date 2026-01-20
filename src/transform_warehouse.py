"""
ETL module for transforming data from staging to warehouse.
Handles the Transform phase of the ETL pipeline.
"""

import os
from db_connection import DatabaseConnection


class WarehouseTransformer:
    """Transforms and loads data from staging to warehouse."""
    
    def __init__(self, db_connection):
        """
        Initialize warehouse transformer.
        
        Args:
            db_connection: DatabaseConnection object
        """
        self.db = db_connection
        self.sql_dir = os.path.join(os.path.dirname(__file__), '..', 'sql')
    
    def create_warehouse_schema(self):
        """Create warehouse schema and tables."""
        print("\n" + "="*60)
        print("CREATING WAREHOUSE SCHEMA")
        print("="*60 + "\n")
        
        script_path = os.path.join(self.sql_dir, '02_create_warehouse_schema.sql')
        
        if self.db.execute_script(script_path):
            print("✓ Warehouse schema created successfully\n")
            return True
        else:
            print("✗ Failed to create warehouse schema\n")
            return False
    
    def transform_to_warehouse(self):
        """Execute transformation script to load data into warehouse."""
        print("="*60)
        print("TRANSFORMING DATA TO WAREHOUSE")
        print("="*60 + "\n")
        
        script_path = os.path.join(self.sql_dir, '03_transform_to_warehouse.sql')
        
        if self.db.execute_script(script_path):
            print("\n✓ Data transformation completed successfully\n")
            return True
        else:
            print("\n✗ Data transformation failed\n")
            return False
    
    def verify_warehouse_data(self):
        """Verify data loaded in warehouse tables."""
        print("="*60)
        print("VERIFYING WAREHOUSE DATA")
        print("="*60 + "\n")
        
        tables = [
            ('dim_customer', 'Dimension: Customer'),
            ('dim_product', 'Dimension: Product'),
            ('dim_date', 'Dimension: Date'),
            ('dim_payment', 'Dimension: Payment'),
            ('fact_sales', 'Fact: Sales')
        ]
        
        for table, description in tables:
            query = f"SELECT COUNT(*) FROM warehouse.{table}"
            result = self.db.fetch_all(query)
            if result:
                count = result[0][0]
                print(f"✓ {description:30s} ({table:20s}): {count:5d} rows")
        
        print()
    
    def show_sample_data(self):
        """Show sample data from fact table."""
        print("="*60)
        print("SAMPLE DATA FROM FACT_SALES")
        print("="*60 + "\n")
        
        query = """
        SELECT 
            fs.order_id,
            dc.full_name AS customer,
            dp.product_name,
            dd.date,
            fs.quantity,
            fs.net_amount,
            fs.profit_amount
        FROM warehouse.fact_sales fs
        JOIN warehouse.dim_customer dc ON fs.customer_key = dc.customer_key
        JOIN warehouse.dim_product dp ON fs.product_key = dp.product_key
        JOIN warehouse.dim_date dd ON fs.date_key = dd.date_key
        ORDER BY fs.order_id
        LIMIT 5;
        """
        
        result = self.db.fetch_all(query)
        if result:
            print(f"{'Order ID':<10} {'Customer':<20} {'Product':<25} {'Date':<12} {'Qty':<5} {'Net Amt':<10} {'Profit':<10}")
            print("-" * 100)
            for row in result:
                print(f"{row[0]:<10} {row[1]:<20} {row[2]:<25} {str(row[3]):<12} {row[4]:<5} ${row[5]:<9.2f} ${row[6]:<9.2f}")
        
        print()


def main():
    """Main function to run warehouse transformation."""
    print("\n" + "="*60)
    print("ETL PIPELINE - WAREHOUSE TRANSFORMATION")
    print("="*60 + "\n")
    
    # Create database connection
    db = DatabaseConnection()
    
    if not db.connect():
        print("✗ Failed to connect to database")
        return
    
    try:
        # Create transformer
        transformer = WarehouseTransformer(db)
        
        # Create warehouse schema
        if not transformer.create_warehouse_schema():
            return
        
        # Transform data to warehouse
        if not transformer.transform_to_warehouse():
            return
        
        # Verify warehouse data
        transformer.verify_warehouse_data()
        
        # Show sample data
        transformer.show_sample_data()
        
        print("✓ Warehouse transformation completed successfully!")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
