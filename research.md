## I. Introduction

*   **Problem Statement:**  Traditional donation methods often lack transparency, accessibility, and efficiency, hindering effective resource allocation to those in need. Statistics on inefficiencies in local charity resource distribution will be included.
*   **Proposed Solution:**  DonateShare, a web application developed using Python, Flask, MySQL, and Tkinter, addresses these limitations by providing a platform for direct connection between donors and recipients.
*   **Contributions:** This paper presents the design and implementation of DonateShare, specifically contributing: (1) A RESTful API using Flask for user authentication, donation management, and communication. (2) A MySQL database schema for persistent data storage and relationship management. (3) A Tkinter-based GUI (Graphical User Interface) enabling user interaction with the platform.  (4) Security analysis of the implemented JWT authentication mechanism.
*   **Organization:** This paper is organized as follows: Section II discusses related work. Section III details the system architecture and design. Section IV describes the implementation. Section V analyzes security. Section VI evaluates performance and usability. Finally, Section VII concludes the paper and outlines future work.

## II. Related Work

*   **Existing Donation Platforms:**  Analyze existing online donation platforms such as GoFundMe and local charity websites.  Focus on their architectural patterns (e.g., monolithic vs. microservices), technologies used (e.g., PHP, Node.js, relational databases), and security features (e.g., OAuth, two-factor authentication). Cite relevant academic papers and technical reports.
*   **Flask Web Framework:** Discuss the Flask web framework and its suitability for building RESTful APIs. Cite key publications and documentation on Flask, including extensions for database integration and security.
*   **MySQL Database:**  Describe the MySQL database system and its features for data management. Include relevant academic work comparing MySQL with other relational database systems.
*   **JWT Authentication:**  Analyze JWT authentication mechanisms, focusing on their advantages and disadvantages in web application security. Cite research papers on JWT vulnerabilities and best practices.

## III. System Architecture and Design

*   **Overall Architecture:** Describe the DonateShare system architecture, including a block diagram illustrating the interaction between the Tkinter frontend, Flask API, and MySQL database.  Show how the client requests are handled by the Flask backend and how the database interacts with the backend.
*   **A. Backend (Flask API - flask\_routes.py)**
    *   **API Endpoints:** Detail key API endpoints such as `/api/register`, `/api/login`, `/api/donations` (GET, POST), `/api/requests` (POST), `/api/messages` (GET, POST), and `/api/profile` (PUT). Provide a table summarizing the endpoints, HTTP methods, required parameters, and response formats.
    *   **Authentication (JWT):** Explain the JWT authentication mechanism.  Specifically:  The `token_required` decorator, token generation upon successful login (using `jwt.encode`), token verification on protected routes (using `jwt.decode`), and the inclusion of `user_id` within the token payload.  The expiration time (24 hours) should also be mentioned. Provide code snippets from `flask_routes.py` to illustrate token generation and verification.
    *   **Data Validation:** Describe the data validation performed on the Flask routes. For example, input validation during registration (username length, password length, email format), donation creation (required fields, title/description lengths), etc. Refer to specific code sections in `flask_routes.py` for each endpoint.
*   **B. Database (MySQL - db\_init.py, database\_handler.py)**
    *   **Schema Design:** Present the database schema using an ER diagram. Define the tables (`users`, `donations`, `requests`, `messages`) and their relationships.  Highlight the use of `unique_id` (VARCHAR(36)) as the primary key for all tables, the `FOREIGN KEY` constraints linking related tables, and the `TIMESTAMP` columns for tracking creation times.
    *   **Data Access Layer:** Explain the role of the `DatabaseHandler` class in `database_handler.py`. Describe how it manages database connections (using `mysql.connector.connect(**DB_CONFIG)`), executes queries, and provides methods for data manipulation (e.g., `create_user`, `create_donation`, `get_donations`).
*   **C. Frontend (Tkinter - tkinter\_app.py)**
    *   **User Interface:** Describe the key UI elements and their functionality. Include screenshots of the Tkinter GUI. Explain how the UI integrates with the Flask API. Detail the processes for user registration, donation posting, request creation, and messaging. Describe the overall UI using the modern color scheme defined in the provided code.

## IV. Implementation Details

*   **Backend Implementation:**
    *   **Code Snippets:** Provide code snippets from `flask_routes.py` to illustrate key functionalities.  Focus on:
        *   User registration: Hashing passwords using `hashlib.sha256` within the `DatabaseHandler`.
        *   Donation creation: Retrieving `current_user` from the decoded JWT token.
        *   Data validation: How data validation is done and errors are handled.
    *   **Error Handling:** Explain the error handling within the Flask API. Illustrate how exceptions are caught (using `try...except` blocks), logged (using `print(f"Error...: {str(e)}")`), and returned to the client as JSON responses with appropriate HTTP status codes.
*   **Database Interaction:**
    *   **SQL Queries:** Show example SQL queries used in `database_handler.py` to interact with the database.
    *   **Data Integrity:** Discuss how data integrity is maintained through database constraints (e.g., `UNIQUE` constraints on `username` and `email` in the `users` table, `FOREIGN KEY` constraints).
*   **Frontend Implementation:**
    *   **API Calls:** Show examples of how the Tkinter frontend makes API calls to the Flask backend using the `requests` library. Illustrate how data is serialized into JSON format and sent in the request body, and how the responses are processed.

## V. Security Analysis

*   **A. Authentication Vulnerabilities:** Analyze potential vulnerabilities in the JWT authentication system, such as:
    *   **Secret Key Management:** Highlight the risk of hardcoding the `SECRET_KEY` in the code (currently set to `'123456shfowef13'`). Recommend storing the secret key in an environment variable and using a strong, randomly generated key.
    *   **Token Hijacking:** Discuss the potential for token hijacking attacks and the importance of using HTTPS to protect tokens in transit.
    *   **Brute-Force Attacks:** Explain the possibility of brute-force attacks to guess the secret key and recommend implementing rate limiting and account lockout mechanisms.
*   **B. Data Validation Vulnerabilities:** Analyze potential vulnerabilities related to data validation:
    *   **SQL Injection:**  While the code uses parameterized queries, emphasize the importance of *always* using parameterized queries and *never* concatenating user input directly into SQL queries to prevent SQL injection attacks.
    *   **Cross-Site Scripting (XSS):** Discuss the potential for XSS vulnerabilities if user-provided data is not properly sanitized before being displayed in the Tkinter GUI.  Recommend using appropriate encoding and escaping techniques.
*   **C. Database Security:** Analyze the security of the database:
    *   **Password Hashing:** While passwords are being hashed using `hashlib.sha256`, recommend using a stronger hashing algorithm such as bcrypt or Argon2, which are specifically designed for password hashing and include salting to prevent rainbow table attacks.
    *   **Access Control:** Discuss the importance of restricting database access to only authorized users and applications.
*   **D. Recommendations:** Provide specific recommendations for improving the security of DonateShare, including:
    *   Storing the secret key in an environment variable.
    *   Using HTTPS to protect tokens in transit.
    *   Implementing rate limiting and account lockout mechanisms.
    *   Using a stronger password hashing algorithm (bcrypt or Argon2).
    *   Sanitizing user input to prevent XSS vulnerabilities.
    *   Regularly updating dependencies to patch security vulnerabilities.

## VI. Evaluation and Results

*   **A. Usability Evaluation:** *Note: the file `tkinter_app.py` was provided but not reviewed, this section would need to be completed based on the code in that file*
    *   **Methodology:** Describe the methodology used to evaluate the usability of the Tkinter GUI.  Consider including user surveys, task completion time measurements, and error rate analysis.
    *   **Results:** Present the results of the usability evaluation. Include screenshots highlighting key aspects of the UI and data on usability metrics.
*   **B. Performance Evaluation:**
    *   **Methodology:** Describe the methodology used to evaluate the performance of the Flask API. This should include load testing using tools like Locust or ApacheBench to measure response time, throughput, and resource utilization under different load conditions.
    *   **Results:** Present the performance results in graphs and tables. Analyze the performance bottlenecks and suggest potential optimizations (e.g., database indexing, caching).
*   **C. Comparison with Existing Platforms:** Compare DonateShare with existing online donation platforms, focusing on:
    *   **Functionality:** Highlight the features that DonateShare offers compared to existing platforms.
    *   **Performance:** Compare the performance of DonateShare with other platforms, if available.
    *   **Security:** Contrast the security measures implemented in DonateShare with those used by other platforms.

## VII. Conclusion

*   **Summary of Contributions:** Briefly summarize the key contributions of the paper.
*   **Limitations:** Acknowledge any limitations of the research or the DonateShare platform.  For example: the lack of a robust image handling mechanism, limited scalability, and the basic security measures implemented.
*   **Future Work:** Suggest directions for future research and development, such as:
    *   Implementing a more robust image handling mechanism with image resizing and validation.
    *   Improving the scalability of the platform using techniques such as load balancing and caching.
    *   Implementing more advanced security features, such as multi-factor authentication and intrusion detection.
    *   Adding support for different payment gateways to facilitate online donations.
    *   Developing a mobile app version of the platform.