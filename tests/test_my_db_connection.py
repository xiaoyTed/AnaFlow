#!/usr/bin/env python3
"""
Quick script to test connection to your PostgreSQL database.

Usage:
    export DATABASE_URL="postgresql://user:pass@10.36.21.200:5432/dbname"
    python test_my_db_connection.py
"""

import os
import sys
import csv

try:
    import psycopg
except ImportError:
    print("❌ psycopg not installed. Run: uv pip install psycopg")
    sys.exit(1)


def test_connection():
    """Test connection to database."""
    # database_url = os.getenv("DATABASE_URL")
    database_url = "postgresql://ana:Svoltana36@10.36.21.200:5432/dqdb?sslmode=disable"
    
    if not database_url:
        print("❌ DATABASE_URL not set!")
        print("\nPlease set it with:")
        print("  export DATABASE_URL='postgresql://user:pass@10.36.21.200:5432/dbname'")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql://postgres:mypass@10.36.21.200:5432/testdb'")
        return False
    
    # Hide password in output
    safe_url = database_url.split('@')[1] if '@' in database_url else database_url
    print(f"🔌 Testing connection to: {safe_url}")
    print()
    
    try:
        # Try to connect
        conn = psycopg.connect(database_url, connect_timeout=10)
        
        # Get some info
        cursor = conn.cursor()
        
        # Check password encryption method
        cursor.execute("SHOW password_encryption")
        password_result = cursor.fetchone()
        password_method = password_result[0] if password_result else "unknown"
        
        cursor.execute("SELECT version()")
        version_result = cursor.fetchone()
        version = version_result[0] if version_result else "unknown"
        
        cursor.execute("SELECT current_database()")
        db_result = cursor.fetchone()
        db_name = db_result[0] if db_result else "unknown"
        
        cursor.execute("SELECT current_user")
        user_result = cursor.fetchone()
        username = user_result[0] if user_result else "unknown"
        
        #list all tables in the database
        print(f"📊 Current database: {db_name}")
        print(f"👤 Current user: {username}")
        cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'dws' AND table_type = 'BASE TABLE'")
        tables_result = cursor.fetchall()
        print(f"🔍 Raw query result: {tables_result}")
        print(f"🔍 Number of rows: {len(tables_result)}")
        tables = [table[1] for table in tables_result]  # table[1] is table_name, table[0] is table_schema
        print(f"📋 Tables in the schema dws: {tables}")

        #list five value in 'car_brand'
        cursor.execute("SELECT MAX(quantity) as max_sales FROM dws.dws_domestic_vehicle_sales_data_by_week WHERE car_brand = '大众';")
        car_brand_result = cursor.fetchall()
        print(f"🔍 Car brand: {car_brand_result}")

        #list all value in 'week_code'
        cursor.execute("SELECT week_code FROM dws.dws_domestic_vehicle_sales_data_by_week;")
        week_code_result = cursor.fetchall()
        week_code_result = week_code_result[0][0]
        print(f"🔍 Week code: {week_code_result}")
        #save the result to a csv file
        # with open('week_code.csv', 'w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(week_code_result)
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg.OperationalError as e:
        print(f"❌ Connection failed!")
        print(f"\nError: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check database server is running")
        print("  2. Verify host is correct: 10.36.21.200:5432")
        print("  3. Check username and password")
        print("  4. Verify firewall allows connections")
        print("  5. Check pg_hba.conf on server")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

