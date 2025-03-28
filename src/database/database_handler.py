import mysql.connector
import hashlib
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime

class DatabaseHandler:
    def __init__(self, host=None, user=None, password=None, database=None):
        """
        Initialize database connection parameters and connection
        
        :param host: Database host (optional, uses env var or default)
        :param user: Database user (optional, uses env var or default)
        :param password: Database password (optional, uses env var or default)
        :param database: Database name (optional, uses env var or default)
        """
        # Load environment variables
        load_dotenv()
        
        # Store connection parameters with fallback to environment variables
        self.connection_params = {
            'host': host or os.getenv('DB_HOST', 'localhost'),
            'user': user or os.getenv('DB_USER', 'root'),
            'password': password or os.getenv('DB_PASSWORD', '12345678'),
            'database': database or os.getenv('DB_NAME', 'CrowdNest'),
            'buffered': True
        }
        
        # Initialize connection and cursor
        self.connection = None
        self.cursor = None
        
        # Establish initial connection
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            # Establish connection
            self.connection = mysql.connector.connect(
                host=self.connection_params['host'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                database=self.connection_params['database'],
                buffered=True
            )
            
            # Create cursor with dictionary support
            self.cursor = self.connection.cursor(dictionary=True)
            
            print("Successfully connected to MySQL database")
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL Platform: {e}")
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
        """
        Legacy method to maintain backwards compatibility with existing calls
        
        :param donor_id: Unique ID of the donor
        :param title: Title of the donation
        :param description: Description of the donation
        :param category: Category of the donation
        :param condition: Condition of the donated item
        :param state: State where the donation is located
        :param city: City where the donation is located
        :param image_path: Optional path to donation image
        :return: Boolean indicating success
        """
        try:
            # If image_path is a file path, read the image data
            image_data = None
            image_type = None
            if image_path and os.path.isfile(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                image_type = os.path.splitext(image_path)[1][1:].lower()  # e.g., 'png', 'jpg'
            
            # Use create_donation method
            success, message, donation_data = self.create_donation(
                donor_id=donor_id,
                title=title,
                description=description,
                category=category,
                condition=condition,
                state=state,
                city=city,
                image_data=image_data,
                image_type=image_type
            )
            
            return success
        
        except Exception as e:
            print(f"Error in add_donation: {e}")
            return False
    
    def search_donations(self, search_query=None, category=None, location=None, title=None):
        """Search donations based on criteria"""
        try:
            base_query = """
            SELECT 
                d.unique_id,
                d.title,
                d.description,
                d.category,
                d.condition,
                d.state,
                d.city,
                d.status,
                d.created_at,
                d.image_path,
                u.username as donor_name,
                u.email as donor_email
            FROM 
                donations d
            JOIN 
                users u ON d.donor_id = u.unique_id
            WHERE 1=1
            """
            params = []

            if search_query:
                base_query += " AND (d.title LIKE %s OR d.description LIKE %s)"
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            if category and category != 'All Categories':
                base_query += " AND d.category = %s"
                params.append(category)

            if location and location != 'All Locations':
                base_query += " AND (d.state = %s OR d.city = %s)"
                params.extend([location, location])

            if title:
                base_query += " AND d.title LIKE %s"
                params.append(f"%{title}%")

            base_query += " ORDER BY d.created_at DESC"
            
            self.cursor.execute(base_query, params)
            results = self.cursor.fetchall()
            
            # Ensure results are dictionaries
            donations = []
            for result in results:
                # Ensure each result is a dictionary with expected keys
                if not isinstance(result, dict):
                    print(f"WARNING: Non-dictionary result: {type(result)}")
                    continue
                
                donation = {
                    'unique_id': result.get('unique_id', 'N/A'),
                    'title': result.get('title', 'N/A'),
                    'description': result.get('description', 'N/A'),
                    'category': result.get('category', 'N/A'),
                    'condition': result.get('condition', 'N/A'),
                    'state': result.get('state', 'N/A'),
                    'city': result.get('city', 'N/A'),
                    'status': result.get('status', 'N/A'),
                    'created_at': result.get('created_at', 'N/A'),
                    'image_path': result.get('image_path', 'N/A'),
                    'donor_name': result.get('donor_name', 'N/A'),
                    'donor_email': result.get('donor_email', 'N/A')
                }
                donations.append(donation)
            
            return donations
            
        except mysql.connector.Error as e:
            print(f"Error searching donations: {e}")
            return []
    
    def get_donation_details(self, donation_id):
        """
        Retrieve full details of a specific donation

        :param donation_id: Unique ID of the donation
        :return: Dictionary with donation details or None
        """
        # Reset cursor to ensure clean state
        self.reset_cursor()

        try:
            # Validate input
            if not donation_id:
                print("Error: Empty donation ID provided")
                return None
            
            # Use dictionary cursor for more robust result handling
            self.cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                d.unique_id, 
                d.title, 
                d.description, 
                d.category, 
                d.`condition`, 
                d.state, 
                d.city, 
                d.image_path, 
                d.image_data,
                d.image_type,
                d.status, 
                d.created_at,
                u.username as donor_name,
                u.email as donor_email
            FROM 
                donations d
            JOIN 
                users u ON d.donor_id = u.unique_id
            WHERE 
                d.unique_id = %s OR d.title LIKE %s
            """
            
            # Execute the query with two possible matching conditions
            self.cursor.execute(query, (donation_id, f'%{donation_id}%'))
            
            # Fetch the result
            result = self.cursor.fetchone()
            
            if result:
                # Safely convert result to dictionary
                donation_details = {
                    'unique_id': result.get('unique_id', 'N/A'),
                    'title': result.get('title', 'N/A'),
                    'description': result.get('description', 'N/A'),
                    'category': result.get('category', 'N/A'),
                    'condition': result.get('condition', 'N/A'),
                    'state': result.get('state', 'N/A'),
                    'city': result.get('city', 'N/A'),
                    'image_path': result.get('image_path', 'N/A'),
                    'image_data': result.get('image_data', None),
                    'image_type': result.get('image_type', None),
                    'status': result.get('status', 'N/A'),
                    'created_at': result.get('created_at', 'N/A'),
                    'donor_name': result.get('donor_name', 'N/A'),
                    'donor_email': result.get('donor_email', 'N/A')
                }
                return donation_details
            else:
                # Log additional diagnostic information
                print(f"No donation found with ID or Title: {donation_id}")
                
                # Additional diagnostic query to understand what's in the database
                diagnostic_query = """
                SELECT unique_id, title FROM donations 
                WHERE unique_id LIKE %s OR title LIKE %s
                """
                self.cursor.execute(diagnostic_query, (f'%{donation_id}%', f'%{donation_id}%'))
                similar_donations = self.cursor.fetchall()
                
                if similar_donations:
                    print("Similar donations found:")
                    for donation in similar_donations:
                        print(f"ID: {donation.get('unique_id', 'N/A')}, Title: {donation.get('title', 'N/A')}")
                
                return None
        
        except mysql.connector.Error as e:
            print(f"MySQL Error retrieving donation details: {e}")
            # Log the specific error details
            print(f"Error Code: {e.errno}")
            print(f"SQL State: {e.sqlstate}")
            print(f"Error Message: {e.msg}")
            return None
        except Exception as e:
            print(f"Unexpected error retrieving donation details: {e}")
            # Capture the full traceback for debugging
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Always reset the cursor
            self.reset_cursor()
    
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
    
    def create_request(self, requester_id, title=None, description=None, category=None, state=None, city=None, donation_id=None, request_message=None):
        """
        Create a request with flexible parameters for general and donation-specific requests

        :param requester_id: Unique ID of the requester
        :param title: Title of the request (optional for general requests)
        :param description: Description of the request (optional)
        :param category: Category of the request (optional)
        :param state: State for the request (optional)
        :param city: City for the request (optional)
        :param donation_id: Unique ID of the donation (optional, for donation-specific requests)
        :param request_message: Message for donation request (optional)
        :return: Unique ID of the created request or None
        """
        try:
            # Generate unique ID for the request
            unique_id = str(uuid.uuid4())
            
            # Determine request type based on parameters
            if donation_id:
                # Verify that the donation exists
                verify_donation_query = "SELECT unique_id FROM donations WHERE unique_id = %s"
                self.cursor.execute(verify_donation_query, (donation_id,))
                donation = self.cursor.fetchone()
                
                if not donation:
                    print(f"Donation with ID {donation_id} does not exist.")
                    return None

                # Check if a request already exists
                existing_request_query = """
                SELECT unique_id FROM donation_requests 
                WHERE requester_id = %s AND donation_id = %s
                """
                self.cursor.execute(existing_request_query, (requester_id, donation_id))
                existing_request = self.cursor.fetchone()
                
                if existing_request:
                    print("Donation request already exists")
                    return existing_request['unique_id']
                
                # Insert donation request
                query = """
                INSERT INTO donation_requests 
                (unique_id, requester_id, donation_id, request_message, status, created_at) 
                VALUES (%s, %s, %s, %s, 'pending', NOW())
                """
                
                # Execute the query
                self.cursor.execute(query, (
                    unique_id,
                    requester_id,
                    donation_id,
                    request_message or ''
                ))
            else:
                # Insert general request
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
            print(f"Error creating request: {e}")
            self.connection.rollback()
            return None
    
    def search_requests(self, search_query=None, category=None, location=None, status=None):
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

            if status:
                base_query += " AND r.status = %s"
                params.append(status)

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
    
    def get_user_donation_history(self, user_id):
        """
        Retrieve donation history for a specific user
        
        :param user_id: Unique ID of the user
        :return: List of donations made by the user
        """
        try:
            query = """
            SELECT d.*, u.username as donor_name, u.email as donor_email
            FROM donations d
            JOIN users u ON d.donor_id = u.unique_id
            WHERE d.donor_id = %s
            ORDER BY d.created_at DESC
            """
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        
        except mysql.connector.Error as e:
            print(f"Error fetching donation history: {e}")
            return []

    def get_user_donation_requests(self, user_id):
        """
        Retrieve donation requests for a specific user
        
        :param user_id: Unique ID of the user
        :return: List of donation requests made by the user
        """
        try:
            query = """
            SELECT 
                r.unique_id,
                r.requester_id,
                r.donation_id,
                r.request_message,
                r.status,
                r.created_at,
                d.title as donation_title, 
                d.category as donation_category,
                d.description as donation_description,
                u_requester.username as requester_name,
                u_requester.email as requester_email,
                u_donor.username as donor_name,
                u_donor.email as donor_email
            FROM donation_requests r
            JOIN donations d ON r.donation_id = d.unique_id
            JOIN users u_requester ON r.requester_id = u_requester.unique_id
            JOIN users u_donor ON d.donor_id = u_donor.unique_id
            WHERE r.requester_id = %s OR d.donor_id = %s
            ORDER BY r.created_at DESC
            """
            self.cursor.execute(query, (user_id, user_id))
            return self.cursor.fetchall()
        
        except mysql.connector.Error as e:
            print(f"Error fetching user donation requests: {e}")
            return []

    def update_donation_request_status(self, request_id, status, user_id):
        """
        Update the status of a donation request

        :param request_id: Unique ID of the request
        :param status: New status (e.g., 'approved', 'rejected')
        :param user_id: ID of the user updating the status
        :return: Boolean indicating success
        """
        try:
            # Verify user's permission to update
            verify_query = """
            SELECT d.donor_id 
            FROM donation_requests r
            JOIN donations d ON r.donation_id = d.unique_id
            WHERE r.unique_id = %s
            """
            self.cursor.execute(verify_query, (request_id,))
            result = self.cursor.fetchone()
            
            if not result or result['donor_id'] != user_id:
                print("Unauthorized to update request status")
                return False
            
            # Update request status
            update_query = """
            UPDATE donation_requests 
            SET status = %s, updated_at = %s 
            WHERE unique_id = %s
            """
            
            current_time = datetime.now()
            self.cursor.execute(update_query, (status, current_time, request_id))
            self.connection.commit()
            
            return True
        
        except mysql.connector.Error as e:
            print(f"Error updating donation request status: {e}")
            self.connection.rollback()
            return False
    
    def get_donation_donor_details(self, donation_id):
        """
        Retrieve donor details for a specific donation

        :param donation_id: Unique ID of the donation
        :return: Dictionary with donor details or None
        """
        try:
            query = """
            SELECT 
                u.unique_id,
                u.username,
                u.full_name,
                u.email,
                u.state,
                d.title as donation_title
            FROM donations d
            JOIN users u ON d.donor_id = u.unique_id
            WHERE d.unique_id = %s
            """
            self.cursor.execute(query, (donation_id,))
            donor_details = self.cursor.fetchone()
            
            return donor_details
        
        except mysql.connector.Error as e:
            print(f"Error fetching donation donor details: {e}")
            return None
    
    def get_all_donation_requests(self):
        """
        Retrieve all donation requests for admin or system-wide view

        :return: List of dictionaries containing donation request details
        """
        try:
            query = """
            SELECT 
                dr.unique_id,
                dr.requester_id,
                dr.donation_id,
                dr.request_message,
                dr.status,
                dr.created_at,
                d.title as donation_title,
                d.category as donation_category,
                d.description as donation_description,
                u_requester.full_name as requester_name,
                u_requester.email as requester_email,
                u_donor.full_name as donor_name,
                u_donor.email as donor_email
            FROM donation_requests dr
            JOIN donations d ON dr.donation_id = d.unique_id
            JOIN users u_requester ON dr.requester_id = u_requester.unique_id
            JOIN users u_donor ON d.donor_id = u_donor.unique_id
            ORDER BY dr.created_at DESC
            """
            
            self.cursor.execute(query)
            requests = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            request_list = []
            for req in requests:
                request_list.append({
                    'unique_id': req['unique_id'],
                    'requester_id': req['requester_id'],
                    'donation_id': req['donation_id'],
                    'request_message': req['request_message'],
                    'status': req['status'],
                    'created_at': req['created_at'],
                    'donation_title': req['donation_title'],
                    'donation_category': req['donation_category'],
                    'donation_description': req['donation_description'],
                    'requester_name': req['requester_name'],
                    'requester_email': req['requester_email'],
                    'donor_name': req['donor_name'],
                    'donor_email': req['donor_email']
                })
            
            return request_list
        
        except mysql.connector.Error as e:
            print(f"Error fetching all donation requests: {e}")
            return []
    
    def create_user(self, username, password, email, location=None):
        """
        Create a new user in the database

        :param username: Unique username for the user
        :param password: User's password (will be hashed)
        :param email: User's email address
        :param location: Optional location information
        :return: Tuple (success_bool, message_str)
        """
        try:
            # Check if username or email already exists
            check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
            self.cursor.execute(check_query, (username, email))
            existing_user = self.cursor.fetchone()
            
            if existing_user:
                return False, "Username or email already exists"
            
            # Hash the password
            hashed_password = self.hash_password(password)
            
            # Generate unique ID
            unique_id = str(uuid.uuid4())
            
            # Prepare the query
            query = """
            INSERT INTO users 
            (unique_id, username, email, password_hash, location, created_at) 
            VALUES (%s, %s, %s, %s, %s, NOW())
            """
            
            # Execute the query
            self.cursor.execute(query, (
                unique_id,
                username,
                email,
                hashed_password,
                location
            ))
            
            # Commit the transaction
            self.connection.commit()
            
            return True, "User created successfully"
        
        except mysql.connector.Error as e:
            print(f"Error creating user: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        
    def verify_user(self, username, password):
        """
        Verify user credentials and return user details

        :param username: Username to verify
        :param password: Password to verify
        :return: Tuple (user_dict or None, message_str)
        """
        try:
            # Hash the provided password
            hashed_password = self.hash_password(password)
            
            # Prepare the query
            query = """
            SELECT * FROM users 
            WHERE username = %s AND password_hash = %s
            """
            
            # Execute the query
            self.cursor.execute(query, (username, hashed_password))
            user = self.cursor.fetchone()
            
            if user:
                return user, "User verified successfully"
            else:
                return None, "Invalid username or password"
        
        except mysql.connector.Error as e:
            print(f"Error verifying user: {e}")
            return None, f"Database error: {str(e)}"
    
    def create_donation(self, donor_id, title, description, category, condition, state, city, status='available', image_data=None, image_type=None):
        """
        Create a new donation in the database

        :param donor_id: Unique ID of the donor
        :param title: Title of the donation
        :param description: Description of the donation
        :param category: Category of the donation
        :param condition: Condition of the donated item
        :param state: State where the donation is located
        :param city: City where the donation is located
        :param status: Status of the donation (default 'available')
        :param image_data: Optional image data (bytes)
        :param image_type: Optional image type (e.g., 'png', 'jpeg')
        :return: Tuple (success_bool, message_str, donation_dict)
        """
        try:
            # Verify donor exists and get their email
            verify_donor_query = "SELECT email, username FROM users WHERE unique_id = %s"
            self.cursor.execute(verify_donor_query, (donor_id,))
            donor = self.cursor.fetchone()
            
            if not donor:
                return False, f"Donor with ID {donor_id} does not exist", None
            
            # Extract donor email and username
            donor_email = donor.get('email')
            donor_username = donor.get('username')
            
            # Generate unique ID for the donation
            unique_id = str(uuid.uuid4())
            
            # Prepare the query with escaped keywords
            query = """
            INSERT INTO donations 
            (unique_id, donor_id, title, description, category, 
            `condition`, state, city, status, image_data, image_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                status,
                image_data,  # Raw image bytes or None
                image_type   # Image type or None
            ))
            
            # Commit the transaction
            self.connection.commit()
            
            # Prepare donation dictionary
            donation_data = {
                'unique_id': unique_id,
                'donor_id': donor_id,
                'donor_email': donor_email,
                'donor_username': donor_username,
                'title': title,
                'description': description,
                'category': category,
                'condition': condition,
                'state': state,
                'city': city,
                'status': status,
                'image_type': image_type
            }
            
            return True, f"Donation '{title}' created successfully with ID {unique_id}", donation_data
        
        except mysql.connector.Error as e:
            print(f"Error creating donation: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}", None
    
    def update_donation_status(self, donation_id, new_status):
        """
        Update the status of a donation

        :param donation_id: Unique ID of the donation
        :param new_status: New status for the donation
        :return: Tuple (success_bool, message_str)
        """
        try:
            # Validate status
            valid_statuses = ['available', 'pending', 'reserved', 'completed', 'withdrawn']
            if new_status not in valid_statuses:
                return False, f"Invalid status. Must be one of {valid_statuses}"
            
            # Prepare the query
            query = """
            UPDATE donations 
            SET status = %s, updated_at = NOW() 
            WHERE unique_id = %s
            """
            
            # Execute the query
            self.cursor.execute(query, (new_status, donation_id))
            
            # Check if any rows were affected
            if self.cursor.rowcount == 0:
                return False, f"No donation found with ID {donation_id}"
            
            # Commit the transaction
            self.connection.commit()
            
            return True, f"Donation status updated to {new_status}"
        
        except mysql.connector.Error as e:
            print(f"Error updating donation status: {e}")
            self.connection.rollback()
            return False, f"Database error: {str(e)}"
        except Exception as e:
            print(f"Unexpected error updating donation status: {e}")
            self.connection.rollback()
            return False, f"Unexpected error: {str(e)}"
    
    def get_donation_status(self, donation_id):
        """
        Retrieve the current status of a donation

        :param donation_id: Unique ID of the donation
        :return: Tuple (status_str or None, message_str)
        """
        try:
            # Prepare the query
            query = """
            SELECT status FROM donations 
            WHERE unique_id = %s
            """
            
            # Execute the query
            self.cursor.execute(query, (donation_id,))
            
            # Fetch the result
            result = self.cursor.fetchone()
            
            if result:
                return result[0], "Donation status retrieved successfully"
            else:
                return None, f"No donation found with ID {donation_id}"
        
        except mysql.connector.Error as e:
            print(f"Error retrieving donation status: {e}")
            return None, f"Database error: {str(e)}"
        except Exception as e:
            print(f"Unexpected error retrieving donation status: {e}")
            return None, f"Unexpected error: {str(e)}"
    
    def reset_cursor(self):
        """Reset the database cursor"""
        try:
            # Close existing cursor if it exists
            if self.cursor:
                self.cursor.close()
            
            # Recreate cursor with dictionary support
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            print(f"Error resetting cursor: {e}")
            # Attempt to reconnect if cursor reset fails
            try:
                self.connect()
            except Exception as reconnect_error:
                print(f"Failed to reconnect: {reconnect_error}")
                raise
    
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

    def create_donation_request(self, user_id, title, description, category, condition, state, city, urgency=None):
        """
        Create a new donation request

        :param user_id: ID of the user creating the request
        :param title: Title of the donation request
        :param description: Detailed description of the needed donation
        :param category: Category of the donation
        :param condition: Condition of the requested item
        :param state: State where the donation is needed
        :param city: City where the donation is needed
        :param urgency: Optional urgency level of the request
        :return: Tuple (success, message, request_id)
        """
        try:
            # Validate input
            if not all([user_id, title, description, category, condition, state, city]):
                return False, "All fields are required", None
            
            # Prepare the SQL query
            query = """
            INSERT INTO donation_requests (
                requester_id, 
                title, 
                description, 
                category, 
                `condition`, 
                state, 
                city, 
                urgency, 
                status, 
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            """
            
            # Set default status and handle optional urgency
            status = 'OPEN'
            urgency = urgency or 'MEDIUM'
            
            # Execute the query
            self.cursor.execute(query, (
                user_id, 
                title, 
                description, 
                category, 
                condition, 
                state, 
                city, 
                urgency, 
                status
            ))
            
            # Commit the transaction
            self.connection.commit()
            
            # Get the ID of the newly created request
            request_id = self.cursor.lastrowid
            
            return True, "Donation request created successfully", request_id
        
        except mysql.connector.Error as e:
            # Rollback in case of error
            self.connection.rollback()
            
            print(f"MySQL Error creating donation request: {e}")
            return False, f"Database error: {e}", None
        
        except Exception as e:
            # Rollback in case of unexpected error
            self.connection.rollback()
            
            print(f"Unexpected error creating donation request: {e}")
            return False, f"Unexpected error: {e}", None

    def get_user_donation_requests(self, user_id):
        """
        Retrieve all donation requests for a specific user

        :param user_id: ID of the user
        :return: List of donation requests or None
        """
        try:
            # Prepare the SQL query
            query = """
            SELECT 
                unique_id,
                title, 
                description, 
                category, 
                `condition`, 
                state, 
                city, 
                urgency,
                status,
                created_at
            FROM 
                donation_requests
            WHERE 
                requester_id = %s
            ORDER BY 
                created_at DESC
            """
            
            # Execute the query
            self.cursor.execute(query, (user_id,))
            
            # Fetch all results
            results = self.cursor.fetchall()
            
            # Convert results to list of dictionaries
            donation_requests = []
            for result in results:
                request = {
                    'unique_id': result[0],
                    'title': result[1],
                    'description': result[2],
                    'category': result[3],
                    'condition': result[4],
                    'state': result[5],
                    'city': result[6],
                    'urgency': result[7],
                    'status': result[8],
                    'created_at': result[9]
                }
                donation_requests.append(request)
            
            return donation_requests
        
        except mysql.connector.Error as e:
            print(f"MySQL Error retrieving donation requests: {e}")
            return None
        
        except Exception as e:
            print(f"Unexpected error retrieving donation requests: {e}")
            return None

    def send_donor_contact_email(self, sender_id, recipient_email, subject, message):
        """
        Send a contact email to the donor
        
        :param sender_id: Unique ID of the user sending the email
        :param recipient_email: Email address of the recipient
        :param subject: Subject of the email
        :param message: Body of the email
        :return: Boolean indicating if email was sent successfully
        """
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            import os
            import re
            from src.utils.html_email_templates import HTMLEmailTemplates
            
            # Validate inputs
            if not all([sender_id, recipient_email, subject, message]):
                print("Error: Missing required email parameters")
                return False
            
            # First, verify the sender exists
            sender_query = "SELECT username, email FROM users WHERE unique_id = %s"
            self.cursor.execute(sender_query, (sender_id,))
            sender = self.cursor.fetchone()
            
            if not sender:
                print(f"Error: Sender with ID {sender_id} not found")
                return False
            
            # Validate recipient email format
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, recipient_email):
                print(f"Error: Invalid recipient email format: {recipient_email}")
                return False
            
            # Prepare email details
            sender_name = sender.get('username', 'Unknown User')
            sender_email = sender.get('email', '')
            
            # Fetch a recent donation title for context
            try:
                # Fetch donation title by donor's unique_id from users table
                donation_query = """
                SELECT d.title 
                FROM donations d
                JOIN users u ON d.donor_id = u.unique_id
                WHERE u.email = %s
                ORDER BY d.created_at DESC 
                LIMIT 1
                """
                self.cursor.execute(donation_query, (recipient_email,))
                donation_result = self.cursor.fetchone()
                donation_item = donation_result.get('title', 'an item') if donation_result else 'an item'
            except Exception as donation_err:
                print(f"Error fetching donation title: {donation_err}")
                donation_item = 'an item'
            
            # Prepare SMTP connection
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_email = os.getenv('SMTP_EMAIL')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if not all([smtp_server, smtp_port, smtp_email, smtp_password]):
                print("Error: SMTP configuration is incomplete")
                return False
            
            # Create HTML email template
            html_content = HTMLEmailTemplates.request_donation_template(
                requester_name=sender_name, 
                donator_name=sender_name, 
                donation_item=donation_item, 
                additional_message=message
            )
            
            # Create email message
            email_msg = HTMLEmailTemplates.create_mime_message(
                subject=subject, 
                html_content=html_content, 
                from_email=f"{sender_name} via CrowdNest <{smtp_email}>", 
                to_email=recipient_email
            )
            
            # Insert email communication record
            email_log_query = """
            INSERT INTO email_communications 
            (sender_id, recipient_email, subject, message, sent_at, status) 
            VALUES (%s, %s, %s, %s, NOW(), %s)
            """
            
            # Attempt to send email
            try:
                # Create SMTP connection
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    # Start TLS for security
                    server.starttls()
                    
                    # Login to the server
                    server.login(smtp_email, smtp_password)
                    
                    # Send email
                    server.send_message(email_msg)
                
                # If email sent successfully, log with 'sent' status
                self.cursor.execute(email_log_query, (
                    sender_id, 
                    recipient_email, 
                    subject, 
                    message,
                    'sent'
                ))
                
                # Commit the transaction
                self.connection.commit()
                
                print(f"Email sent successfully to {recipient_email}")
                return True
            
            except smtplib.SMTPException as smtp_err:
                # Log email sending failure
                print(f"SMTP Error sending email: {smtp_err}")
                
                # Insert record with 'failed' status
                self.cursor.execute(email_log_query, (
                    sender_id, 
                    recipient_email, 
                    subject, 
                    message,
                    'failed'
                ))
                
                # Commit the transaction
                self.connection.commit()
                
                return False
        
        except mysql.connector.Error as e:
            # Rollback in case of database error
            self.connection.rollback()
            print(f"Database error sending email: {e}")
            print(f"Error Code: {e.errno}")
            print(f"SQL State: {e.sqlstate}")
            print(f"Error Message: {e.msg}")
            
            return False
        except Exception as e:
            # Rollback in case of any other error
            self.connection.rollback()
            print(f"Unexpected error sending email: {e}")
            import traceback
            traceback.print_exc()
            return False
