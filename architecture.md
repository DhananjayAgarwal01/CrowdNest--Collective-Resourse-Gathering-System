# CrowdNest System Architecture

```mermaid
flowchart TB
    subgraph PL[Presentation Layer]
        UI[User Interface]
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

    subgraph BL[Business Logic Layer]
        style BL fill:#bbf,stroke:#333,stroke-width:2px
        Auth[Authentication Service]
        DonationMgmt[Donation Management]
        RequestMgmt[Request Management]
        UserMgmt[User Management]
        EmailService[Email Service]
        
        subgraph Security
            Hashing[Password Hashing]
            Session[Session Management]
            Validation[Input Validation]
        end
    end

    subgraph DL[Data Layer]
        style DL fill:#bfb,stroke:#333,stroke-width:2px
        DB[(MySQL Database)]
        subgraph Tables
            Users[(Users)]
            Donations[(Donations)]
            Requests[(Requests)]
            Sessions[(Sessions)]
        end
    end

    %% Connections
    UI --> Auth
    UI --> DonationMgmt
    UI --> RequestMgmt
    UI --> UserMgmt
    
    Auth --> Hashing
    Auth --> Session
    Auth --> DB
    
    DonationMgmt --> Validation
    DonationMgmt --> DB
    DonationMgmt --> EmailService
    
    RequestMgmt --> Validation
    RequestMgmt --> DB
    RequestMgmt --> EmailService
    
    UserMgmt --> DB
    UserMgmt --> EmailService

    %% Database Connections
    DB --> Users
    DB --> Donations
    DB --> Requests
    DB --> Sessions
```

## Layer Descriptions

### Presentation Layer
- Modern Tkinter-based GUI
- Responsive user interface components
- Intuitive navigation and forms
- Real-time status updates

### Business Logic Layer
- Authentication with SHA-256 hashing
- Session management and security
- Donation and request processing
- Email notifications via SMTP
- Input validation and sanitization

### Data Layer
- MySQL database for persistent storage
- Optimized table structures
- Secure data access
- Efficient query handling

## Key Features
- Secure user authentication
- Resource donation management
- Request processing system
- Email notifications
- Profile management
- History tracking