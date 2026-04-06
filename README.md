# Secure FastAPI Calculator & Authentication API

## Project Overview
This project is a fully containerized, secure FastAPI application featuring a calculator interface and a robust user authentication system. It leverages PostgreSQL for data persistence, SQLAlchemy for ORM, and JWT (JSON Web Tokens) for secure route protection. 

The repository includes a comprehensive automated CI/CD pipeline using GitHub Actions, strictly enforcing 10/10 Pylint code quality, 100% Pytest test coverage, End-to-End (E2E) testing via Playwright, and automated Trivy vulnerability scanning prior to Docker Hub deployment.

## Features
* **FastAPI Backend:** High-performance async API routing and validation using Pydantic.
* **JWT Authentication:** Secure user registration, login, and password hashing (bcrypt).
* **End-to-End Testing:** Automated UI interactions and assertions using Playwright.
* **Continuous Integration:** GitHub Actions pipeline for automated testing and linting.
* **Continuous Deployment:** Automated Docker image builds pushed to Docker Hub upon passing security scans.
* **Containerized Database:** PostgreSQL database managed via Docker Compose.

---

## Local Environment Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/reyesfrancisp/secure-user-model.git](https://github.com/reyesfrancisp/secure-user-model.git)
cd secure-user-model
```

### 2. Environment Variables
Create a `.env` file in the root directory. This is required for the application and database to run properly.

```env
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/mytestdb
SECRET_KEY=your-super-secret-local-key-change-in-production
```

### 3. Start the Docker Containers
The application relies on a PostgreSQL database container. Start it using Docker Compose:

```bash
docker compose up -d
```

---

## Running the Application Locally

### 1. Set Up the Virtual Environment
Ensure you have Python 3.10+ installed.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install Playwright Browsers (Required for E2E Tests)
```bash
playwright install --with-deps
```

### 4. Run the FastAPI Server
```bash
uvicorn main:app --reload
```
* **The API will be available at:** `http://127.0.0.1:8000`
* **Interactive API Docs (Swagger UI) available at:** `http://127.0.0.1:8000/docs`

---

## Testing & Quality Assurance
This project maintains a strict 100% test coverage standard across Unit, Integration, and End-to-End tests.

**Run the full test suite with coverage report:**
```bash
pytest --cov=app --cov-report=term-missing
```

**Run Code Quality Checks (Pylint):**
```bash
pylint app tests
```

---

## CI/CD Pipeline Architecture
This repository utilizes GitHub Actions for continuous integration and deployment. The pipeline is triggered on every push and pull request to the `main` branch.

* **Test Phase:** * Provisions an Ubuntu runner with a PostgreSQL service.
  * Installs Python dependencies and Playwright Chromium binaries.
  * Executes Pytest suite and enforces coverage metrics.
* **Security Phase:** * Builds the Docker image.
  * Scans the image using AquaSecurity Trivy to block critical CVEs from reaching production.
* **Deploy Phase:** * Authenticates with Docker Hub using securely stored repository secrets.
  * Pushes the verified `latest` and SHA-tagged images to the public registry.

**Docker Hub Repository:** [https://hub.docker.com/repository/docker/reyesfrancisp/secure-user-model/general](https://hub.docker.com/repository/docker/reyesfrancisp/secure-user-model/general)