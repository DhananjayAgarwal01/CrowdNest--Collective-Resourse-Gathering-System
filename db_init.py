import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'CrowdNest')
}

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect without database selected
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Database '{DB_CONFIG['database']}' created or already exists")
        return True
        
    except Error as e:
        print(f"Error creating database: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def init_tables():
    """Initialize database tables"""
    try:
        # Connect to the database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Drop existing tables in reverse order to handle foreign key constraints
        cursor.execute("DROP TABLE IF EXISTS user_ratings")
        cursor.execute("DROP TABLE IF EXISTS notifications")
        cursor.execute("DROP TABLE IF EXISTS messages")
        cursor.execute("DROP TABLE IF EXISTS requests")
        cursor.execute("DROP TABLE IF EXISTS donation_images")
        cursor.execute("DROP TABLE IF EXISTS donations")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                location VARCHAR(100) NOT NULL,
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
            CREATE TABLE IF NOT EXISTS donations (
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
        
        # Create donation_images table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS donation_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                donation_id VARCHAR(36) NOT NULL,
                image_data LONGTEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (donation_id) REFERENCES donations(unique_id) ON DELETE CASCADE,
                INDEX idx_donation (donation_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                requester_id VARCHAR(36) NOT NULL,
                donation_id VARCHAR(36) NOT NULL,
                message TEXT NOT NULL,
                status ENUM('pending', 'accepted', 'rejected', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users(unique_id) ON DELETE CASCADE,
                FOREIGN KEY (donation_id) REFERENCES donations(unique_id) ON DELETE CASCADE,
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
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
                FOREIGN KEY (sender_id) REFERENCES users(unique_id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(unique_id) ON DELETE CASCADE,
                FOREIGN KEY (donation_id) REFERENCES donations(unique_id) ON DELETE SET NULL,
                INDEX idx_conversation (sender_id, receiver_id),
                INDEX idx_is_read (is_read)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                type ENUM('donation_request', 'request_accepted', 'request_rejected', 'new_message', 'system') NOT NULL,
                content TEXT NOT NULL,
                reference_id VARCHAR(36),
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(unique_id) ON DELETE CASCADE,
                INDEX idx_user_read (user_id, is_read)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create user_ratings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id VARCHAR(36) UNIQUE NOT NULL,
                rater_id VARCHAR(36) NOT NULL,
                rated_id VARCHAR(36) NOT NULL,
                donation_id VARCHAR(36) NOT NULL,
                rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rater_id) REFERENCES users(unique_id) ON DELETE CASCADE,
                FOREIGN KEY (rated_id) REFERENCES users(unique_id) ON DELETE CASCADE,
                FOREIGN KEY (donation_id) REFERENCES donations(unique_id) ON DELETE CASCADE,
                UNIQUE KEY unique_rating (rater_id, rated_id, donation_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        connection.commit()
        print("Successfully initialized database tables")
        return True
        
    except Error as e:
        print(f"Error initializing tables: {e}")
        return False
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """Main initialization function"""
    print("Starting database initialization...")
    
    if not create_database():
        print("Failed to create database")
        return False
        
    if not init_tables():
        print("Failed to initialize tables")
        return False
        
    print("Database initialization completed successfully")
    return True

if __name__ == "__main__":
    main()