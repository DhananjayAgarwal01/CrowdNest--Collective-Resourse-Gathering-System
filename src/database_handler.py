import mysql.connector
from mysql.connector import Error, IntegrityError
import os
import hashlib
from datetime import datetime
import uuid
from dotenv import load_dotenv

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
        """Connect to MySQL database"""
        load_dotenv()
        
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Explicitly set the password to 12345678
                password = '12345678'
                
                print(f"Attempting to connect with:")
                print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
                print(f"User: {os.getenv('DB_USER', 'root')}")
                print(f"Password: {password}")
                print(f"Database: {os.getenv('DB_NAME', 'CrowdNest')}")
                
                self.connection = mysql.connector.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    user=os.getenv('DB_USER', 'root'),
                    password=password,
                    database=os.getenv('DB_NAME', 'CrowdNest'),
                    auth_plugin='mysql_native_password',
                    allow_local_infile=True
                )
                self.connection.autocommit = False  # Explicit transaction control
                print("Successfully connected to MySQL database")
                return
            except Error as e:
                last_error = e
                retry_count += 1
                print(f"MySQL connection attempt {retry_count} failed: {e}")
                print(f"Error type: {type(e)}")
                print(f"Error details: {e.errno}, {e.sqlstate}, {e.msg}")
                if retry_count < max_retries:
                    # Wait before retrying (exponential backoff)
                    import time
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
            cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = LOWER(%s)", 
                          (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return False, "Username or email already exists"
            
            # Generate unique ID
            unique_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Prepare full name
            full_name = full_name or username
            
            # Insert new user
            query = """
            INSERT INTO users (
                unique_id, username, password_hash, email, full_name, location, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (
                unique_id, 
                username, 
                hashed_password, 
                email, 
                full_name,
                location
            ))
            
            # Commit the transaction
            self.connection.commit()
            
            return True, "User created successfully"

        except IntegrityError as e:
            # Rollback in case of integrity error
            self.connection.rollback()
            print(f"Integrity Error: {e}")
            return False, "Error creating user. Please check your inputs."
        
        except Error as e:
            # Rollback in case of any other database error
            self.connection.rollback()
            print(f"Database Error: {e}")
            return False, f"Database error: {str(e)}"
        
        finally:
            # Close cursor
            if cursor:
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
                SELECT unique_id, username, email, full_name, location, created_at
                FROM users
                WHERE LOWER(username) = LOWER(%s) AND password_hash = %s
            """
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                # Add additional user details if needed
                user['total_donations'] = 0
                user['total_requests'] = 0
                user['total_messages'] = 0
                return (user, "Success")
            else:
                return (None, "Invalid username or password")

        except Error as e:
            print(f"Error verifying user: {e}")
            return None, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def get_donations(self, search_query=None, category=None, condition=None, location=None, donation_id=None):
        """Get donations based on search criteria"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT d.*, u.full_name as donor_name, u.email as donor_email
                FROM donations d
                JOIN users u ON d.donor_id = u.unique_id
                WHERE 1=1
            """
            params = []
            
            if donation_id:
                query += " AND d.unique_id = %s"
                params.append(donation_id)
                
            if search_query:
                query += " AND (d.title LIKE %s OR d.description LIKE %s)"
                search_pattern = f"%{search_query}%"
                params.extend([search_pattern, search_pattern])
                
            if category:
                query += " AND d.category = %s"
                params.append(category)
                
            if condition:
                query += " AND d.condition = %s"
                params.append(condition)
                
            if location:
                query += " AND d.location = %s"
                params.append(location)
                
            query += " ORDER BY d.created_at DESC"
            
            cursor.execute(query, params)
            donations = cursor.fetchall()
            return donations
            
        except Error as e:
            print(f"Error getting donations: {e}")
            return []
        finally:
            cursor.close()

    def create_donation(self, donor_id, title, description, category, condition, state, city, image_data=None):
        """Create a new donation"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Convert image_data to bytes if it's a list
            if isinstance(image_data, list):
                # Assuming the first element is the image data
                image_data = image_data[0] if image_data else None
            
            # Generate a unique ID for the donation
            unique_id = str(uuid.uuid4())
            
            # Insert donation
            query = """
                INSERT INTO donations (
                    unique_id, donor_id, title, description, category,
                    `condition`, location, status,
                    image_path, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """
            
            # Combine state and city into location
            location = f"{city}, {state}"
            
            values = (
                unique_id, donor_id, title, description, category,
                condition, location, 'available',
                image_data
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            
            return True, "Donation created successfully"
            
        except mysql.connector.Error as err:
            # Rollback the transaction in case of error
            self.connection.rollback()
            print(f"Error creating donation: {err}")
            return False, f"Failed to create donation: {str(err)}"
            
        finally:
            if cursor:
                cursor.close()

    def update_donation_status(self, donation_id, new_status):
        """Update donation status (Available/Received/Donated)"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(
                """UPDATE donations 
                   SET status = %s
                   WHERE id = %s
                """,
                (new_status, donation_id)
            )
            
            self.connection.commit()
            return True, f"Donation marked as {new_status}"
            
        except Error as e:
            print(f"Error updating donation status: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()

    def save_profile_changes(self, user_id, email, full_name, location):
        """Save user profile changes"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            # Check if email already exists for another user
            cursor.execute(
                """SELECT COUNT(*) FROM users 
                   WHERE LOWER(email) = LOWER(%s) AND unique_id != %s
                """, 
                (email, user_id)
            )
            email_count = cursor.fetchone()[0]
            
            if email_count > 0:
                return False, "Email already exists"
            
            # Update user profile
            cursor.execute(
                """UPDATE users 
                   SET email = %s, full_name = %s, location = %s
                   WHERE unique_id = %s
                """,
                (email, full_name, location, user_id)
            )
            self.connection.commit()
            return True, "Profile updated successfully"
            
        except Error as e:
            print(f"Error updating profile: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()