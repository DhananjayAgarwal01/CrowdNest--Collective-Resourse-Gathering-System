import os
import uuid
import random
import traceback
from src.database.database_handler import DatabaseHandler
from src.constants import CATEGORIES, CONDITIONS, STATES

def generate_test_image(filename):
    """Generate a simple test image"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a blank image
    image = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add some text to the image
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((10, 10), f"Test Image: {filename}", fill='black', font=font)
    
    # Ensure test_images directory exists
    os.makedirs('test_images', exist_ok=True)
    
    # Save the image
    image_path = os.path.join('test_images', filename)
    image.save(image_path)
    return image_path

def test_donation_creation(num_donations=10):
    """
    Create multiple test donations with varied data
    
    :param num_donations: Number of test donations to create
    """
    try:
        # Initialize database handler
        db_handler = DatabaseHandler()
        
        # Create a test user
        unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
        username = unique_username
        password = "testpass123"
        email = f"{unique_username}@example.com"
        
        # Choose a random state
        test_state = random.choice(list(STATES.keys()))
        test_city = random.choice(STATES[test_state])
        
        # Create user
        user_success, user_message = db_handler.create_user(
            username, password, email, test_city
        )
        if not user_success:
            print(f"Failed to create user: {user_message}")
            return
        
        # Verify user to get unique_id
        user, verify_message = db_handler.verify_user(username, password)
        if not user:
            print(f"Failed to verify user: {verify_message}")
            return
        
        # Prepare and create multiple donations
        created_donations = []
        for i in range(num_donations):
            # Generate varied donation data
            donation_data = {
                'donor_id': user['unique_id'],
                'title': f"Test Donation {i+1}",
                'description': f"Description for test donation {i+1}. This is a detailed description of the item.",
                'category': random.choice(CATEGORIES),
                'condition': random.choice(CONDITIONS),
                'state': test_state,
                'city': test_city,
                'status': random.choice(['available', 'pending', 'reserved']),
                'image_data': generate_test_image(f'test_donation_{i+1}.png')
            }
            
            # Create donation
            donation_success, donation_message, donation_data = db_handler.create_donation(**donation_data)
            
            # Print and store results
            print(f"Donation {i+1} - Success: {donation_success}, Message: {donation_message}")
            
            if donation_success:
                # Add the full donation data to created_donations
                created_donations.append(donation_data)
        
        # Print summary
        print(f"\nSummary:")
        print(f"Created {len(created_donations)} test donations")
        print(f"Donor Username: {username}")
        print(f"Donor Email: {email}")
        print(f"Donor Location: {test_city}, {test_state}")
        
        return created_donations
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return None

def test_donation_request(donations):
    """
    Test donation request creation
    
    :param donations: List of donations to request
    """
    if not donations:
        print("No donations to request")
        return
    
    # Initialize database handler
    db_handler = DatabaseHandler()
    
    # Create a requester user
    unique_username = f"requester_{str(uuid.uuid4())[:8]}"
    username = unique_username
    password = "testrequestpass123"
    email = f"{unique_username}@example.com"
    
    # Choose a random state
    test_state = random.choice(list(STATES.keys()))
    test_city = random.choice(STATES[test_state])
    
    # Create requester user
    user_success, user_message = db_handler.create_user(
        username, password, email, test_city
    )
    if not user_success:
        print(f"Failed to create requester user: {user_message}")
        return
    
    # Verify requester user
    user, verify_message = db_handler.verify_user(username, password)
    if not user:
        print(f"Failed to verify requester user: {verify_message}")
        return
    
    # Request random donations
    num_requests = min(3, len(donations))
    requested_donations = random.sample(donations, num_requests)
    
    for donation in requested_donations:
        # Create donation request
        request_message = f"I would like to request the {donation['title']} for my needs."
        request_id = db_handler.create_request(
            requester_id=user['unique_id'], 
            donation_id=donation['unique_id'], 
            request_message=request_message
        )
        
        if request_id:
            print(f"Request created for donation: {donation['title']}")
        else:
            print(f"Failed to create request for donation: {donation['title']}")

if __name__ == "__main__":
    # Create test donations
    test_donations = test_donation_creation()
    
    # Create test donation requests
    if test_donations:
        test_donation_request(test_donations)
