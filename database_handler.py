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
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'CrowdNest')
}

class DatabaseHandler:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        """Establish database connection with retry mechanism"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.connection.autocommit = False
            print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Connection failed: {e}")
            raise
            
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
        """Create a new user with validation"""
        self.ensure_connection()
        cursor = self.connection.cursor()

        try:
            # Input validation
            if not all([username, password, email, location]):
                return False, "All fields are required"
                
            if len(password) < 6:
                return False, "Password must be at least 6 characters"
                
            # Check existing user
            cursor.execute(
                "SELECT id FROM users WHERE LOWER(username) = LOWER(%s) OR LOWER(email) = LOWER(%s)", 
                (username, email)
            )
            if cursor.fetchone():
                return False, "Username or email already exists"

            # Create user
            hashed_password = self.hash_password(password)
            unique_id = str(uuid.uuid4())

            query = """
                INSERT INTO users (unique_id, username, password_hash, email, location, created_at) 
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (unique_id, username, hashed_password, email, location))
            self.connection.commit()
            return True, "User created successfully"

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
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            hashed_password = self.hash_password(password)
            query = """
                SELECT u.*, 
                       COUNT(DISTINCT d.id) as total_donations,
                       COUNT(DISTINCT r.id) as total_requests,
                       COUNT(DISTINCT m.id) as total_messages
                FROM users u
                LEFT JOIN donations d ON u.unique_id = d.donor_id
                LEFT JOIN requests r ON u.unique_id = r.requester_id
                LEFT JOIN messages m ON u.unique_id = m.sender_id
                WHERE u.username = %s AND u.password_hash = %s
                GROUP BY u.id
            """
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Error verifying user: {e}")
            return None
        finally:
            cursor.close()
            
    def create_donation(self, donor_id, title, description, category, condition, location, image_data=None):
        """Create a new donation with image data"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            unique_id = str(uuid.uuid4())
            query = """
                INSERT INTO donations 
                (unique_id, donor_id, title, description, category, `condition`, location, image_data, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            values = (unique_id, donor_id, title, description, category, condition, location, image_data)
            cursor.execute(query, values)
            self.connection.commit()
            return True, "Donation created successfully"
        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()
            
    def get_donations(self, search_term=None, category=None, condition=None, location=None):
        """Get all donations with optional filters"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT d.*, 
                       u.username as donor_name,
                       u.email as donor_email,
                       u.location as donor_location,
                       u.unique_id as donor_id,
                       COUNT(r.id) as request_count,
                       dl.status as delivery_status,
                       dl.tracking_number,
                       dl.estimated_date,
                       dl.actual_date
                FROM donations d
                JOIN users u ON d.donor_id = u.unique_id
                LEFT JOIN requests r ON d.unique_id = r.donation_id
                LEFT JOIN deliveries dl ON d.unique_id = dl.donation_id
                WHERE 1=1
            """
            params = []
            
            if search_term:
                query += " AND (d.title LIKE %s OR d.description LIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])
                
            if category:
                query += " AND d.category = %s"
                params.append(category)
                
            if condition:
                query += " AND d.condition = %s"
                params.append(condition)
                
            if location:
                query += " AND d.location LIKE %s"
                params.append(f"%{location}%")
                
            query += " GROUP BY d.unique_id ORDER BY d.created_at DESC"
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching donations: {e}")
            return []
        finally:
            cursor.close()

    def create_delivery(self, donation_id, requester_id, estimated_date):
        """Create a new delivery record"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            unique_id = str(uuid.uuid4())
            tracking_number = f"TRK{str(uuid.uuid4())[:8].upper()}"
            
            query = """
                INSERT INTO deliveries 
                (unique_id, donation_id, requester_id, tracking_number, status, estimated_date, created_at)
                VALUES (%s, %s, %s, %s, 'pending', %s, NOW())
            """
            cursor.execute(query, (unique_id, donation_id, requester_id, tracking_number, estimated_date))
            
            # Update donation status
            cursor.execute(
                "UPDATE donations SET status = 'in_delivery' WHERE unique_id = %s",
                (donation_id,)
            )
            
            self.connection.commit()
            return True, tracking_number
        except Error as e:
            self.connection.rollback()
            return False, str(e)
        finally:
            cursor.close()

    def update_delivery_status(self, tracking_number, status, actual_date=None):
        """Update delivery status"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            query = """
                UPDATE deliveries 
                SET status = %s, actual_date = %s, updated_at = NOW()
                WHERE tracking_number = %s
            """
            cursor.execute(query, (status, actual_date, tracking_number))
            
            if status == 'delivered':
                # Update donation status
                cursor.execute("""
                    UPDATE donations d
                    JOIN deliveries dl ON d.unique_id = dl.donation_id
                    SET d.status = 'completed'
                    WHERE dl.tracking_number = %s
                """, (tracking_number,))
                
            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def get_delivery_status(self, tracking_number):
        """Get delivery status and details"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT d.*, 
                       dn.title as donation_title,
                       u_donor.username as donor_name,
                       u_req.username as requester_name
                FROM deliveries d
                JOIN donations dn ON d.donation_id = dn.unique_id
                JOIN users u_donor ON dn.donor_id = u_donor.unique_id
                JOIN users u_req ON d.requester_id = u_req.unique_id
                WHERE d.tracking_number = %s
            """
            cursor.execute(query, (tracking_number,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching delivery status: {e}")
            return None
        finally:
            cursor.close()
            
    def create_request(self, requester_id, donation_id, message):
        """Create a new donation request"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            # Check if user already requested this donation
            cursor.execute(
                "SELECT id FROM requests WHERE requester_id = %s AND donation_id = %s",
                (requester_id, donation_id)
            )
            if cursor.fetchone():
                return False, "You have already requested this donation"

            unique_id = str(uuid.uuid4())
            query = """
                INSERT INTO requests 
                (unique_id, requester_id, donation_id, message, status, created_at)
                VALUES (%s, %s, %s, %s, 'pending', NOW())
            """
            cursor.execute(query, (unique_id, requester_id, donation_id, message))
            self.connection.commit()
            return True, "Request sent successfully"
        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()
            
    def get_requests(self, user_id, is_donor=False):
        """Get requests for a user (either as requester or donor)"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            if is_donor:
                query = """
                    SELECT r.*, 
                           u.username as requester_name,
                           d.title as donation_title,
                           d.category,
                           d.condition
                    FROM requests r
                    JOIN users u ON r.requester_id = u.unique_id
                    JOIN donations d ON r.donation_id = d.unique_id
                    WHERE d.donor_id = %s
                    ORDER BY r.created_at DESC
                """
            else:
                query = """
                    SELECT r.*, 
                           d.title as donation_title,
                           d.category,
                           d.condition,
                           u.username as donor_name
                    FROM requests r
                    JOIN donations d ON r.donation_id = d.unique_id
                    JOIN users u ON d.donor_id = u.unique_id
                    WHERE r.requester_id = %s
                    ORDER BY r.created_at DESC
                """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching requests: {e}")
            return []
        finally:
            cursor.close()
            
    def send_message(self, sender_id, receiver_id, content, donation_id=None):
        """Send a message between users"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            if not content.strip():
                return False, "Message content cannot be empty"
                
            unique_id = str(uuid.uuid4())
            query = """
                INSERT INTO messages (unique_id, sender_id, receiver_id, donation_id, content, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (unique_id, sender_id, receiver_id, donation_id, content))
            self.connection.commit()
            return True, "Message sent successfully"
        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()
            
    def get_messages(self, user_id, other_user_id=None):
        """Get messages for a user, optionally filtered by conversation"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            if other_user_id:
                query = """
                    SELECT m.*, 
                           s.username as sender_name,
                           r.username as receiver_name,
                           d.title as donation_title
                    FROM messages m
                    JOIN users s ON m.sender_id = s.unique_id
                    JOIN users r ON m.receiver_id = r.unique_id
                    LEFT JOIN donations d ON m.donation_id = d.unique_id
                    WHERE (m.sender_id = %s AND m.receiver_id = %s)
                       OR (m.sender_id = %s AND m.receiver_id = %s)
                    ORDER BY m.created_at ASC
                """
                cursor.execute(query, (user_id, other_user_id, other_user_id, user_id))
            else:
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
            
    def update_profile(self, user_id, email=None, location=None, current_password=None, new_password=None):
        """Update user profile information"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            updates = []
            params = []
            
            if email:
                # Check email uniqueness
                cursor.execute("SELECT id FROM users WHERE email = %s AND unique_id != %s", (email, user_id))
                if cursor.fetchone():
                    return False, "Email already in use"
                updates.append("email = %s")
                params.append(email)
                
            if location:
                updates.append("location = %s")
                params.append(location)
                
            if new_password:
                if not current_password:
                    return False, "Current password is required"
                    
                # Verify current password
                cursor.execute(
                    "SELECT id FROM users WHERE unique_id = %s AND password_hash = %s",
                    (user_id, self.hash_password(current_password))
                )
                if not cursor.fetchone():
                    return False, "Current password is incorrect"
                    
                updates.append("password_hash = %s")
                params.append(self.hash_password(new_password))
                
            if not updates:
                return True, "No changes to update"
                
            query = f"UPDATE users SET {', '.join(updates)} WHERE unique_id = %s"
            params.append(user_id)
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            return True, "Profile updated successfully"
        except Error as e:
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        finally:
            cursor.close()
            
    def get_user_stats(self, user_id):
        """Get user statistics"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        self.user_id = user_id
        try:
            query = """
                SELECT 
                    COUNT(DISTINCT d.id) as donations_made,
                    COUNT(DISTINCT r.id) as requests_made,
                    COUNT(DISTINCT m.id) as messages_sent,
                    u.created_at as join_date
                FROM users u
                LEFT JOIN donations d ON u.unique_id = d.donor_id
                LEFT JOIN requests r ON u.unique_id = r.requester_id
                LEFT JOIN messages m ON u.unique_id = m.sender_id
                WHERE u.unique_id = self.user_id
                GROUP BY u.id
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching user stats: {e}")
            return None
        finally:
            cursor.close()
            
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")
            
    def send_request(self, data):
        """Send a request for a donation"""
        self.ensure_connection()
        cursor = self.connection.cursor()
        
        try:
            query = """
                INSERT INTO requests 
                (unique_id, donation_id, requester_id, message, status, created_at)
                VALUES (%s, %s, %s, %s, 'pending', NOW())
            """
            values = (
                str(uuid.uuid4()),
                data['donation_id'],
                self.current_user['unique_id'],
                data['message']
            )
            cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            self.connection.rollback()
            print(f"Error sending request: {e}")
            return False
        finally:
            cursor.close()

    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = "SELECT * FROM users WHERE unique_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching user: {e}")
            return None
        finally:
            cursor.close()

    def get_user_conversations(self, user_id):
        """Get all conversations for a user"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT DISTINCT
                    u.unique_id,
                    u.username,
                    u.email,
                    m.created_at as last_message_time
                FROM users u
                JOIN messages m ON (u.unique_id = m.sender_id OR u.unique_id = m.receiver_id)
                WHERE (m.sender_id = %s OR m.receiver_id = %s)
                    AND u.unique_id != %s
                ORDER BY m.created_at DESC
            """
            cursor.execute(query, (user_id, user_id, user_id))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching conversations: {e}")
            return []
        finally:
            cursor.close()

    def get_conversation_messages(self, user_id, other_user_id):
        """Get messages between two users"""
        self.ensure_connection()
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            query = """
                SELECT m.*,
                       s.username as sender_name,
                       r.username as receiver_name
                FROM messages m
                JOIN users s ON m.sender_id = s.unique_id
                JOIN users r ON m.receiver_id = r.unique_id
                WHERE (m.sender_id = %s AND m.receiver_id = %s)
                   OR (m.sender_id = %s AND m.receiver_id = %s)
                ORDER BY m.created_at ASC
            """
            cursor.execute(query, (user_id, other_user_id, other_user_id, user_id))
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching messages: {e}")
            return []
        finally:
            cursor.close()