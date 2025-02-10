import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dhananjay@007', # Change this to the root password for your device
    'database': 'CrowdNest'
}

def init_database():
    try:
        # First connect without database to create it if needed
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create donations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                donor_id VARCHAR(36) NOT NULL,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                category VARCHAR(50),
                `condition` VARCHAR(50),
                location VARCHAR(100),
                image_path VARCHAR(255),
                status VARCHAR(20) DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (donor_id) REFERENCES users(unique_id)
            )
        """)
        
        # Create requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                requester_id VARCHAR(36) NOT NULL,
                donation_id VARCHAR(36) NOT NULL,
                message TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users(unique_id),
                FOREIGN KEY (donation_id) REFERENCES donations(unique_id)
            )
        """)
        
        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                sender_id VARCHAR(36) NOT NULL,
                receiver_id VARCHAR(36) NOT NULL,
                donation_id VARCHAR(36),
                content TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(unique_id),
                FOREIGN KEY (receiver_id) REFERENCES users(unique_id),
                FOREIGN KEY (donation_id) REFERENCES donations(unique_id)
            )
        """)
        
        print("Successfully initialized database schema")
        return True
        
    except Error as e:
        print(f"Error initializing database: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    if init_database():
        print("Database initialization completed successfully")
    else:
        print("Database initialization failed") 