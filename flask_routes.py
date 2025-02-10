from flask import Flask, request, jsonify
from database_handler import DatabaseHandler
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta

# Flask configuration
SECRET_KEY = '123456shfowef13'  # Change this to a secure secret key in production

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
db = DatabaseHandler()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route('/')
def index():
    return jsonify({'message': 'CrowdNest API is running'})

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'message': 'No data provided'}), 400

        required_fields = ['username', 'password', 'email', 'state', 'city']
        if not all(field in data for field in required_fields):
            return jsonify({
                'message': 'Missing required fields',
                'required': required_fields
            }), 400

        # Validate inputs
        if len(data['username']) < 3:
            return jsonify({'message': 'Username must be at least 3 characters long'}), 400
        if len(data['password']) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        if '@' not in data['email']:
            return jsonify({'message': 'Invalid email format'}), 400

        # Combine state and city into location
        location = f"{data['city']}, {data['state']}"

        # Create user in database
        success = db.create_user(data['username'], data['password'], data['email'], location)
        if success:
            return jsonify({
                'message': 'User created successfully',
                'username': data['username']
            }), 201
        else:
            return jsonify({'message': 'Username or email already exists'}), 409

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
            
        if not all(k in data for k in ('username', 'password')):
            return jsonify({'message': 'Missing username or password'}), 400
            
        user = db.verify_user(data['username'], data['password'])
        
        if user:
            token = jwt.encode({
                'user_id': user['unique_id'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'])
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user['unique_id'],
                    'username': user['username'],
                    'email': user['email'],
                    'location': user['location']
                }
            })
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/donations', methods=['GET', 'POST'])
@token_required
def donations(current_user):
    if request.method == 'POST':
        try:
            data = request.get_json()
            print(f"Received donation data: {data}")
            
            # Check for required fields
            required_fields = ['title', 'description', 'category', 'condition', 'location']
            if not all(k in data for k in required_fields):
                missing = [k for k in required_fields if k not in data]
                return jsonify({
                    'message': 'Missing required fields',
                    'missing_fields': missing
                }), 400
                
            # Validate field lengths
            if len(data['title']) > 100:
                return jsonify({'message': 'Title must be less than 100 characters'}), 400
            if len(data['description']) > 500:
                return jsonify({'message': 'Description must be less than 500 characters'}), 400
                
            print(f"Creating donation for user: {current_user}")
            # Create donation using the current_user directly (it's the user_id from token)
            if db.create_donation(
                current_user,  # current_user is already the user_id
                data['title'],
                data['description'],
                data['category'],
                data['condition'],
                data['location'],
                data.get('image_path')  # Make image optional
            ):
                return jsonify({'message': 'Donation created successfully'}), 201
            else:
                return jsonify({'message': 'Error creating donation in database'}), 400
                
        except Exception as e:
            print(f"Error in donation creation: {str(e)}")
            return jsonify({'message': f'Server error: {str(e)}'}), 500
    
    else:  # GET
        try:
            search_term = request.args.get('search')
            donations = db.get_donations(search_term)
            return jsonify(donations)
        except Exception as e:
            print(f"Error fetching donations: {str(e)}")
            return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/requests', methods=['POST'])
@token_required
def create_request(current_user):
    data = request.get_json()
    
    if not all(k in data for k in ('donation_id', 'message')):
        return jsonify({'message': 'Missing required fields'}), 400
        
    if db.create_request(current_user, data['donation_id'], data['message']):
        return jsonify({'message': 'Request created successfully'}), 201
    else:
        return jsonify({'message': 'Error creating request'}), 400

@app.route('/api/messages', methods=['GET', 'POST'])
@token_required
def messages(current_user):
    if request.method == 'POST':
        data = request.get_json()
        
        if not all(k in data for k in ('receiver_id', 'content')):
            return jsonify({'message': 'Missing required fields'}), 400
            
        if db.send_message(
            current_user,
            data['receiver_id'],
            data['content'],
            data.get('donation_id')
        ):
            return jsonify({'message': 'Message sent successfully'}), 201
        else:
            return jsonify({'message': 'Error sending message'}), 400
    
    else:  # GET
        messages = db.get_messages(current_user)
        return jsonify(messages)

@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    
    if db.update_profile(
        current_user,
        email=data.get('email'),
        location=data.get('location')
    ):
        return jsonify({'message': 'Profile updated successfully'})
    else:
        return jsonify({'message': 'Error updating profile'}), 400

if __name__ == '__main__':
    app.run(debug=True) 