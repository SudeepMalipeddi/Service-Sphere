# Household Services App - Service Sphere

This is a simple web application for a multi-user app (requires one admin and other service professionals/ customers) which acts as platform for providing comprehensive home servicing and solutions.

## Overview

Service Sphere is a multi-user application that facilitates household service bookings. The platform supports three user roles:

- **Customers** can browse services, book appointments, and review professionals
- **Service Professionals** can offer services, manage requests, and build their reputation
- **Administrators** oversee the platform, verify professionals, and manage services

## Features

- User authentication with role-based access control
- Service browsing and booking system
- Professional verification workflow
- Real-time notifications
- Review and rating system
- Admin dashboard with analytics
- Request management for all user types

## Technical Stack

### Backend

- Python 3.8+
- Flask (RESTful API)
- SQLAlchemy ORM
- JWT Authentication
- Celery for background tasks
- Redis for caching and message broker

### Frontend

- Vue.js 3
- Pinia for state management
- Bootstrap 5 for UI components
- Chart.js for analytics

## Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- Redis server
- Modern web browser

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/service-sphere.git
cd service-sphere
```

### 2. Backend Setup

Create and activate a virtual environment:

```bash

python3 -m venv venv
source venv/bin/activate  # On Windows :venv\Scripts\activate

```

Install dependencies:

```bash

pip install -r requirements.txt
```

Start the Flask server:

```bash
python app.py
```

### 3. Frontend Setup

Install npm packages:

```bash

cd frontend
npm install
npm run dev
```

### 4. Start Redis server

```bash
redis-server
```

### 5. Start Celery worker and beat (for background tasks and scheduling)

In a new terminal, activate the virtual environment again and run in two separate terminals:

```bash
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info
```

### 6. Start MailHog (for email testing in development)

```bash
~/go/bin/MailHog
```

Accessing the Application
Once all components are running:

Frontend: http://localhost:5173/
Backend API: http://localhost:5000/api
MailHog: http://localhost:8025/

### Default Admin Login

Email: admin@example.com
Password: admin123
