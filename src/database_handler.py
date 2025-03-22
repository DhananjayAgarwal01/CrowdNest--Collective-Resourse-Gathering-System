import mysql.connector
from mysql.connector import Error, IntegrityError
import os
import hashlib
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'database': os.getenv('DB_NAME', 'CrowdNest'),
    'auth_plugin': 'mysql_native_password'
}

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        """Establish database connection with retry mechanism"""
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                self.connection = mysql.connector.connect(**DB_CONFIG)
                self.connection.autocommit = False  # Explicit transaction control
                print("Successfully connected to MySQL database")
                return
            except Error as e:
                last_error = e
                retry_count += 1
                print(f"MySQL connection attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    # Wait before retrying (exponential backoff)
                    time.sleep(2 ** retry_count)
        
        raise Exception(f"Failed to connect to MySQL database after {max_retries} attempts. Last error: {last_error}")
            
    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
        except Error as e:
            print(f"Error ensuring database connection: {e}")
            raise
            
    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = os.getenv('PASSWORD_SALT', 'default_salt')
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def create_user(self, username, password, email, location, full_name=None):
        """Create a new user with validation"""
        self.ensure_connection()
        cursor = self.connection.cursor()

        try:
            # Input validation
            if not all([username, password, email, location]):
                return False, "All fields are required"
                
            if len(password) < 6:
                return False, "Password must be at least 6 characters"
                
            # Sanitize inputs
            username = username.strip()
            email = email.strip()
            location = location.strip()
            
            # Check existing user
            try:
                cursor.execute(
                    """SELECT COUNT(*) FROM users 
                       WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = LOWER(%s)
                    """, 
                    (username, email)
                )
                user_count = cursor.fetchone()[0]
                
                if user_count > 0:
                    return False, "Username or email already exists"
            except mysql.connector.Error as err:
                print(f"MySQL Error checking existing user: {err}")
                if self.connection and self.connection.is_connected():
                    self.connection.rollback()
                return False, "Database error while checking user existence"
            except Exception as e:
                print(f"Unexpected error checking existing user: {e}")
                if self.connection and self.connection.is_connected():
                    self.connection.rollback()
                return False, "Database error while checking user existence"

            try:
                # Create user
                hashed_password = self.hash_password(password)
                unique_id = str(uuid.uuid4())

                try:
                    query = """
                        INSERT INTO users (unique_id, username, password_hash, email, location, full_name, created_at) 
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """
                    cursor.execute(query, (unique_id, username, hashed_password, email, location, full_name))
                    self.connection.commit()
                    return True, "User created successfully"
                except mysql.connector.Error as err:
                    print(f"MySQL Error during user creation: {err}")
                    self.connection.rollback()
                    return False, "Database error during user creation"
            except (Error, sqlite3.Error) as e:
                print(f"Error creating user: {e}")
                return False, "Error creating user account"

        except IntegrityError as e:
            self.connection.rollback()
            return False, "Database integrity error"
        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()

    def verify_user(self, username, password):
        """Verify user credentials and return user data"""
        self.ensure_connection()
        cursor = None
        
        try:
            if not username or not password:
                return None, "Username and password are required"

            username = username.strip()
            hashed_password = self.hash_password(password)
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT u.unique_id, u.username, u.email, u.location, u.created_at, u.profile_image, u.full_name,
                       COUNT(DISTINCT d.id) as total_donations,
                       COUNT(DISTINCT r.id) as total_requests,
                       COUNT(DISTINCT m.id) as total_messages
                FROM users u
                LEFT JOIN donations d ON u.unique_id = d.donor_id
                LEFT JOIN requests r ON u.unique_id = r.requester_id
                LEFT JOIN messages m ON u.unique_id = m.sender_id
                WHERE LOWER(u.username) = LOWER(%s) AND u.password_hash = %s
                GROUP BY u.unique_id, u.username, u.email, u.location, u.created_at, u.profile_image
            """
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            return (user, "Success") if user else (None, "Invalid username or password")

        except Error as e:
            print(f"Error verifying user: {e}")
            return None, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()