import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_database():
    """Initialize the database with required tables"""
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '12345678')
        )
        
        # Create cursor
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS CrowdNest")
        cursor.execute("USE CrowdNest")
        
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS donations")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Create users table with correct column names
        cursor.execute("""
        CREATE TABLE users (
            unique_id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            location VARCHAR(100),
            profile_image VARCHAR(255) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create donations table
        cursor.execute("""
        CREATE TABLE donations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unique_id VARCHAR(36) UNIQUE NOT NULL,
            donor_id VARCHAR(36) NOT NULL,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            `condition` VARCHAR(50) NOT NULL,
            location VARCHAR(100) NOT NULL,
            image_path LONGTEXT,
            status ENUM('available', 'pending', 'completed', 'cancelled') DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES users(unique_id) ON DELETE CASCADE,
            INDEX idx_status (status),
            INDEX idx_category (category),
            INDEX idx_location (location),
            FULLTEXT INDEX idx_search (title, description)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Commit changes
        connection.commit()
        print("Database initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
    finally:
        # Close cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    initialize_database()