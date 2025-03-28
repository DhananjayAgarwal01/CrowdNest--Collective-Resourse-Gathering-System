import mysql.connector
import hashlib
import os
import uuid
from dotenv import load_dotenv

class DatabaseHandler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Database connection parameters
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '12345678'),
            'database': os.getenv('DB_NAME', 'CrowdNest')
        }
        
        # Establish connection
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.connection_params)
            self.cursor = self.connection.cursor(dictionary=True)
            print("Successfully connected to MySQL database")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        try:
            # Hash the provided password
            hashed_password = self.hash_password(password)
            
            # Query to check user credentials
            query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
            self.cursor.execute(query, (username, hashed_password))
            
            user = self.cursor.fetchone()
            
            if user:
                # Remove sensitive information
                user.pop('password_hash', None)
                return user
            return None
        
        except mysql.connector.Error as e:
            print(f"Authentication error: {e}")
            return None
    
    def register_user(self, username, email, password, location=None):
        """Register a new user"""
        try:
            # Generate unique ID
            unique_id = str(uuid.uuid4())
            
            # Hash the password
            hashed_password = self.hash_password(password)
            
            # Prepare the query
            query = """
            INSERT INTO users 
            (unique_id, username, email, password_hash, location, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            # Print out the values for debugging
            print(f"Registering user - Unique ID: {unique_id}")
            print(f"Registering user - Username: {username}")
            print(f"Registering user - Email: {email}")
            print(f"Registering user - Location: {location}")
            
            # Execute the query
            self.cursor.execute(query, (unique_id, username, email, hashed_password, location))
            self.connection.commit()
            
            return unique_id
        
        except mysql.connector.Error as e:
            print(f"Registration error: {e}")
            self.connection.rollback()
            return None
    
    def change_user_password(self, user_id, old_password, new_password):
        """Change user password"""
        try:
            # Hash passwords
            old_hashed_password = self.hash_password(old_password)
            new_hashed_password = self.hash_password(new_password)
            
            # Verify old password first
            verify_query = "SELECT * FROM users WHERE unique_id = %s AND password_hash = %s"
            self.cursor.execute(verify_query, (user_id, old_hashed_password))
            
            if not self.cursor.fetchone():
                return False
            
            # Update password
            update_query = "UPDATE users SET password_hash = %s WHERE unique_id = %s"
            self.cursor.execute(update_query, (new_hashed_password, user_id))
            self.connection.commit()
            
            return True
        
        except mysql.connector.Error as e:
            print(f"Password change error: {e}")
            self.connection.rollback()
            return False
    
    def get_user_details(self, user_id):
        """Get complete user details including profile information"""
        try:
            query = """
            SELECT u.*, 
                COUNT(DISTINCT d.unique_id) as total_donations,
                COUNT(DISTINCT r.unique_id) as total_requests
            FROM users u
            LEFT JOIN donations d ON u.unique_id = d.donor_id
            LEFT JOIN requests r ON u.unique_id = r.requester_id
            WHERE u.unique_id = %s
            GROUP BY u.unique_id
            """
            self.cursor.execute(query, (user_id,))
            user_details = self.cursor.fetchone()
            
            if user_details:
                # Remove sensitive information
                user_details.pop('password_hash', None)
                return user_details
            return None
            
        except mysql.connector.Error as e:
            print(f"Error fetching user details: {e}")
            return None
    
    def add_donation(self, donor_id, title, description, category, condition, state, city, image_path=None):
        """Add a new donation to the database"""
        try:
            # Generate unique ID for the donation
            unique_id = str(uuid.uuid4())
            
            # Prepare the query
            query = """
            INSERT INTO donations 
            (unique_id, donor_id, title, description, category, `condition`, state, city, image_path, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            # Execute the query
            self.cursor.execute(query, (
                unique_id,
                donor_id,
                title,
                description,
                category,
                condition,
                state,
                city,
                image_path
            ))
            self.connection.commit()
            
            return unique_id
            
        except mysql.connector.Error as e:
            print(f"Error adding donation: {e}")
            self.connection.rollback()
            return None
    
    def search_donations(self, search_query=None, category=None, location=None):
        """Search donations based on criteria. Returns all donations if no criteria specified."""
        try:
            base_query = """
            SELECT d.*, u.username as donor_name, u.email as donor_email
            FROM donations d
            JOIN users u ON d.donor_id = u.unique_id
            WHERE 1=1
            """
            params = []

            if search_query:
                base_query += " AND (d.title LIKE %s OR d.description LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            if category:
                base_query += " AND d.category = %s"
                params.append(category)

            if location:
                base_query += " AND (d.state = %s OR d.city = %s)"
                params.extend([location, location])

            base_query += " ORDER BY d.created_at DESC"
            
            self.cursor.execute(base_query, params)
            return self.cursor.fetchall()
            
        except mysql.connector.Error as e:
            print(f"Error searching donations: {e}")
            return []
    
    def get_donation_details(self, donation_id):
        """Get detailed information about a specific donation"""
        try:
            query = """
            SELECT d.*, u.username as donor_name, u.email as donor_email
            FROM donations d
            JOIN users u ON d.donor_id = u.unique_id
            WHERE d.unique_id = %s
            """
            self.cursor.execute(query, (donation_id,))
            return self.cursor.fetchone()
            
        except mysql.connector.Error as e:
            print(f"Error fetching donation details: {e}")
            return None
    
    def delete_donation(self, donation_id, user_id):
        """Delete a donation if the user is the owner"""
        try:
            # Verify ownership first
            verify_query = "SELECT donor_id FROM donations WHERE unique_id = %s"
            self.cursor.execute(verify_query, (donation_id,))
            donation = self.cursor.fetchone()
            
            if not donation or donation['donor_id'] != user_id:
                return False
            
            # Delete the donation
            delete_query = "DELETE FROM donations WHERE unique_id = %s"
            self.cursor.execute(delete_query, (donation_id,))
            self.connection.commit()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Error deleting donation: {e}")
            self.connection.rollback()
            return False
    
    def add_request(self, requester_id, title, description, category, state, city):
        """Add a new request to the database"""
        try:
            # Generate unique ID for the request
            unique_id = str(uuid.uuid4())
            
            # Prepare the query
            query = """
            INSERT INTO requests 
            (unique_id, requester_id, title, description, category, state, city, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            # Execute the query
            self.cursor.execute(query, (
                unique_id,
                requester_id,
                title,
                description,
                category,
                state,
                city
            ))
            self.connection.commit()
            
            return unique_id
            
        except mysql.connector.Error as e:
            print(f"Error adding request: {e}")
            self.connection.rollback()
            return None
    
    def search_requests(self, search_query=None, category=None, location=None):
        """Search requests based on criteria"""
        try:
            base_query = """
            SELECT r.*, u.username as requester_name, u.email as requester_email
            FROM requests r
            JOIN users u ON r.requester_id = u.unique_id
            WHERE 1=1
            """
            params = []

            if search_query:
                base_query += " AND (r.title LIKE %s OR r.description LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            if category:
                base_query += " AND r.category = %s"
                params.append(category)

            if location:
                base_query += " AND (r.state = %s OR r.city = %s)"
                params.extend([location, location])

            base_query += " ORDER BY r.created_at DESC"
            
            self.cursor.execute(base_query, params)
            return self.cursor.fetchall()
            
        except mysql.connector.Error as e:
            print(f"Error searching requests: {e}")
            return []
    
    def get_request_details(self, request_id):
        """Get detailed information about a specific request"""
        try:
            query = """
            SELECT r.*, u.username as requester_name, u.email as requester_email
            FROM requests r
            JOIN users u ON r.requester_id = u.unique_id
            WHERE r.unique_id = %s
            """
            self.cursor.execute(query, (request_id,))
            return self.cursor.fetchone()
            
        except mysql.connector.Error as e:
            print(f"Error fetching request details: {e}")
            return None
    
    def delete_request(self, request_id, user_id):
        """Delete a request if the user is the owner"""
        try:
            # Verify ownership first
            verify_query = "SELECT requester_id FROM requests WHERE unique_id = %s"
            self.cursor.execute(verify_query, (request_id,))
            request = self.cursor.fetchone()
            
            if not request or request['requester_id'] != user_id:
                return False
            
            # Delete the request
            delete_query = "DELETE FROM requests WHERE unique_id = %s"
            self.cursor.execute(delete_query, (request_id,))
            self.connection.commit()
            
            return True
            
        except mysql.connector.Error as e:
            print(f"Error deleting request: {e}")
            self.connection.rollback()
            return False
    
    def close(self):
        """Close database connection and cursor"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("Database connection closed successfully")
        except mysql.connector.Error as e:
            print(f"Error closing database connection: {e}")
