import mysql.connector
from mysql.connector import Error, IntegrityError
import os
import hashlib
from datetime import datetime
import uuid

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dhananjay@007',
    'database': 'donateshare'
}

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            raise
            
    def ensure_connection(self):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
        except Error as e:
            print(f"Error ensuring database connection: {e}")
            raise
            
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email, location):
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return False
                
            hashed_password = self.hash_password(password)
            unique_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO users (unique_id, username, password_hash, email, location)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (unique_id, username, hashed_password, email, location))
            self.connection.commit()
            return True
            
        except IntegrityError:
            print("Username or email already exists")
            return False
        except Error as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()
            
    def verify_user(self, username, password):
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            hashed_password = self.hash_password(password)
            query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Error verifying user: {e}")
            return None
        finally:
            cursor.close()
            
    def create_donation(self, donor_id, title, description, category, condition, location, image_path=None):
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            print(f"Creating donation with params: donor_id={donor_id}, title={title}, category={category}, condition={condition}, location={location}")
            unique_id = str(uuid.uuid4())
            query = """
                INSERT INTO donations 
                (unique_id, donor_id, title, description, category, `condition`, location, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (unique_id, donor_id, title, description, category, condition, location, image_path)
            cursor.execute(query, values)
            self.connection.commit()
            print("Successfully created donation in database")
            return True
        except Error as e:
            print(f"Database error creating donation: {str(e)}")
            print(f"Error Code: {e.errno}")
            print(f"SQLSTATE: {e.sqlstate}")
            print(f"Full Error: {e}")
            return False
        finally:
            cursor.close()
            
    def get_donations(self, search_term=None):
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            if search_term:
                query = """
                    SELECT d.*, u.username as donor_name 
                    FROM donations d
                    JOIN users u ON d.donor_id = u.unique_id
                    WHERE d.title LIKE %s OR d.description LIKE %s
                    ORDER BY d.created_at DESC
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern))
            else:
                query = """
                    SELECT d.*, u.username as donor_name 
                    FROM donations d
                    JOIN users u ON d.donor_id = u.unique_id
                    ORDER BY d.created_at DESC
                """
                cursor.execute(query)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching donations: {e}")
            return []
        finally:
            cursor.close()
            
    def create_request(self, requester_id, donation_id, message):
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            unique_id = str(uuid.uuid4())
            query = """
                INSERT INTO requests (unique_id, requester_id, donation_id, message)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (unique_id, requester_id, donation_id, message))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error creating request: {e}")
            return False
        finally:
            cursor.close()
            
    def send_message(self, sender_id, receiver_id, content, donation_id=None):
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            unique_id = str(uuid.uuid4())
            query = """
                INSERT INTO messages (unique_id, sender_id, receiver_id, donation_id, content)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (unique_id, sender_id, receiver_id, donation_id, content))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error sending message: {e}")
            return False
        finally:
            cursor.close()
            
    def get_messages(self, user_id):
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT m.*, 
                       s.username as sender_name,
                       r.username as receiver_name,
                       d.title as donation_title
                FROM messages m
                JOIN users s ON m.sender_id = s.unique_id
                JOIN users r ON m.receiver_id = r.unique_id
                LEFT JOIN donations d ON m.donation_id = d.unique_id
                WHERE m.sender_id = %s OR m.receiver_id = %s
                ORDER BY m.created_at DESC
            """
            cursor.execute(query, (user_id, user_id))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching messages: {e}")
            return []
        finally:
            cursor.close()
            
    def update_profile(self, user_id, email=None, location=None):
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            updates = []
            params = []
            
            if email:
                updates.append("email = %s")
                params.append(email)
            if location:
                updates.append("location = %s")
                params.append(location)
                
            if not updates:
                return True
                
            query = f"UPDATE users SET {', '.join(updates)} WHERE unique_id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error updating profile: {e}")
            return False
        finally:
            cursor.close()
            
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed") 