# 🕌 Rohis Management System

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A comprehensive web-based application designed to digitize and streamline the management of **Rohis (Rohani Islam)** activities in schools. This system helps administrators efficiently manage member data, track attendance, create meeting minutes, and organize Islamic events.

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [Acknowledgments](#-acknowledgments)

## ✨ Features

### Core Features
- 🔐 **Secure Authentication System** - Role-based access control (Admin, Ketua, Pembina, Member)
- 👥 **Member Management** - Comprehensive member database with profiles and role assignments
- 📊 **Attendance Tracking** - Digital attendance recording with multiple status options (Present, Absent, Excused, Late)
- 📝 **Meeting Minutes (Notulensi)** - Rich text editor for creating and managing meeting documentation
- 📅 **Islamic Calendar Integration** - Automatic display of Islamic holidays with Hijri date conversion
- 🤖 **AI-Powered Chatbot** - Islamic educational assistant using Groq API
- 📈 **Analytics Dashboard** - Real-time statistics and attendance reports
- 📱 **Responsive Design** - Mobile-friendly interface with modern UI/UX

### Advanced Features
- **PIC (Person In Charge) Management** - Assign and manage event coordinators
- **Core Team Attendance** - Separate attendance tracking for leadership team
- **Session Management** - Create and lock attendance sessions
- **Document Export** - Export attendance reports to DOCX format
- **News Feed** - Display upcoming events and recent meeting summaries
- **Profile Customization** - Upload profile pictures and manage personal information
- **Password Management** - Secure password change with forced reset on first login

## 🎯 Demo

> **Note:** This is a school project and personal portfolio demonstration. The system is optimized for small-scale Rohis organizations.

### Default Credentials
```
Email: [Contact administrator]
Password: rohis2026 (Must be changed on first login)
```

## 🛠️ Technology Stack

### Backend
- **Framework:** Flask 3.1.2
- **Database:** 
  - Development: SQLite
  - Production: PostgreSQL (via psycopg2-binary)
- **ORM:** SQLAlchemy 2.0.45
- **Authentication:** Flask-Login 0.6.3
- **Password Hashing:** Flask-Bcrypt 1.0.1
- **Database Migrations:** Flask-Migrate 4.0.4 / Alembic 1.11.1

### Frontend
- **Framework:** Bootstrap 5.3.0
- **Icons:** Font Awesome 6.4.0, Bootstrap Icons
- **Fonts:** Google Fonts (Inter)
- **Calendar:** FullCalendar 6.1.11
- **Rich Text Editor:** Quill.js 1.3.6
- **Animations:** Animate.css, WOW.js

### AI & APIs
- **AI Provider:** Groq (llama-3.1-8b-instant)
- **Features:** 
  - Islamic educational chatbot
  - Meeting minutes summarization
  - Attendance report formatting

### Additional Libraries
- **Hijri Calendar:** ummalqura
- **Document Processing:** python-docx
- **HTTP Requests:** requests 2.32.5
- **Environment Management:** python-dotenv 1.2.1
- **WSGI Server:** gunicorn 21.2.0

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git
- Virtual environment tool (venv)

### Step-by-Step Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rohis-management-system.git
cd rohis-management-system
```

2. **Create and activate virtual environment**
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```bash
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/database.db
GROQ_API_KEY=your-groq-api-key

# Optional (for production)
PORT=5000
FLASK_ENV=development
```

To generate a secure secret key:
```python
import secrets
print(secrets.token_hex(32))
```

5. **Initialize the database**
```bash
flask db upgrade
```

6. **Seed the database with initial data**
```bash
python seeder.py seed
```

7. **Run the application**
```bash
# Development
python app.py

# Production with Gunicorn
gunicorn --bind=0.0.0.0:5000 app:app
```

8. **Access the application**
```
http://localhost:5000
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `DATABASE_URL` | Database connection string | Yes | `sqlite:///instance/database.db` |
| `GROQ_API_KEY` | Groq API key for AI features | Yes | - |
| `PORT` | Application port | No | `5000` |
| `FLASK_ENV` | Environment (development/production) | No | `development` |

### Database Configuration

**Development (SQLite):**
```python
DATABASE_URL=sqlite:///instance/database.db
```

**Production (PostgreSQL):**
```python
DATABASE_URL=postgresql://user:password@host:port/database
```

### Groq API Setup

1. Sign up at [Groq Console](https://console.groq.com/)
2. Create an API key
3. Add to `.env` file:
```
GROQ_API_KEY=gsk_your_api_key_here
```

## 📖 Usage

### For Administrators

1. **Creating Sessions**
   - Navigate to Dashboard → Create Session
   - Enter session name and date
   - Optionally assign a PIC

2. **Managing Attendance**
   - Go to Mark Attendance
   - Select a session
   - Mark attendance for each member (Present/Absent/Excused/Late)
   - One-click save per member

3. **Creating Meeting Minutes**
   - Access Meeting Minutes → Create New
   - Select session
   - Use rich text editor to document meeting
   - Auto-save feature prevents data loss

4. **Managing PICs**
   - Navigate to Member Management
   - Assign members to PICs
   - Grant attendance marking permissions

### For Members

1. **View Attendance History**
   - Dashboard → My Attendance History
   - See all session attendance records
   - View summary statistics

2. **Read Meeting Minutes**
   - Dashboard → View Meeting Minutes
   - Browse all session notes
   - AI-generated summaries for quick reading

3. **View Calendar**
   - Check upcoming Rohis sessions
   - See Islamic holidays with Hijri dates

### Using the AI Chatbot

Click the chat bubble in the bottom-right corner to:
- Ask about Islamic topics
- Get help navigating the system
- Request information about features

Example queries:
- "Take me to attendance"
- "What is the importance of salah?"
- "Show me the dashboard"

## 📁 Project Structure

```
rohis-management-system/
├── app.py                      # Main application file
├── models.py                   # Database models
├── utils.py                    # Utility functions
├── ai.py                       # AI chatbot logic
├── formatter.py                # Attendance formatting
├── summarizer.py               # Meeting minutes summarization
├── seeder.py                   # Database seeder
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── Procfile                    # Heroku deployment config
├── .replit                     # Replit configuration
│
├── migrations/                 # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Migration environment
│
├── instance/                   # Instance-specific files
│   └── database.db            # SQLite database (dev)
│
├── static/                     # Static assets
│   ├── style.css              # Main stylesheet
│   ├── chat.css               # Chatbot styles
│   ├── login.css              # Login page styles
│   ├── attendance.js          # Attendance logic
│   ├── chat.js                # Chatbot logic
│   ├── images/                # Image assets
│   └── uploads/               # User uploads
│       └── profiles/          # Profile pictures
│
└── templates/                  # HTML templates
    ├── base.html              # Base template
    ├── login.html             # Login page
    ├── dashboard_admin.html   # Admin dashboard
    ├── dashboard_member.html  # Member dashboard
    ├── attendance.html        # Attendance marking
    ├── notulensi.html         # Meeting minutes editor
    ├── calendar.html          # Calendar view
    ├── member_list.html       # Member directory
    └── ...                    # Other templates
```

## 🔌 API Endpoints

### Attendance
```
POST   /api/attendance              # Mark regular attendance
POST   /api/attendance/core         # Mark core team attendance
POST   /api/session/<id>/lock       # Lock a session
```

### Meeting Minutes
```
POST   /api/notulensi/<session_id> # Save/update notulensi
DELETE /api/notulensi/<id>          # Delete notulensi
```

### Calendar & News
```
GET    /api/dashboard_calendar      # Get calendar events
GET    /api/news-feed               # Get news feed data
```

### Chatbot
```
POST   /chat                        # Send message to AI chatbot
```

### Export
```
GET    /export/attendance/<id>      # Export attendance as DOCX
```

## 🗄️ Database Schema

### Users
- `id`: Primary key
- `email`: Unique school email
- `password`: Bcrypt hashed password
- `name`: Full name
- `role`: admin | ketua | pembina | member
- `class_name`: Student class
- `profile_picture`: Profile image filename
- `pic_id`: Foreign key to PIC
- `can_mark_attendance`: Permission flag
- `must_change_password`: Force password reset

### Sessions
- `id`: Primary key
- `name`: Session name
- `date`: Session date
- `pic_id`: Assigned PIC
- `is_locked`: Lock status

### Attendance
- `id`: Primary key
- `session_id`: Foreign key to Session
- `user_id`: Foreign key to User
- `status`: present | absent | excused | late
- `attendance_type`: regular | core
- `timestamp`: Record timestamp

### Notulensi
- `id`: Primary key
- `session_id`: Foreign key to Session
- `content`: HTML content
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### PIC (Person In Charge)
- `id`: Primary key
- `name`: PIC name

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write docstrings for functions

## 🗺️ Roadmap

### Phase 1 (Completed)
- ✅ Core authentication system
- ✅ Attendance tracking
- ✅ Meeting minutes
- ✅ AI chatbot integration
- ✅ Calendar with Islamic dates

### Phase 2 (In Progress)
- 🔄 Excel/PDF export for analytics
- 🔄 Advanced statistics and charts
- 🔄 Email notifications
- 🔄 Mobile responsive improvements

### Phase 3 (Planned)
- 📋 Multi-language support (Indonesian/English)
- 📋 Role-based permission system expansion
- 📋 Integration with school systems
- 📋 Mobile application (React Native)
- 📋 Advanced reporting dashboard
- 📋 Automated attendance reminders

## ⚠️ Important Notes

### Limitations
- **Scale:** Designed for small-scale organizations (up to 100 members)
- **Performance:** Not optimized for large-scale deployments
- **Security:** Basic authentication - consider additional security measures for production
- **Browser Support:** Modern browsers only (Chrome, Firefox, Safari, Edge)

### Known Issues
- AI chatbot requires stable internet connection
- Profile picture upload limited to 5MB
- Calendar may not display correctly in older browsers

## 🙏 Acknowledgments

- **Groq** - For providing the AI API
- **Bootstrap Team** - For the amazing CSS framework
- **FullCalendar** - For the calendar component
- **Ummalqura** - For Hijri calendar conversion
- **My School** - For the opportunity to develop this project

## 👨‍💻 Developer

**Haidar Ali Fawwaz Nasirodin (Dadarzz)**

This project was developed as a school project and personal portfolio, demonstrating practical application of web development concepts including Flask, SQLAlchemy, REST APIs, and front-ends.
## 📧 Contact & Support

For questions, issues, or suggestions:
- Create an issue on GitHub
- Email: [Your Email]
- School: GDA Jogja

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star!**

Made with ❤️ for the Rohis community
