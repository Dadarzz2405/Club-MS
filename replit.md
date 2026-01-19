# Rohis Attendance System

## Overview
This is a Flask-based attendance management system for Rohis (Islamic student organization). It provides user authentication, session management, attendance tracking, and an Islamic calendar feature.

## Tech Stack
- **Backend**: Python 3.11, Flask
- **Database**: SQLite (database.db)
- **Authentication**: Flask-Login, Flask-Bcrypt
- **ORM**: Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **AI Integration**: Groq API for chatbot
- **Export**: python-docx for document generation
- **Islamic Calendar**: ummalqura for Hijri date conversion

## Project Structure
```
├── app.py              # Main Flask application with routes
├── models.py           # SQLAlchemy models (User, Session, Attendance, Pic)
├── ai.py               # Groq chatbot integration
├── formatter.py        # Attendance formatting utilities
├── utils.py            # Helper functions
├── seeder.py           # Database seeding script
├── database.db         # SQLite database
├── templates/          # Jinja2 HTML templates
├── static/             # Static files (JS, CSS, uploads)
│   ├── attendance.js
│   ├── chat.js
│   └── uploads/profiles/  # User profile pictures
├── migrations/         # Alembic database migrations
└── requirements.txt    # Python dependencies
```

## Key Features
- User authentication with roles (admin, ketua, pembina, member)
- Attendance marking and tracking
- Session management with PIC (Person in Charge) assignment
- Islamic holiday calendar integration
- AI chatbot powered by Groq
- Attendance export to DOCX format

## Running the Application
The application runs on port 5000:
```bash
python app.py
```

For production:
```bash
gunicorn --bind=0.0.0.0:5000 app:app
```

## Environment Variables
- `GROQ_API_KEY`: Required for the AI chatbot feature

## Database
Uses SQLite with Flask-Migrate for schema migrations. The database file is `database.db` in the project root.

## Recent Changes
- 2026-01-19: Initial setup on Replit environment
