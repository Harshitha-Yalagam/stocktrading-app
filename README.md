#  Stock Trading Web Application

A full-stack stock trading simulation platform built with Flask and SQLite, where users can register, log in, simulate stock trades using real-time data via Alpha Vantage API, and manage their virtual portfolio. Designed as a learning project to practice web development, API integration, and database management.

---

##  Features

-  User authentication and session management
-  Fake cash system (starts with $10,000)
-  Real-time stock prices using Alpha Vantage API
-  Simulated buying/selling of stocks
-  Portfolio tracking with current market value
-  Transaction history
-  Password hashing using Werkzeug for security

##  Tech Stack
###  Frontend
- HTML / CSS

###  Backend
- Flask (Python)
- Flask-Session
- Werkzeug (for password hashing)
- requests (for API calls)

###  Database
- SQLite
- cs50 SQL library (for easier queries)

###  APIs
- Alpha Vantage (for live stock prices)

