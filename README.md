# **Travel API with Microservices**

## **Overview**
This project implements a Travel API using Flask, following a microservices architecture. The API consists of three services:
1. **Destination Service**: Manages travel destinations (retrieve and delete operations).
2. **User Service**: Handles user registration, login, and profile management.
3. **Authentication Service**: Provides secure authentication and role-based access control.

All services follow **OpenAPI/Swagger** standards, ensuring comprehensive API documentation.

---

## **Features**
### **Destination Service**
- Retrieve all travel destinations.
- Delete a specific destination (Admin-only).
- Each destination includes:
  - **Name**: String
  - **Description**: String
  - **Location**: String

### **User Service**
- Register new users.
- Authenticate users and provide access tokens.
- View user-specific profiles.

### **Authentication Service**
- Issue and validate authentication tokens.
- Enforce role-based access control for secure endpoints.

---

## **Requirements**
Ensure you have the following installed:
1. **Python (>= 3.9)**  
2. **Flask (>= 2.0)**  
3. **Flask-RESTful**  
4. **Flask-JWT-Extended**  
5. **Flask-Swagger-UI**  

Install dependencies using the `requirements.txt` files included in each service directory.

---

## **Setup Instructions**
### **1. Clone the repository**
Clone the repository to your local machine:
```bash
git clone https://github.com/your-repo/travel-api.git
cd travel-api
```
### **2. Install dependencies**

Set up a virtual environment and install dependencies for each service:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
Navigate to each service directory (e.g., /destination_service) and run:
```bash
pip install -r requirements.txt
```
### **3. Run services**

Each microservice runs independently. Open separate terminal windows for each service:

**Destination Service**
```bash
cd destination_service
python app.py
```
**User Service**
```bash
cd user_service
python app.py
```

**Authentication Service**
```bash
cd auth_service
python app.py
```

### **4. Access API Documentation**

Swagger UI is available for all services:

- Destination Service: http://localhost:5001
- User Service: http://localhost:5003
- Authentication Service: http://localhost:5006

## Example Requests
### Register a User

Endpoint: POST http://localhost:5003/user/register

Request Body:
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "password123",
  "role": "Admin"
}
```
### Login a User

Endpoint: POST http://localhost:5003/login
Request Body:
```json
{
  "email": "john.doe@example.com",
  "password": "password123"
}
```
### Get Destinations

Endpoint: GET http://localhost:5001/destinations

Headers
```json
{
  "Authorization": "Bearer <ACCESS_TOKEN>"
}
```
### Delete a Destination

Endpoint: DELETE http://localhost:5001/destinations/1

Headers:
```json
{
  "Authorization": "Bearer <ACCESS_TOKEN>",
  "Role": "Admin"
}
```
Request Body:
```json
{
    id: "1"
}
```



