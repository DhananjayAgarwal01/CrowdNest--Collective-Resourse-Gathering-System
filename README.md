# DonateShare - Item Donation Platform

A desktop application built with Python, Tkinter, and Flask that allows users to donate and request items, chat with other users, and manage their donations.

## Features

- User authentication (login/register)
- Create and browse donations
- Real-time messaging between users
- User profile management
- Search functionality for donations
- Modern and intuitive UI

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- Tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd donateshare
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Configure the application:
   - Open `database_handler.py` and update the `DB_CONFIG` dictionary with your MySQL credentials:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'your_mysql_username',
       'password': 'your_mysql_password',
       'database': 'donateshare'
   }
   ```
   - Open `flask_routes.py` and update the `SECRET_KEY` with a secure key:
   ```python
   SECRET_KEY = 'your-secure-secret-key'
   ```

5. Initialize the database:
```bash
python db_init.py
```

## Usage

1. Start the application:
```bash
python tkinter_app.py
```

2. Register a new account or login with existing credentials

3. Use the navigation buttons to:
   - View and create donations
   - Browse available items
   - Chat with other users
   - Manage your profile

## Project Structure

- `tkinter_app.py`: Main application file with Tkinter UI
- `flask_routes.py`: Flask backend routes
- `database_handler.py`: Database operations
- `db_init.py`: Database initialization script

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 