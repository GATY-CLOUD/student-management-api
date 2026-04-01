# Student Management API

A REST API built with Flask and SQLAlchemy that manages student records 
and provides AI-powered academic insights using Ollama.

## Features
- Full CRUD operations for student records
- AI-powered career path recommendations per course
- AI-generated study tips tailored to each student's course

## Tech Stack
- Python / Flask
- SQLAlchemy (SQLite)
- Ollama (AI model integration)

## Installation

1. Clone the repository
   git clone https://github.com/yourusername/student-management-api.git
   cd student-management-api

2. Install dependencies
   pip install -r requirements.txt

3. Set up environment variables
   Create a .env file in the root directory:
   OLLAMA_HOST=your_ollama_host_url

4. Run the application
   python app.py

## API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| GET    | /students                       | Get all students             |
| GET    | /students/<id>                  | Get a single student         |
| POST   | /students                       | Create a new student         |
| PUT    | /students/<id>                  | Update a student             |
| DELETE | /students/<id>                  | Delete a student             |
| POST   | /students/<id>/career-paths     | Get AI career recommendations|
| POST   | /students/<id>/study-tips       | Get AI study tips            |

## Sample Response — Career Paths

{
  "careers": [
    {
      "job_title": "Data Scientist",
      "key_skills": ["Python", "SQL", "Machine Learning"],
      "salary_range": "$85,000 - $150,000",
      "industries": ["Technology", "Finance", "Healthcare"]
    }
  ]
}

## Author
Ezenwosu Chidera — AI Integration Specialist
GitHub: github.com/yourusername
LinkedIn: linkedin.com/in/yourprofile