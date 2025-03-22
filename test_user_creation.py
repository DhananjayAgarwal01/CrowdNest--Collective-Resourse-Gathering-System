from src.database_handler import DatabaseHandler
import traceback
import uuid

def test_user_creation():
    try:
        db_handler = DatabaseHandler()
        
        # Generate unique username
        unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
        
        # Test user creation
        username = unique_username
        password = "testpass123"
        email = f"{unique_username}@example.com"
        location = "Test City"
        
        # Try to create user
        success, message = db_handler.create_user(username, password, email, location)
        print(f"User Creation - Success: {success}, Message: {message}")
        
        # Try to verify the newly created user
        user, verify_message = db_handler.verify_user(username, password)
        print(f"User Verification - User: {user}, Message: {verify_message}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_user_creation()
