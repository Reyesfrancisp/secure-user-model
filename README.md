# Secure User Model API

This project implements a secure user model using FastAPI, SQLAlchemy, and Pydantic, complete with password hashing and automated CI/CD via GitHub Actions.

## How to Run Tests Locally
1. Ensure you have Docker installed and running.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt