# 🕌 Rohis Management System — Features Guide

A comprehensive web-based application for digitizing and streamlining Islamic student organization (Rohis) management in schools.

---

## 📋 Core Features

### 🔐 Authentication & Access Control

- **Role-Based Login System**
  - Email and password authentication with bcrypt hashing
  - Four role levels: Admin, Ketua, Pembina, Member
  - Forced password change on first login
  - Secure session management via Flask-Login

- **User Profile Management**
  - Upload and manage profile pictures (stored as BLOB in database)
  - Update personal information
  - Change password securely with current password verification
  - View member directory with profiles and contact info

### 👥 Member Management

- **Member Directory**
  - Browse all members with profile pictures, names, classes, and roles
  - Filter members by role (Admin, Ketua, Pembina, Member)
  - Search and sort functionality
  - Display attendance marking permissions and PIC assignments

- **Bulk Member Operations**
  - Add multiple members via CSV file upload
  - Batch add members via copy-paste (comma-separated format)
  - Support for: name, email, class, role
  - Individual member deletion with confirmation
  - Batch delete multiple members at once
  - Export member list to CSV

- **Member Assignment**
  - Assign members to PICs (Persons In Charge/Divisions)
  - Change member roles (Member → Pembina → Ketua → Admin)
  - Protect against deleting last admin
  - Grant/revoke attendance marking permissions
  - Assign members to core team for leadership tracking

### 📅 Session Management

- **Create & Schedule Sessions**
  - Schedule Rohis meetings and events with date and time
  - Three session types: All Members, Core Only, Events
  - Add optional descriptions for each session
  - Track session creation and modification dates

- **Session Control**
  - View all sessions with status indicators
  - Lock sessions to prevent further attendance marking
  - Assign multiple PICs to events for coordinated responsibility
  - Delete sessions (removes all attendance records and notes)
  - Filter sessions by type (All Members, Core, Events)

- **Session Statistics**
  - View attendance count per session
  - Track which sessions are locked vs open
  - See PIC assignments and coordinator information
  - Export attendance reports per session

### ✅ Attendance Tracking

- **Regular Member Attendance**
  - Mark attendance for all members in sessions
  - Four status options: Present, Absent, Excused, Late
  - One-click status change with immediate save
  - Rows lock after marking to prevent accidental changes
  - Session lock prevents further modifications

- **Core Team Attendance**
  - Separate tracking for Admin, Ketua, Pembina
  - Leadership attendance visibility
  - Same status options as regular members
  - Accessible only to core team members

- **Attendance Reports**
  - Download attendance as DOCX file with formatted table
  - Summary statistics (Present, Absent, Excused, Late counts)
  - Individual records with names, roles, timestamps
  - Timestamps recorded in WIB (Jakarta) timezone
  - Export includes session name and date

- **Attendance History**
  - Members can view their own attendance records
  - See status per session with dates
  - View summary statistics (total present, absent, excused)
  - Admins can view any member's attendance history
  - Filter and sort by session

### 📝 Meeting Minutes (Notulensi)

- **Rich Text Editor**
  - Full WYSIWYG editor (Quill.js)
  - Formatting: bold, italic, underline, strikethrough
  - Headers (h1-h3), lists (ordered & bullet)
  - Text alignment, colors, backgrounds
  - Link insertion support
  - HTML content saved to database

- **Auto-Save Functionality**
  - Real-time unsaved changes indicator
  - Warn user before leaving with unsaved changes
  - Save on button click with visual feedback
  - Display last update timestamp
  - Keyboard shortcut: Ctrl+S or Cmd+S to save

- **Notulensi Management**
  - Create new minutes per session
  - Edit existing notes with full history
  - Delete notes (admins only)
  - View full note content in dedicated view
  - AI-generated summaries for quick reading (when API available)

- **Meeting Summary**
  - Auto-generate brief 2-3 sentence summaries
  - Fallback to content preview if summary unavailable
  - Display in news feed for easy discovery
  - Show last update date on list view

### 📊 Analytics & Reporting

- **Attendance Analytics**
  - View member attendance history with statistics
  - Admin dashboard shows all member attendance data
  - Filter by member, session, or date range
  - Visual statistics cards (Total, Present, Absent, Excused)
  - Export attendance data to DOCX format

- **News Feed & Updates**
  - Upcoming sessions (next 3 upcoming events)
  - Recent meeting summaries (latest 3 notulensi)
  - PIC assignments for upcoming events
  - Quick links to read full meeting notes
  - Real-time data loading

- **Dashboard Cards**
  - Quick access shortcuts to all features
  - Role-specific dashboards for Admin vs Members
  - Visual indicators for special access (Can Mark Attendance)
  - Session type icons and status badges

### 🕌 Islamic Calendar Integration

- **Hijri Date Conversion**
  - Automatic conversion of Gregorian to Hijri dates
  - Display Hijri dates alongside session names
  - 40+ Islamic holidays included (Muharram through Dhu al-Hijjah)

- **Full Calendar Display**
  - Month, Week, Day, and List views
  - Interactive event browser
  - Color-coded events (Rohis sessions vs Islamic holidays)
  - Today's date highlighted and emphasized
  - Navigate between dates easily
  - Responsive design for mobile viewing

- **Holiday Reference**
  - Mawlid al-Nabi, Isra & Mi'raj, Ramadan dates
  - Eid celebrations (Fitr & Adha)
  - Day of Ashura, Laylat al-Qadr
  - Nuzul al-Qur'an and other significant dates

### 🤖 AI-Powered Features

- **Islamic Education Chatbot**
  - Ask questions about Islamic teachings and practices
  - Quick navigation commands (e.g., "Take me to attendance")
  - Formatted responses in natural language
  - Floating chat widget in bottom-right corner

- **Chatbot Capabilities**
  - Answer Islamic education questions
  - Guide navigation to features
  - Explain system functionality
  - Fallback to helpful messages when uncertain
  - No API key = graceful degradation

- **Meeting Minutes Summarization**
  - Auto-generate concise summaries of meeting notes
  - Intelligently extract key decisions and topics
  - Display in news feed for quick scanning
  - HTML-aware text extraction

### 🎭 Event & Division Management (PIC System)

- **Create Divisions/PICs**
  - Define roles like "Acara", "Konsumsi", "Dokumentasi"
  - Add descriptions of responsibilities
  - Track creation timestamps
  - Delete PICs (removes all user assignments)

- **Assign PICs to Events**
  - Attach multiple divisions to a single event
  - Enable coordination across responsibilities
  - Members see their assigned PIC's event details
  - PICs can mark attendance for their members

- **PIC-Based Attendance**
  - PIC coordinators mark attendance for their members
  - Automatic permission system
  - Members track PIC assignment status
  - View which members belong to each PIC

### 📅 Weekly Piket (Duty) Schedule

- **Schedule Management**
  - Assign members to specific days of the week
  - View weekly duty roster
  - Track assignment creation/update dates
  - Clear assignments by day
  - Multiple members per day supported

- **Member View**
  - Members see their assigned piket days
  - Visual calendar layout (Monday-Sunday)
  - See other assigned members per day
  - Know when reminders will be sent (06:00 WIB)
  - Quick overview of upcoming duties

- **Admin Control**
  - Bulk assign members to days
  - Edit schedules anytime
  - Clear all assignments for a day
  - View assignment history logs
  - Test email reminders before going live

### 💌 Automated Email Reminders

- **Daily Piket Reminders**
  - Automatic email at 06:00 WIB on assigned days
  - HTML-formatted professional email
  - Includes member responsibilities checklist
  - Optional additional information field
  - Graceful error handling

- **Reminder System**
  - Supports Mailjet and Resend email providers
  - Configurable via environment variables
  - Batch sending to multiple recipients
  - Failed email retry logic
  - Comprehensive error logging

- **Email Log History**
  - Track all sent reminders
  - View success/failure status
  - See recipient list per reminder
  - Display error messages when applicable
  - Statistics on success rate

- **Test Functionality**
  - Admins can test reminders manually
  - Send test emails before schedule goes live
  - Verify email addresses and content
  - Debug email delivery issues

### 🎨 User Interface & Experience

- **Responsive Design**
  - Works on desktop, tablet, and mobile
  - Bootstrap 5.3 framework
  - Mobile-first approach
  - Touch-friendly buttons and inputs

- **Modern Styling**
  - Gradient backgrounds and buttons
  - Smooth transitions and animations
  - Custom color scheme with CSS variables
  - Dark text on light backgrounds for readability
  - Hover effects and state indicators

- **Dashboard Views**
  - Admin dashboard with all features
  - Member dashboard with access to relevant features
  - Quick-access cards with icons
  - Role-specific content display
  - Breadcrumb navigation

- **Data Tables & Lists**
  - Sortable and filterable tables
  - Hover effects on rows
  - Inline action buttons
  - Responsive table scrolling on mobile
  - Empty state messages

- **Form Controls**
  - Date picker for session scheduling
  - Rich text editor for notes
  - File upload with validation
  - Dropdown selects for role/PIC assignment
  - Form validation and error messages

### 🔒 Security & Permissions

- **Role-Based Access Control**
  - Admin: Full system access
  - Ketua: Most features except user deletion
  - Pembina: Limited admin features
  - Member: View-only and personal data access

- **Permission Checks**
  - Attendance marking restricted by role
  - Edit/delete operations require permission
  - Session locking prevents unauthorized changes
  - PIC assignment validated before saving

- **Data Protection**
  - Password hashing with bcrypt
  - Session-based authentication
  - CSRF protection (Flask built-in)
  - SQL injection prevention via SQLAlchemy ORM
  - Secure password storage

### 💾 Data Management

- **Database Support**
  - SQLite for development
  - PostgreSQL for production
  - SQLAlchemy ORM for abstraction
  - Database migrations via Alembic
  - Automatic schema management

- **File Storage**
  - Profile pictures stored as BLOB in database
  - Support for PNG, JPG, JPEG, WebP formats
  - 5MB file size limit
  - Automatic filename sanitization
  - Default image fallback

- **Data Export**
  - Export attendance to DOCX format
  - CSV export for member lists
  - Download formatted reports
  - Timestamped file naming

---

## 🎯 Feature Availability by Role

### 👑 Admin
- Everything (full system access)
- Create/edit/delete sessions, PICs, members
- Mark attendance and lock sessions
- Manage email reminders and schedules
- View all analytics and reports

### 👔 Ketua (Chairman)
- Create sessions and mark attendance
- Manage members (add/edit, but not delete)
- Create/edit notulensi
- View analytics
- Manage piket schedules
- Cannot delete last admin

### 📚 Pembina (Advisor)
- Create sessions and mark attendance
- View member list
- Create/edit notulensi
- Limited attendance viewing
- Support admin functions

### 👤 Member
- View own attendance history
- Read meeting minutes
- View member directory
- View piket schedule
- Ask chatbot questions
- May have special "Can Mark Attendance" permission for their PIC

---

## 🚀 Advanced Workflows

### Event Coordination Workflow
1. Admin creates event session with "Event" type
2. Assigns multiple PICs (Acara, Konsumsi, Dokumentasi)
3. Each PIC coordinator marks attendance for their team
4. Admins create detailed meeting minutes after event
5. System generates summary for news feed
6. Members view event details and notes

### Weekly Piket Workflow
1. Admin sets up weekly duty schedule
2. Assigns members to specific days
3. System sends automatic email reminders at 06:00 WIB
4. Members see upcoming duties on their dashboard
5. Admin can test reminders before going live
6. Logs track all reminder sends and failures

### Member Onboarding Workflow
1. Admin batch-adds new members via CSV
2. System assigns default password
3. Members forced to change password on first login
4. Admins assign members to PICs
5. Members can upload profile picture
6. Members granted specific permissions as needed

---

## 📊 Data You Can Track

- Attendance records (date, session, status, timestamp)
- Member information (name, email, class, role, PIC)
- Session details (name, date, type, lock status)
- Meeting notes (content, creation/update dates)
- Email reminders (recipients, status, timestamps)
- User activities (login, profile updates, uploads)
- PIC assignments (member-to-division mappings)
- Weekly duty schedules (day-of-week assignments)

---

## ⚡ Performance Features

- **Auto-Save** on notulensi with change detection
- **Session Locking** prevents accidental modifications
- **One-Click Attendance** marking for speed
- **Batch Operations** for bulk member management
- **Caching** of profile pictures as BLOB
- **Lazy Loading** of news feed data

---

## 🔧 Technical Integrations

- **Groq API** for AI chatbot and summarization
- **Mailjet or Resend** for email delivery
- **FullCalendar** for interactive calendar display
- **Quill.js** for rich text editing
- **Hijri Calendar** library for Islamic date conversion
- **Python-DOCX** for document generation

---

## ✨ Quality of Life Features

- **Unsaved Changes Warning** prevents data loss
- **Keyboard Shortcuts** (Ctrl+S to save notulensi)
- **Dark Mode Aware** styling
- **Timezone Support** (WIB timestamps)
- **Loading Indicators** during operations
- **Success/Error Feedback** messages
- **Confirmation Dialogs** for destructive actions
- **Empty State Messages** guide users
- **Breadcrumb Navigation** for context
- **Back Buttons** on every page

---

## 📱 Responsive Features

- Mobile-friendly navigation
- Touch-friendly buttons and clickable areas
- Responsive tables with horizontal scroll
- Stacked layouts on small screens
- Optimized calendar view for mobile
- Mobile-optimized forms
- Touchscreen-friendly date picker

---

## 🛡️ System Reliability

- **Error Handling** with user-friendly messages
- **Graceful Degradation** when APIs unavailable
- **Fallback Content** if summaries fail
- **Database Integrity** via constraints
- **Logging** of all major operations
- **Session Management** prevents data loss
- **Transaction Safety** for critical operations

---

**Last Updated:** February 2026
**Version:** 1.0 - Feature Complete Release
