# CrowdNest System Architecture

## System Block Diagram (Text Version)

```
+-------------------+
|    Frontend UI    |
|   (Tkinter)   |
+--------+----------+
         |
         v
+--------+----------+
|   Application     |
|    Controller     |
+--------+----------+
         |
         v
+--------+----------+
|   Service Layer   |
| - User Management |
| - Donation Mgmt   |
| - Request Handling|
+--------+----------+
         |
         v
+--------+----------+
|  Database Layer   |
| - MySQL Database  |
| - Tables:         |
|   * users         |
|   * donations     |
|   * donation_req  |
+-------------------+
```

```mermaid
flowchart TB
    subgraph FL[Frontend Layer]
        UI[Tkinter/Web Interface]
        style UI fill:#f9f,stroke:#333,stroke-width:2px
        subgraph UI_Components
            Login[Login Screen]
            Register[Registration]
            Dashboard[Dashboard]
            DonationForm[Donation Form]
            RequestForm[Request Form]
            Profile[User Profile]
        end
    end

    subgraph CL[Controller Layer]
        style CL fill:#ffd,stroke:#333,stroke-width:2px
        AppController[Application Controller]
        Router[Request Router]
        StateManager[State Management]
    end

    subgraph SL[Service Layer]
        style SL fill:#bbf,stroke:#333,stroke-width:2px
        UserService[User Management]
        DonationService[Donation Management]
        RequestService[Request Handling]
        AuthService[Authentication]
        ValidationService[Validation Service]
    end

    subgraph DL[Database Layer]
        style DL fill:#bfb,stroke:#333,stroke-width:2px
        DB[(MySQL Database)]
        subgraph Tables
            Users[(users)]
            Donations[(donations)]
            DonationReq[(donation_req)]
        end
    end

    %% Connections
    UI --> AppController
    AppController --> Router
    Router --> StateManager
    
    Router --> UserService
    Router --> DonationService
    Router --> RequestService
    Router --> AuthService
    
    UserService --> ValidationService
    DonationService --> ValidationService
    RequestService --> ValidationService
    
    UserService --> DB
    DonationService --> DB
    RequestService --> DB
    AuthService --> DB

    %% Database Connections
    DB --> Users
    DB --> Donations
    DB --> DonationReq
```

## Layer Descriptions

### Frontend Layer (Tkinter/Web)
- Modern Tkinter-based GUI interface
- Responsive and intuitive user components
- Form handling and validation
- Real-time status updates
- Event handling and user interactions

### Application Controller Layer
- Central request routing and handling
- State management and data flow control
- Component coordination
- Error handling and logging
- Session management

### Service Layer
- User Management Service
  * User registration and authentication
  * Profile management
  * Access control
- Donation Management Service
  * Donation processing
  * Resource allocation
  * Status tracking
- Request Handling Service
  * Request validation
  * Request processing
  * Notification handling

### Database Layer
- MySQL database for persistent storage
- Core tables:
  * users: User information and credentials
  * donations: Donation records and status
  * donation_req: Request tracking and management
- Optimized query handling
- Data integrity and security

## Key Features
- Clean separation of concerns across layers
- Centralized request handling through controller
- Modular service architecture
- Secure data management
- Scalable component structure