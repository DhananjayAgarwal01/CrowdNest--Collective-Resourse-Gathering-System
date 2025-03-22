import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mysql_connection():
    try:
        # Print connection details for debugging
        print("Attempting to connect with:")
        print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
        print(f"User: {os.getenv('DB_USER', 'root')}")
        print(f"Database: {os.getenv('DB_NAME', 'CrowdNest')}")
        
        # Attempt connection
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'CrowdNest'),
            auth_plugin='mysql_native_password',
            allow_local_infile=True
        )
        
        # If connection is successful
        print("Successfully connected to MySQL database!")
        
        # Create a cursor and execute a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()
        print(f"MySQL Database Version: {db_version[0]}")
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"MySQL Connection Error: {err}")
        print(f"Error Number: {err.errno}")
        print(f"SQL State: {err.sqlstate}")
        print(f"Error Message: {err.msg}")

if __name__ == "__main__":
    test_mysql_connection()
