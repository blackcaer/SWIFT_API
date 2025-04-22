# SWIFT Codes Management API

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Coverage](https://img.shields.io/badge/Coverage-86%25-brightgreen?style=for-the-badge)

A REST API for managing bank SWIFT/BIC (Bank Identifier Code) codes with comprehensive data processing, storage, and retrieval capabilities. The system processes SWIFT codes from Excel file, maintains headquarters-branch relationships, and provides fast, low-latency access through RESTful endpoints.

## 🎯 Key Features

### 1. SWIFT Data Processing
- Excel file parsing with sophisticated data handling:
  - Automatic HQ detection (codes ending with "XXX")
  - Branch-HQ relationship mapping (first 8 characters matching)
  - Data standardization (uppercase country names and codes)
  - Redundant column filtering
  - Strict 11-character SWIFT code validation

### 2. Data Storage
- PostgreSQL database implementation for:
  - Fast, low-latency querying
  - Efficient data retrieval by SWIFT code and country
  - Robust relationship management between HQs and branches
  - Data integrity enforcement

### 3. REST API Endpoints
- **GET /v1/swift-codes/{swift-code}**
  - Retrieve detailed information for any SWIFT code
  - Different response structures for HQ (includes branches) and branch codes
  
- **GET /v1/swift-codes/country/{countryISO2code}**
  - Get all SWIFT codes for a specific country
  - Returns both HQs and branches with complete details
  
- **POST /v1/swift-codes**
  - Add new SWIFT code entries
  - Validates HQ-branch relationships
  - Ensures data integrity
  
- **DELETE /v1/swift-codes/{swift-code}**
  - Remove SWIFT codes from the database
  - Proper error handling for non-existent codes

## 💻 Setup and Running

### Prerequisites
- Docker and Docker Compose installed
- Git for cloning the repository

### Installation Steps
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd SWIFT_API/
   ```

2. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

3. Load initial SWIFT codes data:
   ```bash
   docker-compose exec web python /app/app/scripts/load_swift_codes.py
   ```
   - Default source: `data/Interns_2025_SWIFT_CODES.xlsx`
   - Optional: Use --file argument for custom source

### Testing
1. Run the test suite:
   ```bash
   docker-compose exec web pytest /app/tests/
   ```

2. Check test coverage:
   ```bash
   docker-compose exec web pytest --cov=/app/app /app/tests/
   ```

### API Documentation
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Container Management
- Stop containers: `docker-compose stop`
- Start containers: `docker-compose start`
- Remove containers and volumes: `docker-compose down -v`

## 🔍 Implementation Details

Some of the implementation details were not explicitly specified, so I listed my assumption here:

### Data Validation and Processing

  - Only **11-character codes** are accepted. Although SWIFT codes could technically be 8-character (hq without XXX) the project does not support this, because source data has only 11-character codes. 
  - POST endpoint recives request with **isHeadquarter** provided. This value could be deducted from SWIFT code, but specification stated that it has to be there. That value is only used to return 422 when it doesnt match the SWIFT code. 

  - Do not allow adding branch without existing HQ. This wasn't stated in specification, but adding bank without it's HQ has no sense.
  
  - **Address** field can be empty (as in source data)


## Testing
- Comprehensive unit tests
- Integration tests for all endpoints
- Edge case coverage
- Current test coverage: 86%
