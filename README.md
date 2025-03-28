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
- Python 3.8+
- MySQL Server
- pip (Python package manager)

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

## Database Setup

1. Install MySQL Server
2. Create a new database:
```sql
CREATE DATABASE CrowdNest;
USE CrowdNest;
```

3. Run database setup script:
```bash
mysql -u root -p CrowdNest < database_setup.sql
```

## Environment Configuration

Create a `.env` file in the project root with the following contents:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=12345678
DB_NAME=CrowdNest
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
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape CrowdNest
- Special thanks to the open-source community for the tools and libraries used in this project 

# 🎁 CrowdNest: Collective Resource Gathering System

## 🌟 Project Overview

CrowdNest is an innovative donation management application designed to facilitate resource sharing and community support. The platform enables users to donate items, browse available donations, and connect with donors seamlessly.

## ✨ Key Features

- 👤 User Authentication
  - Secure user registration and login
  - Password hashing with salt for enhanced security

- 🎁 Donation Management
  - Create and list donations
  - Upload donation images
  - Mark donations as completed
  - View donation history

- 🔍 Donation Browsing
  - Filter donations by category, condition, and location
  - Detailed donation preview
  - Contact donor functionality

- 📊 User Dashboard
  - Track your donations
  - View donation statistics
  - Manage profile

## 🚀 Technology Stack

- **Frontend**: Tkinter (Python GUI)
- **Backend**: Python
- **Database**: MySQL
- **Authentication**: SHA-256 Hashing
- **Environment**: Python 3.8+

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- pip package manager

### Installation Steps
1. Clone the repository
```bash
git clone https://github.com/yourusername/CrowdNest.git
cd CrowdNest
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up MySQL Database
- Create a MySQL database named `CrowdNest`
- Run `init_db.sql` to create necessary tables

4. Configure Environment
- Create a `.env` file with database credentials
```
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=CrowdNest
PASSWORD_SALT=your_unique_salt
```

5. Run the Application
```bash
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact

Your Name - youremail@example.com

Project Link: [https://github.com/yourusername/CrowdNest](https://github.com/yourusername/CrowdNest)