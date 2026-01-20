"""
Database connection utility module.
Handles PostgreSQL database connections and operations.
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database connection parameters from environment variables."""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'sales_dw')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'postgres')
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            print(f"✓ Connected to database: {self.database}")
            return True
        except psycopg2.Error as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def create_database(self, db_name):
        """Create a new database if it doesn't exist."""
        try:
            # Connect to default 'postgres' database to create new database
            temp_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            temp_cursor = temp_conn.cursor()
            
            # Check if database exists
            temp_cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
            )
            exists = temp_cursor.fetchone()
            
            if not exists:
                temp_cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)
                ))
                print(f"✓ Database '{db_name}' created successfully")
            else:
                print(f"✓ Database '{db_name}' already exists")
            
            temp_cursor.close()
            temp_conn.close()
            return True
        except psycopg2.Error as e:
            print(f"✗ Error creating database: {e}")
            return False
    
    def execute_script(self, script_path):
        """Execute a SQL script file."""
        try:
            with open(script_path, 'r') as file:
                sql_script = file.read()
            
            self.cursor.execute(sql_script)
            self.connection.commit()
            print(f"✓ Executed script: {script_path}")
            return True
        except (psycopg2.Error, FileNotFoundError) as e:
            print(f"✗ Error executing script {script_path}: {e}")
            self.connection.rollback()
            return False
    
    def execute_query(self, query, params=None):
        """Execute a SQL query with optional parameters."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except psycopg2.Error as e:
            print(f"✗ Error executing query: {e}")
            self.connection.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        """Fetch all rows from a query."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"✗ Error fetching data: {e}")
            return None
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")


def get_connection():
    """Factory function to get a database connection."""
    db = DatabaseConnection()
    if db.connect():
        return db
    return None
