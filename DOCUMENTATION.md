# CrowdNest Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [Authentication System](#authentication-system)
4. [Donation Management](#donation-management)
5. [User Interface](#user-interface)
6. [API and Callback Reference](#api-and-callback-reference)
7. [Error Handling](#error-handling)
8. [Security Considerations](#security-considerations)

## Architecture Overview

### System Components
- **Frontend**: Tkinter-based GUI
- **Backend**: Python application with MySQL database
- **Authentication**: Custom implementation with SHA-256 hashing

### Module Structure
- `app.py`: Main application entry point
- `src/database_handler.py`: Database interaction layer
- `src/pages/`: Individual page implementations
- `src/ui/`: UI component and styling modules

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    unique_id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Donations Table
```sql
CREATE TABLE donations (
    unique_id VARCHAR(36) PRIMARY KEY,
    donor_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    `condition` VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    status ENUM('available', 'reserved', 'completed') DEFAULT 'available',
    image_path LONGBLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(unique_id)
);
```

## Authentication System

### Password Security
- Passwords are hashed using SHA-256
- A unique salt is added to each password
- Salt is stored in environment variables
- Prevents rainbow table and dictionary attacks

### Authentication Flow
1. User enters credentials
2. Password is hashed with salt
3. Credentials verified against database
4. Session token generated on successful login

## Donation Management

### Donation Lifecycle
1. **Creation**: Donor provides donation details
2. **Listing**: Donation appears in browse page
3. **Contact**: Users can contact donor
4. **Marking Complete**: Donor can mark donation as completed

### Key Methods
- `create_donation()`: Add new donation
- `get_donations()`: Retrieve donation list
- `mark_donation_as_donated()`: Update donation status
- `get_user_donation_history()`: Retrieve completed donations

## User Interface

### Pages
- Login Page
- Registration Page
- Dashboard
- Donation Form
- Donation List
- Donation Details
- Profile Page
- Donation History

### UI Components
- Modern, flat design
- Tkinter with custom styling
- Responsive layouts
- Error message popups
- Confirmation dialogs

## API and Callback Reference

### Database Callbacks
- `login_callback(email, password)`
- `register_callback(full_name, email, password)`
- `create_donation_callback(donation_details)`
- `contact_donor_callback(donation_id)`
- `mark_as_donated_callback(donation_id)`

### Navigation Callbacks
- `show_frame(frame_name)`
- `logout()`

## Error Handling

### Error Types
- Authentication Errors
- Database Connection Errors
- Validation Errors
- Permission Errors

### Error Handling Strategy
- Descriptive error messages
- Logging critical errors
- Graceful error recovery
- User-friendly notifications

## Security Considerations

### Input Validation
- Email format validation
- Password strength requirements
- SQL injection prevention
- XSS protection

### Data Protection
- Minimal personal information storage
- Encrypted password storage
- HTTPS recommended for future web version
- Regular security audits

## Performance Optimization

### Database
- Indexed columns
- Efficient query design
- Connection pooling

### UI
- Lazy loading of resources
- Efficient event handling
- Minimal blocking operations

## Future Roadmap
- Web application version
- Advanced donation matching
- Social sharing features
- Enhanced user profiles

## Troubleshooting

### Common Issues
1. Database Connection Failures
   - Check `.env` configuration
   - Verify MySQL service is running
   - Confirm network accessibility

2. Authentication Problems
   - Reset password functionality
   - Verify email format
   - Check for caps lock

## Contributing Guidelines

### Code Style
- PEP 8 Python guidelines
- Type hinting
- Comprehensive docstrings
- 80-character line limit

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Commit with descriptive messages
4. Write/update tests
5. Pass all CI checks
6. Request review

## License
MIT License - See LICENSE file for details
