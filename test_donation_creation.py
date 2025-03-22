from src.database_handler import DatabaseHandler
import uuid
import traceback

def test_donation_creation():
    try:
        # Initialize database handler
        db_handler = DatabaseHandler()
        
        # Create a test user first
        unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
        username = unique_username
        password = "testpass123"
        email = f"{unique_username}@example.com"
        location = "Test City"
        
        # Create user
        user_success, user_message = db_handler.create_user(username, password, email, location)
        if not user_success:
            print(f"Failed to create user: {user_message}")
            return
        
        # Verify user to get unique_id
        user, verify_message = db_handler.verify_user(username, password)
        if not user:
            print(f"Failed to verify user: {verify_message}")
            return
        
        # Prepare donation data
        donation_data = {
            'donor_id': user['unique_id'],
            'title': 'Test Donation',
            'description': 'This is a test donation for creating a new item',
            'category': 'Electronics',
            'condition': 'Good',
            'state': 'Test State',
            'city': 'Test City',
            'image_data': None  # Optional: you can add an image path or bytes here
        }
        
        # Create donation
        donation_success, donation_message = db_handler.create_donation(**donation_data)
        
        # Print results
        print(f"Donation Creation - Success: {donation_success}, Message: {donation_message}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_donation_creation()
