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
    
    def create_user(self, username, password, email, location):
        """Create a new user in the database"""
        self.ensure_connection()
        cursor = None
        
        try:
            # Check if username already exists
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(%s)", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return False, "Username already exists"
            
            # Generate unique ID
            unique_id = str(uuid.uuid4())
            
            # Hash the password
            password_hash = self.hash_password(password)
            
            # Insert new user
            query = """
            INSERT INTO users (
                unique_id, username, password_hash, email, full_name, location, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (
                unique_id, 
                username, 
                password_hash, 
                email, 
                '', 
                location
            ))
            
            # Commit the transaction
            self.connection.commit()
            
            return True, "User created successfully"
        
        except Error as e:
            print(f"Error creating user: {e}")
            if self.connection:
                self.connection.rollback()
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
                SELECT unique_id, username, email, full_name, location, created_at, password_hash
                FROM users
                WHERE LOWER(username) = LOWER(%s) AND password_hash = %s
            """
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                # Remove password_hash from returned user data
                user.pop('password_hash', None)
                
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

    def get_donations(self, **kwargs):
        """Retrieve donations with flexible filtering"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Base query to get donations with donor information
            query = """
                SELECT d.*, u.full_name as donor_name, u.email as donor_email
                FROM donations d
                JOIN users u ON d.donor_id = u.unique_id
                WHERE 1=1
            """
            
            # Prepare conditions and values for filtering
            conditions = []
            values = []
            
            # Mapping of allowed filter keys
            filter_mapping = {
                'category': 'd.category',
                'condition': 'd.condition',
                'location': 'd.location',
                'status': 'd.status',
                'unique_id': 'd.unique_id',
                'donor_id': 'd.donor_id'
            }
            
            # Handle search term separately
            if 'search_term' in kwargs and kwargs['search_term']:
                search_term = f"%{kwargs['search_term']}%"
                conditions.append("(d.title LIKE %s OR d.description LIKE %s)")
                values.extend([search_term, search_term])
            
            # Build dynamic filter conditions
            for key, value in kwargs.items():
                if key in filter_mapping and value is not None and key != 'search_term':
                    conditions.append(f"{filter_mapping[key]} = %s")
                    values.append(value)
            
            # Add conditions to query if any exist
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # Order by most recent first
            query += " ORDER BY d.created_at DESC"
            
            # Execute query
            cursor.execute(query, values)
            donations = cursor.fetchall()
            
            return donations
        
        except mysql.connector.Error as err:
            print(f"Error retrieving donations: {err}")
            return []
        
        finally:
            if cursor:
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
            
            return True, unique_id
            
        except mysql.connector.Error as err:
            # Rollback the transaction in case of error
            self.connection.rollback()
            print(f"Error creating donation: {err}")
            return False, f"Failed to create donation: {str(err)}"
            
        finally:
            if cursor:
                cursor.close()

    def mark_donation_as_donated(self, donation_id, current_user_id):
        """Mark a donation as donated, but only if the current user is the donor"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # First, verify that the current user is the donor
            verify_query = """
                SELECT donor_id 
                FROM donations 
                WHERE unique_id = %s
            """
            cursor.execute(verify_query, (donation_id,))
            donation = cursor.fetchone()
            
            if not donation or donation['donor_id'] != current_user_id:
                return False, "You are not authorized to mark this donation as donated"
            
            # Update donation status
            update_query = """
                UPDATE donations 
                SET status = 'completed', 
                    updated_at = NOW() 
                WHERE unique_id = %s
            """
            cursor.execute(update_query, (donation_id,))
            self.connection.commit()
            
            return True, "Donation marked as donated successfully"
        
        except mysql.connector.Error as err:
            # Rollback the transaction in case of error
            self.connection.rollback()
            print(f"Error marking donation as donated: {err}")
            return False, f"Failed to mark donation as donated: {str(err)}"
        
        finally:
            if cursor:
                cursor.close()

    def get_user_donation_history(self, user_id):
        """Retrieve donation history for a specific user"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT d.*, u.full_name as donor_name
                FROM donations d
                JOIN users u ON d.donor_id = u.unique_id
                WHERE d.donor_id = %s AND d.status = 'completed'
                ORDER BY d.updated_at DESC
            """
            
            cursor.execute(query, (user_id,))
            donation_history = cursor.fetchall()
            
            return donation_history
        
        except mysql.connector.Error as err:
            print(f"Error retrieving donation history: {err}")
            return []
        
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
    
    def create_donation_request(self, donation_id, requester_id, requester_name, requester_email):
        """Create a new donation request"""
        self.ensure_connection()
        cursor = None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Check if request already exists
            cursor.execute(
                """SELECT * FROM donation_requests 
                   WHERE donation_id = %s AND requester_id = %s
                """,
                (donation_id, requester_id)
            )
            existing_request = cursor.fetchone()
            
            if existing_request:
                return False, "You have already requested this item"
            
            # Generate unique ID for request
            request_id = str(uuid.uuid4())
            
            # Insert request
            cursor.execute(
                """INSERT INTO donation_requests (
                    unique_id, donation_id, requester_id, requester_name,
                    requester_email, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, 'pending', NOW())
                """,
                (request_id, donation_id, requester_id, requester_name, requester_email)
            )
            
            self.connection.commit()
            return True, "Request created successfully"
            
        except Error as e:
            print(f"Error creating request: {e}")
            if self.connection:
                self.connection.rollback()
            return False, f"Database error: {str(e)}"
        
        finally:
            if cursor:
                cursor.close()
    
    def get_donation_requests(self, user_id):
        """Get all donation requests for a user's donations"""
        self.ensure_connection()
        cursor = None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT r.*, d.title as donation_title
                FROM donation_requests r
                JOIN donations d ON r.donation_id = d.unique_id
                WHERE d.donor_id = %s
                ORDER BY r.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            requests = cursor.fetchall()
            
            return requests
            
        except Error as e:
            print(f"Error fetching requests: {e}")
            return []
        
        finally:
            if cursor:
                cursor.close()
    
    def get_request_details(self, request_id):
        """Get details of a specific request"""
        self.ensure_connection()
        cursor = None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT r.*, d.title as donation_title
                FROM donation_requests r
                JOIN donations d ON r.donation_id = d.unique_id
                WHERE r.unique_id = %s
            """
            
            cursor.execute(query, (request_id,))
            request = cursor.fetchone()
            
            return request
            
        except Error as e:
            print(f"Error fetching request details: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()
    
    def update_request_status(self, request_id, new_status):
        """Update the status of a donation request"""
        self.ensure_connection()
        cursor = None
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute(
                """UPDATE donation_requests
                   SET status = %s, updated_at = NOW()
                   WHERE unique_id = %s
                """,
                (new_status, request_id)
            )
            
            self.connection.commit()
            return True, f"Request {new_status} successfully"
            
        except Error as e:
            print(f"Error updating request status: {e}")
            if self.connection:
                self.connection.rollback()
            return False, f"Database error: {str(e)}"
        
        finally:
            if cursor:
                cursor.close()
            print(f"Error updating profile: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}"

    def update_user_profile(self, user_id, profile_data):
        """Update user profile information"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Prepare the update query dynamically based on provided data
            update_fields = []
            values = []
            
            # Validate and add fields to update
            if 'full_name' in profile_data:
                update_fields.append("full_name = %s")
                values.append(profile_data['full_name'])
            
            if 'email' in profile_data:
                # Validate email format
                import re
                if not re.match(r"[^@]+@[^@]+\.[^@]+", profile_data['email']):
                    return False, "Invalid email format"
                
                update_fields.append("email = %s")
                values.append(profile_data['email'])
            
            if 'location' in profile_data:
                update_fields.append("location = %s")
                values.append(profile_data['location'])
            
            # If no fields to update, return
            if not update_fields:
                return False, "No fields to update"
            
            # Add user_id to values for WHERE clause
            values.append(user_id)
            
            # Construct full query
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE unique_id = %s
            """
            
            # Execute update
            cursor.execute(query, values)
            self.connection.commit()
            
            return True, "Profile updated successfully"
        
        except mysql.connector.Error as err:
            # Rollback the transaction in case of error
            self.connection.rollback()
            print(f"Error updating user profile: {err}")
            
            # Check for duplicate email
            if err.errno == 1062:  # Duplicate entry
                return False, "Email already in use"
            
            return False, f"Failed to update profile: {str(err)}"
        
        finally:
            if cursor:
                cursor.close()

    def change_user_password(self, user_id, current_password, new_password):
        """Change user's password with verification"""
        try:
            # Validate input
            if not user_id or not current_password or not new_password:
                print("Invalid input for password change")
                return False
            
            # Verify current password first
            cursor = self.connection.cursor(dictionary=True)
            
            # Hash the current password for verification
            current_password_hash = self.hash_password(current_password)
            
            # Check if current password is correct
            query = "SELECT * FROM users WHERE unique_id = %s AND password_hash = %s"
            cursor.execute(query, (user_id, current_password_hash))
            user = cursor.fetchone()
            
            if not user:
                return False, "Current password is incorrect"
            
            # Hash the new password
            new_password_hash = self.hash_password(new_password)
            
            # Update password
            update_query = "UPDATE users SET password_hash = %s WHERE unique_id = %s"
            cursor.execute(update_query, (new_password_hash, user_id))
            
            # Commit the transaction
            self.connection.commit()
            
            return True, "Password updated successfully"
        
        except Error as e:
            print(f"Error changing password: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        
        finally:
            if cursor:
                cursor.close()

    def get_filtered_donations(self, filter_dict=None):
        """
        Retrieve donations with optional filtering
        
        :param filter_dict: Dictionary of filter conditions
        :return: List of filtered donations
        """
        try:
            # Ensure connection is active
            self.ensure_connection()
            
            # Create cursor
            cursor = self.connection.cursor(dictionary=True)
            
            # Base query
            query = """
                SELECT d.*, u.full_name as donor_name, u.email as donor_email
                FROM donations d
                JOIN users u ON d.donor_id = u.unique_id
                WHERE 1=1
            """
            
            # Parameters list for query
            params = []
            
            # Build dynamic filter conditions
            if filter_dict:
                for key, value in filter_dict.items():
                    # Handle special cases
                    if key == 'category':
                        query += " AND d.category = %s"
                        params.append(value)
                    elif key == 'location':
                        query += " AND d.location LIKE %s"
                        params.append(f"%{value}%")
                    elif key == 'status':
                        query += " AND d.status = %s"
                        params.append(value)
                    elif key == 'donor_id':
                        query += " AND d.donor_id = %s"
                        params.append(value)
            
            # Add ordering
            query += " ORDER BY d.created_at DESC"
            
            # Execute query
            cursor.execute(query, params)
            
            # Fetch all donations
            donations = cursor.fetchall()
            
            return donations
        
        except mysql.connector.Error as err:
            print(f"Error retrieving filtered donations: {err}")
            return []
        
        finally:
            if cursor:
                cursor.close()