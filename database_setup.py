import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect without specifying a database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '12345678')
        )
        
        cursor = connection.cursor()
        
        # Create database
        db_name = os.getenv('DB_NAME', 'CrowdNest')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database {db_name} created or already exists.")
        
        # Close connection
        cursor.close()
        connection.close()
    except mysql.connector.Error as e:
        print(f"Error creating database: {e}")

def create_tables():
    """Create all necessary tables"""
    try:
        # Connect to the specific database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '12345678'),
            database=os.getenv('DB_NAME', 'CrowdNest')
        )
        
        cursor = connection.cursor()
        
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Users table with enhanced schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            unique_id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            location VARCHAR(100),
            profile_image VARCHAR(255) DEFAULT NULL,
            total_donations INT DEFAULT 0,
            total_requests INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
            email_verified BOOLEAN DEFAULT FALSE,
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Users table created or already exists.")
        
        # Donations table with enhanced schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unique_id VARCHAR(36) UNIQUE NOT NULL,
            donor_id VARCHAR(36) NOT NULL,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            `condition` VARCHAR(50) NOT NULL,
            state VARCHAR(50) NOT NULL,
            city VARCHAR(50) NOT NULL,
            image_path LONGTEXT,
            status ENUM('available', 'reserved', 'donated', 'pending', 'completed') DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (donor_id) REFERENCES users(unique_id) ON DELETE CASCADE,
            INDEX idx_status (status),
            INDEX idx_category (category),
            INDEX idx_location (state, city),
            FULLTEXT INDEX idx_search (title, description)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Donations table created or already exists.")
        
        # Requests table with enhanced schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            unique_id VARCHAR(36) PRIMARY KEY,
            requester_id VARCHAR(36) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            state VARCHAR(50) NOT NULL,
            city VARCHAR(50) NOT NULL,
            status ENUM('open', 'fulfilled', 'closed') DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (requester_id) REFERENCES users(unique_id) ON DELETE CASCADE,
            INDEX idx_status (status),
            INDEX idx_category (category),
            INDEX idx_location (state, city),
            FULLTEXT INDEX idx_search (title, description)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("Requests table created or already exists.")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Commit changes
        connection.commit()
        
        # Close connection
        cursor.close()
        connection.close()
    except mysql.connector.Error as e:
        print(f"Error creating tables: {e}")

def main():
    """Main function to set up the database"""
    create_database()
    create_tables()
    print("Database setup completed successfully.")

if __name__ == "__main__":
    main()
