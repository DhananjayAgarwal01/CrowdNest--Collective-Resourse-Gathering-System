
CREATE DATABASE IF NOT EXISTS CrowdNest;
USE CrowdNest;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    unique_id VARCHAR(36) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    location VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS donations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    unique_id VARCHAR(36) UNIQUE NOT NULL,
    donor_id VARCHAR(36) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    `condition` VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'available',
    image_data MEDIUMBLOB,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(unique_id)
);

CREATE TABLE IF NOT EXISTS requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    unique_id VARCHAR(36) UNIQUE NOT NULL,
    requester_id VARCHAR(36) NOT NULL,
    donation_id VARCHAR(36) NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_id) REFERENCES users(unique_id),
    FOREIGN KEY (donation_id) REFERENCES donations(unique_id)
);

CREATE TABLE IF NOT EXISTS deliveries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    unique_id VARCHAR(36) UNIQUE NOT NULL,
    donation_id VARCHAR(36) NOT NULL,
    requester_id VARCHAR(36) NOT NULL,
    tracking_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    estimated_date DATE,
    actual_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES donations(unique_id),
    FOREIGN KEY (requester_id) REFERENCES users(unique_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    unique_id VARCHAR(36) UNIQUE NOT NULL,
    sender_id VARCHAR(36) NOT NULL,
    receiver_id VARCHAR(36) NOT NULL,
    donation_id VARCHAR(36),
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(unique_id),
    FOREIGN KEY (receiver_id) REFERENCES users(unique_id),
    FOREIGN KEY (donation_id) REFERENCES donations(unique_id)
);
