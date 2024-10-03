# User_Auth
This project is a Flask-based API for managing user authentication and organization data. It implements JWT-based authentication, PostgreSQL for database management, and provides routes for user and organization operations.



## Requirements

- Python 3.8+
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-JWT-Extended

## Installation

1. Clone the repository:
   git clone https://github.com/Nne85/User_Auth.git
   cd User_Auth

# User Authentication and Organization Management API

This project is a Flask-based API for managing user authentication and organization data. It implements JWT-based authentication, PostgreSQL for database management, and provides routes for user and organization operations.


## Features

- User registration and login with JWT authentication.
- Relationship management between users and organizations.
- Protected routes accessible only to authenticated users.
- Support for multiple organizations per user and role-based access.

## Virtual Environment
python3 -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`

### Install the required dependencies:
pip install -r requirements.txt

### Run app
flask run

