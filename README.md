# CrowdNest - Collective Resource Gathering System

CrowdNest is a desktop application built with Python and MySQL that facilitates resource sharing and donation management within communities. It features a modern Tkinter GUI and secure database operations.

## Features

- User authentication and profile management
- Donation creation and management
- Resource browsing and searching
- Messaging system between users
- Modern and intuitive user interface
- Location-based filtering
- Real-time updates

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CrowdNest.git
cd CrowdNest
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure MySQL:
- Create a MySQL database named `CrowdNest`
- Update the database configuration in `database_handler.py` with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'CrowdNest'
}
```

4. Initialize the database:
```bash
python db_init.py
```

## Running the Application

Start the application by running:
```bash
python tkinter_app.py
```

## Project Structure

- `tkinter_app.py`: Main application file with GUI implementation
- `database_handler.py`: Database operations and connection management
- `db_init.py`: Database initialization and schema creation
- `requirements.txt`: Project dependencies

## Database Schema

The application uses the following tables:
- `users`: User account information
- `donations`: Donation listings
- `requests`: Donation requests
- `messages`: User-to-user communication

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape CrowdNest
- Special thanks to the open-source community for the tools and libraries used in this project 