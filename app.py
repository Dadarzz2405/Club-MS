#NEEDED LIBRARIES RAHHHHHH, kinda messy
from utils import can_mark_attendance, is_core_user
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, Response, Blueprint
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from models import (
    Pic, db, User, Session, Attendance, Notulensi,
    Division, JadwalPiket, PiketAssignment, EmailReminderLog, SessionPIC
)
from datetime import datetime, date, timezone, timedelta
from ummalqura.hijri_date import HijriDate
import json
from werkzeug.utils import secure_filename
from ai import call_chatbot_groq
from flask_migrate import Migrate
import csv
from io import TextIOWrapper, StringIO, BytesIO
from docx import Document
from formatter import format_attendance
from summarizer import summarize_notulensi
from sqlalchemy.exc import IntegrityError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from email_service import get_email_service
import logging

# Load environment variables from .env file in development
load_dotenv()

logger = logging.getLogger(__name__)
UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
#init for all the librariessss
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)
attendance_bp = Blueprint("attendance", __name__)

#manager ofc, t can see it
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#cofee for the render service
@app.route('/health', methods=['GET'])
def health_check():
    from datetime import datetime
    return jsonify({
        'status': 'ok',
        'service': 'Rohis Attendance System',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'App is awake and running'
    })
#Login, no need comment actually
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.must_change_password:
                return redirect(url_for('profile'))
            else:
                if user.role in ['admin', 'ketua', 'pembina']:
                    return redirect(url_for('dashboard_admin'))
                else:
                    return redirect(url_for('dashboard_member'))
        else:
            flash('Invalid email or password', 'error')
        
    return render_template('login.html')

#home route ofc, need this, i'm an admin ofc
@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role in ['admin', 'ketua', 'pembina']:
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_member'))
    else:
        return redirect(url_for('login'))
#Dashboards, admin on top
@app.route('/dashboard_admin')
@login_required
def dashboard_admin():
    if not current_user.role in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    return render_template('dashboard_admin.html')

@app.route('/dashboard_member')
@login_required
def dashboard_member():
    if current_user.role in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('dashboard_admin'))
    return render_template('dashboard_member.html')
#profile bruhh, make it less boring
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already taken', 'error')
            return redirect(url_for('profile')) 

        current_user.username = username
        
        if password: 
            current_user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/member-list')
@login_required
def member_list():
    users = User.query.all()
    return render_template('member_list.html', users=users)


@app.route('/member/add', methods=['POST'])
@login_required
def add_member():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_list'))

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    class_name = request.form.get('class_name') or None
    role = request.form.get('role') or 'member'

    if not name or not email:
        flash('Name and email are required', 'error')
        return redirect(url_for('member_list'))

    # Default password for new members
    default_password = 'rohisnew'
    hashed = bcrypt.generate_password_hash(default_password).decode('utf-8')

    new_user = User(name=name, email=email, class_name=class_name, role=role, password=hashed)
    try:
        db.session.add(new_user)
        db.session.commit()
        flash(f'Created member {name} with default password.', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('A user with that email already exists.', 'error')

    return redirect(url_for('member_list'))


@app.route('/member/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_member(user_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_list'))

    user = User.query.get_or_404(user_id)

    # Prevent deleting self
    if user.id == current_user.id:
        flash("You cannot delete your own account.", 'error')
        return redirect(url_for('member_list'))

    # Prevent removing the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot delete the last admin user.', 'error')
            return redirect(url_for('member_list'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Member deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete member.', 'error')

    return redirect(url_for('member_list'))


@app.route('/member/change-role/<int:user_id>', methods=['POST'])
@login_required
def change_member_role(user_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_list'))

    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if not new_role:
        flash('Role is required.', 'error')
        return redirect(url_for('member_list'))

    # Prevent removing last admin
    if user.role == 'admin' and new_role != 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot remove admin role from the last admin.', 'error')
            return redirect(url_for('member_list'))

    user.role = new_role
    db.session.commit()
    flash('Member role updated.', 'success')
    return redirect(url_for('member_list'))


@app.route('/member-management')
@login_required
def member_management():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_list'))

    users = User.query.order_by(User.name).all()
    all_pics = Pic.query.order_by(Pic.name).all()
    return render_template('member_management.html', users=users, all_pics=all_pics)


@app.route('/member-management/batch-add', methods=['POST'])
@login_required
def member_management_batch_add():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_management'))

    # Accept CSV file upload or bulk textarea input
    csv_file = request.files.get('csv_file')
    bulk_text = request.form.get('bulk_text', '').strip()
    default_password = 'rohisnew'
    hashed = bcrypt.generate_password_hash(default_password).decode('utf-8')
    added = 0
    errors = []

    def add_user_row(name, email, class_name, role):
        nonlocal added
        if not name or not email:
            return
        email_l = email.strip().lower()
        existing = User.query.filter_by(email=email_l).first()
        if existing:
            errors.append(f'User with email {email_l} already exists')
            return
        try:
            u = User(name=name.strip(), email=email_l, class_name=(class_name or None), role=(role or 'member'), password=hashed)
            db.session.add(u)
            db.session.commit()
            added += 1
        except IntegrityError:
            db.session.rollback()
            errors.append(f'Failed to add {email_l} (integrity)')

    # Handle CSV
    if csv_file and csv_file.filename:
        try:
            stream = TextIOWrapper(csv_file.stream, encoding='utf-8')
            reader = csv.reader(stream)
            # detect header: name,email,class,role or similar
            for row in reader:
                if not row or all(not c.strip() for c in row):
                    continue
                # support flexible columns
                if len(row) >= 2:
                    name = row[0]
                    email = row[1]
                    class_name = row[2] if len(row) > 2 else None
                    role = row[3] if len(row) > 3 else 'member'
                    add_user_row(name, email, class_name, role)
        except Exception as e:
            errors.append(f'Failed to parse CSV: {e}')

    if bulk_text:
        for line in StringIO(bulk_text):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                name = parts[0]
                email = parts[1]
                class_name = parts[2] if len(parts) > 2 else None
                role = parts[3] if len(parts) > 3 else 'member'
                add_user_row(name, email, class_name, role)

    if added:
        flash(f'Added {added} members.', 'success')
    if errors:
        for e in errors:
            flash(e, 'warning')

    return redirect(url_for('member_management'))


@app.route('/member-management/batch-delete', methods=['POST'])
@login_required
def member_management_batch_delete():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_management'))

    # Expect a list of user ids named 'selected_ids' (comma-separated) or multiple form fields
    selected = request.form.getlist('selected_ids') or []
    # if single string comma-separated
    if len(selected) == 1 and ',' in selected[0]:
        selected = [s.strip() for s in selected[0].split(',') if s.strip()]

    try:
        ids = [int(i) for i in selected]
    except ValueError:
        flash('Invalid user selection', 'error')
        return redirect(url_for('member_management'))

    if not ids:
        flash('No members selected for deletion', 'warning')
        return redirect(url_for('member_management'))

    # Protect self-deletion and last-admin
    users_to_delete = User.query.filter(User.id.in_(ids)).all()
    admin_count = User.query.filter_by(role='admin').count()
    removing_admins = sum(1 for u in users_to_delete if u.role == 'admin')

    # Prevent deleting self
    if any(u.id == current_user.id for u in users_to_delete):
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('member_management'))

    if admin_count - removing_admins < 1:
        flash('Cannot delete selected admins because this would remove the last admin.', 'error')
        return redirect(url_for('member_management'))

    deleted = 0
    for u in users_to_delete:
        try:
            db.session.delete(u)
            db.session.commit()
            deleted += 1
        except Exception:
            db.session.rollback()
            flash(f'Failed to delete {u.email}', 'warning')

    flash(f'Deleted {deleted} members.', 'success')
    return redirect(url_for('member_management'))


@app.route('/member/<int:user_id>/assign-pic', methods=['POST', 'GET'])
@login_required
def assign_member_to_pic(user_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        flash('Access denied', 'error')
        return redirect(url_for('member_management'))
    
    user = User.query.get_or_404(user_id)
    pic_id = request.form.get('pic_id')
    
    try:
        if pic_id and pic_id.strip():
            # Assign to PIC
            pic_id = int(pic_id)
            pic = Pic.query.get(pic_id)
            
            if not pic:
                flash(f'Invalid PIC selected', 'error')
                return redirect(url_for('member_management'))
            
            user.pic_id = pic_id
            flash(f'✅ {user.name} assigned to {pic.name}', 'success')
        else:
            # Remove PIC assignment
            if user.pic_id:
                old_pic = Pic.query.get(user.pic_id)
                user.pic_id = None
                flash(f'Removed {user.name} from {old_pic.name if old_pic else "PIC"}', 'info')
            else:
                flash(f'{user.name} has no PIC assignment', 'info')
        
        # Also update attendance permission if needed
        # user.can_mark_attendance = (user.pic_id is not None)
        
        db.session.commit()
        
    except ValueError:
        flash('Invalid PIC ID format', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error assigning PIC: {str(e)}', 'error')
    
    return redirect(url_for('member_management'))


# ============================================================================
# SESSION MANAGEMENT ROUTES (CORRECTED)
# ============================================================================

@app.route('/sessions/manage')
@login_required
def manage_sessions():
    """View and manage all sessions"""
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    
    sessions = Session.query.order_by(Session.date.desc()).all()
    return render_template('session_management.html', sessions=sessions)


@app.route('/create-session', methods=['GET', 'POST'])
@login_required
def create_session():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        date = request.form.get('date', '').strip()
        session_type = request.form.get('session_type', 'all')
        description = request.form.get('description', '').strip()
        
        if not name or not date:
            flash('Name and date are required', 'error')
            return redirect(url_for('create_session'))
        
        # Validate session type
        if session_type not in ['all', 'core', 'event']:
            session_type = 'all'
        
        # Create session (no PIC assignment here)
        new_session = Session(
            name=name,
            date=date,
            session_type=session_type,
            description=description if description else None
        )
        
        try:
            db.session.add(new_session)
            db.session.commit()
            
            # Redirect to PIC assignment if it's an event
            if session_type == 'event':
                flash(f'Event "{name}" created! Now assign PICs to coordinate.', 'success')
                return redirect(url_for('assign_pics_to_session', session_id=new_session.id))
            else:
                flash(f'Session "{name}" created successfully!', 'success')
                return redirect(url_for('manage_sessions'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating session: {str(e)}', 'error')
            return redirect(url_for('create_session'))
    
    # GET request - show form (no PICs needed)
    return render_template('create_session.html')


@app.route('/api/session/<int:session_id>/delete', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Delete a session and all related data (including SessionPIC assignments)"""
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return jsonify({"error": "Access denied"}), 403
    
    try:
        session = Session.query.get_or_404(session_id)
        session_name = session.name
        
        # Delete SessionPIC assignments
        SessionPIC.query.filter_by(session_id=session_id).delete()
        
        # Delete attendance records
        Attendance.query.filter_by(session_id=session_id).delete()
        
        # Delete notulensi
        Notulensi.query.filter_by(session_id=session_id).delete()
        
        # Delete session
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f'Session "{session_name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting session: {e}")
        return jsonify({
            "error": "database_error",
            "message": str(e)
        }), 500


# ============================================================================
# PIC-TO-SESSION ASSIGNMENT ROUTES (NEW)
# ============================================================================

@app.route('/session/<int:session_id>/assign-pics', methods=['GET', 'POST'])
@login_required
def assign_pics_to_session(session_id):
    """Assign PICs (divisions) to a session"""
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    
    session = Session.query.get_or_404(session_id)
    
    if request.method == 'POST':
        # Get selected PIC IDs
        pic_ids = request.form.getlist('pic_ids')
        
        try:
            # Remove all existing PIC assignments for this session
            SessionPIC.query.filter_by(session_id=session_id).delete()
            
            # Add new PIC assignments
            for pic_id_str in pic_ids:
                try:
                    pic_id = int(pic_id_str)
                    # Verify PIC exists
                    pic = Pic.query.get(pic_id)
                    if pic:
                        session_pic = SessionPIC(
                            session_id=session_id,
                            pic_id=pic_id
                        )
                        db.session.add(session_pic)
                except (ValueError, TypeError):
                    continue
            
            db.session.commit()
            flash(f'PICs updated for "{session.name}"', 'success')
            return redirect(url_for('assign_pics_to_session', session_id=session_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating PICs: {str(e)}', 'error')
            return redirect(url_for('assign_pics_to_session', session_id=session_id))
    
    # GET request - show form
    available_pics = Pic.query.all()
    return render_template(
        'assign_pics_to_session.html',
        session=session,
        available_pics=available_pics
    )


@app.route('/session/<int:session_id>/remove-pic/<int:pic_id>', methods=['POST'])
@login_required
def remove_pic_from_session(session_id, pic_id):
    """Remove a specific PIC from a session"""
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    
    try:
        session_pic = SessionPIC.query.filter_by(
            session_id=session_id,
            pic_id=pic_id
        ).first()
        
        if session_pic:
            pic_name = session_pic.pic.name
            db.session.delete(session_pic)
            db.session.commit()
            flash(f'Removed "{pic_name}" from this session', 'success')
        else:
            flash('PIC assignment not found', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing PIC: {str(e)}', 'error')
    
    return redirect(url_for('assign_pics_to_session', session_id=session_id))

# ============================================================================
# UPDATED PIC MANAGEMENT (NO SESSION ASSIGNMENT)
# ============================================================================

@app.route('/pics', methods=['GET', 'POST'])
@login_required
def manage_pics():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash("PIC name cannot be empty", "error")
            return redirect(url_for('manage_pics'))

        existing = Pic.query.filter_by(name=name).first()
        if existing:
            flash(f"PIC '{name}' already exists!", "error")
        else:
            new_pic = Pic(
                name=name,
                description=description if description else None
            )
            db.session.add(new_pic)
            db.session.commit()
            flash(f"PIC '{name}' created successfully!", "success")

        return redirect(url_for('manage_pics'))

    pics = Pic.query.all()
    return render_template('manage_pic.html', pics=pics)


@app.route('/pic/delete/<int:id>', methods=['POST'])
@login_required
def delete_pic(id):
    """Delete a PIC and remove all its assignments"""
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)

    pic = Pic.query.get_or_404(id)
    pic_name = pic.name

    # Remove PIC from users
    for user in pic.members:
        user.pic_id = None
        user.can_mark_attendance = False

    # Remove PIC from sessions (SessionPIC table)
    SessionPIC.query.filter_by(pic_id=id).delete()

    # Delete the PIC
    db.session.delete(pic)
    db.session.commit()

    flash(f"PIC '{pic_name}' deleted and all assignments removed", "success")
    return redirect(url_for('manage_pics'))


# ============================================================================
# UPDATED ATTENDANCE ROUTES FOR SESSION TYPES
# ============================================================================

@app.route('/attendance-mark')
@login_required
def attendance_mark():
    if current_user.role not in ['admin', 'ketua']:
        abort(403)
    
    # Filter sessions based on type
    # Core members can see all sessions
    # Regular members only see 'all' type sessions
    if current_user.role in ['admin', 'ketua', 'pembina']:
        sessions = Session.query.order_by(Session.date.desc()).all()
    else:
        sessions = Session.query.filter_by(session_type='all').order_by(Session.date.desc()).all()
    
    # Get members based on session type (this will be handled in the template)
    users = User.query.filter(User.role == 'member').all()
    
    return render_template('attendance_mark_core.html', sessions=sessions, users=users)


@app.route('/attendance/core')
@login_required
def attendance_core():
    """Core member attendance - only show core and event sessions"""
    if not is_core_user(current_user):
        abort(403)
    sessions = Session.query.filter(
        Session.session_type.in_(['core', 'event'])
    ).order_by(Session.date.desc()).all()
    
    users = User.query.filter(User.role.in_(["admin", "ketua", "pembina"])).all()
    core_users = users

    return render_template(
        "attendance_mark_core.html",
        sessions=sessions,
        users=users,
        core_users=core_users
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_eligible_users_for_session(session):
    if session.session_type == 'core':
        # Only core members
        return User.query.filter(User.role.in_(['admin', 'ketua', 'pembina'])).all()
    elif session.session_type == 'event':
        # All members, but can be filtered by PIC
        if session.pic_id:
            return User.query.filter_by(pic_id=session.pic_id).all()
        return User.query.all()
    else:  # 'all'
        # All members
        return User.query.filter(User.role == 'member').all()

#idk why the hell the import is here but just go on lah ya...
from datetime import date
@app.route('/api/attendance', methods=['POST'])
@login_required
def api_attendance():
    data = request.get_json()

    session_id = data.get("session_id")
    user_id = data.get("user_id")
    status = data.get("status")

    if not all([session_id, user_id, status]):
        return jsonify({"error": "invalid_data", "message": "Missing required fields"}), 400

    try:
        session_id = int(session_id)
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({"error": "invalid_data", "message": "Invalid ID format"}), 400

    session = Session.query.get(session_id)
    if not session:
        return jsonify({"error": "invalid_data", "message": "Session not found"}), 404

    if session.is_locked:
        return jsonify({"error": "session_locked", "message": "This session is locked"}), 403

    if not can_mark_attendance(current_user, session.pic_id):
        return jsonify({"error": "forbidden", "message": "You don't have permission"}), 403

    # Check if already marked
    existing_record = Attendance.query.filter_by(
        session_id=session_id,
        user_id=user_id,
        attendance_type='regular'
    ).first()

    if existing_record:
        return jsonify({"error": "already_marked", "message": "Attendance already recorded"}), 409

    wib = timezone(timedelta(hours=7))
    attendance = Attendance(
        session_id=session_id,
        user_id=user_id,
        status=status,
        attendance_type='regular',
        timestamp=datetime.now(wib)
    )
    try:
        db.session.add(attendance)
        db.session.commit()
        return jsonify({"success": True})
    except IntegrityError as e:
        db.session.rollback()
        print(f"Integrity error: {e}")
        return jsonify({"error": "already_marked", "message": "Attendance already recorded"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({"error": "database_error", "message": str(e)}), 500
@app.route("/api/attendance/core", methods=["POST"])
@login_required
def api_attendance_core():
    if not is_core_user(current_user):
        return jsonify({"error": "forbidden", "message": "Access denied"}), 403

    data = request.get_json()
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    status = data.get("status")

    if not all([session_id, user_id, status]):
        return jsonify({"error": "invalid_data", "message": "Missing required fields"}), 400

    try:
        session_id = int(session_id)
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({"error": "invalid_data", "message": "Invalid ID format"}), 400

    session = Session.query.get(session_id)
    if not session:
        return jsonify({"error": "invalid_data", "message": "Session not found"}), 404

    if session.is_locked:
        return jsonify({"error": "session_locked", "message": "This session is locked"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "invalid_data", "message": "User not found"}), 404

    if not is_core_user(user):
        return jsonify({"error": "not_core_user", "message": "User is not a core member"}), 400

    existing_record = Attendance.query.filter_by(
        session_id=session_id,
        user_id=user_id,
        attendance_type="core"
    ).first()

    if existing_record:
        return jsonify({"error": "already_marked", "message": "Attendance already recorded"}), 409

    wib = timezone(timedelta(hours=7))
    att = Attendance(
        session_id=session_id,
        user_id=user_id,
        status=status,
        attendance_type="core",
        timestamp=datetime.now(wib)
    )

    try:
        db.session.add(att)
        db.session.commit()
        return jsonify({"success": True})
    except IntegrityError as e:
        db.session.rollback()
        print(f"Integrity error: {e}")
        return jsonify({"error": "already_marked", "message": "Attendance already recorded"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({"error": "database_error", "message": str(e)}), 500
    
@app.route("/api/session/<int:session_id>/status", methods=["GET"])
@login_required
def get_session_status(session_id):
    """Get session lock status"""
    session = Session.query.get_or_404(session_id)
    return jsonify({
        "is_locked": session.is_locked,
        "session_id": session.id,
        "name": session.name
    })

@app.route("/api/session/<int:session_id>/lock", methods=["POST"])
@login_required
def lock_session(session_id):
    if current_user.role not in ["admin", "ketua", "pembina"]:
        return jsonify({"error": "forbidden"}), 403

    session = Session.query.get_or_404(session_id)
    session.is_locked = True
    db.session.commit()

    return jsonify({"locked": True})
    
#DOWNLOAD ATTENDANCE RAHHHHH
@app.route("/export/attendance/<int:session_id>")
@login_required
def export_attendance_csv(session_id):
    if current_user.role not in ["admin", "ketua", "pembina"]:
        abort(403)

    session = Session.query.get_or_404(session_id)

    records = (
        db.session.query(
            Attendance,
            User.name,
            User.email,
            User.role
        )
        .join(User, Attendance.user_id == User.id)
        .filter(Attendance.session_id == session_id)
        .order_by(User.name)
        .all()
    )

    if not records:
        flash("No attendance records found for this session", "warning")
        return redirect(url_for('attendance_mark'))

    wib = timezone(timedelta(hours=7))
    
    doc = Document()
    doc.add_heading(f'Attendance Report: {session.name}', 0)
    doc.add_paragraph(f'Date: {session.date}')
    doc.add_paragraph(f'Total Attendees: {len(records)}')
    doc.add_paragraph('')
    
    summary = {
        'present': sum(1 for a, _, _, _ in records if a.status == 'present'),
        'absent': sum(1 for a, _, _, _ in records if a.status == 'absent'),
        'excused': sum(1 for a, _, _, _ in records if a.status == 'excused'),
        'late': sum(1 for a, _, _, _ in records if a.status == 'late'),
    }
    
    doc.add_heading('Summary', level=1)
    summary_table = doc.add_table(rows=5, cols=2)
    summary_table.style = 'Light Grid Accent 1'
    
    summary_data = [
        ('Status', 'Count'),
        ('Present', str(summary['present'])),
        ('Absent', str(summary['absent'])),
        ('Excused', str(summary['excused'])),
        ('Late', str(summary['late']))
    ]
    
    for i, (label, value) in enumerate(summary_data):
        summary_table.rows[i].cells[0].text = label
        summary_table.rows[i].cells[1].text = value
    
    doc.add_paragraph('')
    
    doc.add_heading('Detailed Records', level=1)
    
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Light Grid Accent 1'
    
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Name'
    header_cells[1].text = 'Role'
    header_cells[2].text = 'Status'
    header_cells[3].text = 'Time'
    header_cells[4].text = 'Type'
    
    for attendance, name, email, role in records:
        row_cells = table.add_row().cells
        row_cells[0].text = name
        row_cells[1].text = role.capitalize()
        row_cells[2].text = attendance.status.capitalize()
        formatted_time = attendance.timestamp.astimezone(wib).strftime("%H:%M")
        row_cells[3].text = formatted_time
        row_cells[4].text = attendance.attendance_type.capitalize()
    
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)

    filename = f"attendance_{session.name.replace(' ', '_')}_{session.date}.docx"

    return Response(
        bio,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@app.route('/attendance-history')
@login_required
def attendance_history():
    records = Attendance.query.filter_by(user_id=current_user.id).all()

    summary = {
        'present': sum(1 for r in records if r.status=='present'),
        'absent': sum(1 for r in records if r.status=='absent'),
        'excused': sum(1 for r in records if r.status=='excused')
    }

    return render_template('attendance_history.html', records=records, summary=summary)

@app.route('/attendance-history-admin')
@login_required
def attendance_history_admin():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('invalid_credential')) 
    users = User.query.filter(User.role=='member').all()
    return render_template('attendance_history_admin.html', users=users)

@app.route('/attendance-history-admin/<int:user_id>')
@login_required
def attendance_history_admin_view(user_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('invalid_credential'))
    
    selected_user = User.query.get_or_404(user_id)

    records = Attendance.query.filter_by(user_id=user_id).all()
    
    summary = {
        'present': sum(1 for r in records if r.status=='present'),
        'absent': sum(1 for r in records if r.status=='absent'),
        'excused': sum(1 for r in records if r.status=='excused')
    }
    return render_template('attendance_history_admin_view.html', user=selected_user, records=records, summary=summary)

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if current_user.role in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('attendance_mark'))
    
    is_pic = current_user.can_mark_attendance
    if not is_pic and current_user.role != 'member':
        abort(403)
    
    if request.method == 'POST':
        session_id = request.form.get('session_id')
        if not session_id:
            flash('Session not selected', 'error')
            return redirect(url_for('attendance'))
        session = Session.query.get_or_404(session_id)
        if session.is_locked:
            flash('Session is locked', 'error')
            return redirect(url_for('attendance'))
        
        if is_pic:
            if not can_mark_attendance(current_user, session.pic_id):
                abort(403)
            members = User.query.filter_by(pic_id=current_user.id).all()
        else:
            members = User.query.filter(User.role == 'member').all()
        
        wib = timezone(timedelta(hours=7))
        for member in members:
            status = request.form.get(f'status_{member.id}')
            if status:
                existing = Attendance.query.filter_by(session_id=session_id, user_id=member.id, attendance_type='regular').first()
                if not existing:
                    attendance = Attendance(session_id=session_id, user_id=member.id, status=status, attendance_type='regular', timestamp=datetime.now(wib))
                    db.session.add(attendance)
        db.session.commit()
        flash('Attendance saved', 'success')
        return redirect(url_for('attendance'))
    
    selected_session_id = request.args.get('session_id')
    
    if is_pic:
        sessions = Session.query.filter_by(pic_id=current_user.id).all()
        members = User.query.filter_by(pic_id=current_user.id).all()
    else:
        sessions = Session.query.all()
        members = User.query.filter(User.role == 'member').all()
    
    attendance_map = {}
    if selected_session_id:
        attendances = Attendance.query.filter_by(session_id=selected_session_id, attendance_type='regular').all()
        for a in attendances:
            attendance_map[a.user_id] = a.status
    return render_template('attendance.html', sessions=sessions, members=members, selected_session_id=selected_session_id, attendance_map=attendance_map)

@app.route('/logout')
@login_required
def logout(): 
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not bcrypt.check_password_hash(current_user.password, old_password):
            flash("Incorrect current password.", "danger")
        elif new_password != confirm_password:
            flash("New passwords don't match.", "danger")
        else:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.must_change_password = False
            db.session.commit()
            flash("Password updated successfully!", "success")
            if current_user.role in ['admin', 'ketua', 'pembina']:
                return redirect(url_for('dashboard_admin'))
            else:
                return redirect(url_for('dashboard_member'))
    return render_template('change_password.html')

@app.route("/profile/upload_pfp", methods=['POST'])
@login_required
def upload_pfp():
    file = request.files.get('pfp')

    if not file or file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('profile'))
    
    filename_attr = getattr(file, 'filename', '')
    if not filename_attr or not allowed_file(filename_attr):
        flash('Invalid file type. Allowed types: png, jpg, jpeg, webp', 'error')
        return redirect(url_for('profile'))
    
    # Check file size (5MB limit)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        flash('File size too large. Maximum 5MB allowed.', 'error')
        return redirect(url_for('profile'))
    
    # Read file as binary
    image_data = file.read()
    
    # Store in database
    current_user.profile_picture_data = image_data
    current_user.profile_picture_filename = secure_filename(filename_attr)
    
    db.session.commit()
    flash('Profile picture updated successfully', 'success')
    return redirect(url_for('profile'))

# Add route to serve profile pictures from database:
@app.route("/profile-picture/<int:user_id>")
def serve_profile_picture(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.profile_picture_data:
        # Determine mime type from filename
        filename = user.profile_picture_filename or 'image.png'
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
        
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp'
        }
        
        mime_type = mime_types.get(ext, 'image/png')
        
        return Response(user.profile_picture_data, mimetype=mime_type)
    else:
        # Serve default image
        default_path = os.path.join('static', 'uploads', 'profiles', 'default.png')
        if os.path.exists(default_path):
            with open(default_path, 'rb') as f:
                return Response(f.read(), mimetype='image/png')
        else:
            abort(404)

ISLAMIC_HOLIDAYS = {
    # Muharram
    "01-01": "Islamic New Year",
    "01-09": "Day of Tasua",
    "01-10": "Day of Ashura",

    # Rabi' al-Awwal
    "03-12": "Mawlid al-Nabi",

    # Rajab
    "07-01": "Start of Rajab",
    "07-27": "Isra and Mi'raj",

    # Sha'ban
    "08-15": "Mid-Sha'ban (Laylat al-Bara'ah)",

    # Ramadan
    "09-01": "Start of Ramadan",
    "09-17": "Nuzul al-Qur'an",
    "09-21": "Laylat al-Qadr (possible)",
    "09-23": "Laylat al-Qadr (possible)",
    "09-25": "Laylat al-Qadr (possible)",
    "09-27": "Laylat al-Qadr (possible)",
    "09-29": "Laylat al-Qadr (possible)",

    # Shawwal
    "10-01": "Eid al-Fitr",
    "10-02": "Eid al-Fitr ",

    # Dhu al-Qi'dah
    "11-01": "Start of Dhuqa'dah",

    # Dhu al-Hijjah
    "12-01": "Start of Dhu al-Hijjah",
    "12-08": "Day of Tarwiyah",
    "12-09": "Day of Arafah",
    "12-10": "Eid al-Adha",
    "12-11": "Days of Tashreeq",
    "12-12": "Days of Tashreeq",
    "12-13": "Days of Tashreeq",
}

@app.route("/calendar")
@login_required
def calendar():
    
    return render_template("calendar.html")

def get_hijri_date(gregorian_date):
    try:
        g = datetime.strptime(gregorian_date, "%Y-%m-%d").date()
        h = HijriDate(g.year, g.month, g.day, gr=True)
        return f"{h.day} {h.month_name} {h.year} H"
    except Exception:
        return ""

def get_hijri_key_from_gregorian(g_date: date):
    h = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
    return f"{h.month:02d}-{h.day:02d}", h


    
@app.route('/api/dashboard_calendar')
@login_required
def api_dashboard_calendar():
    sessions = Session.query.all()
    calendar_events = []

    for session in sessions:
        hijri_date = get_hijri_date(session.date)
        calendar_events.append({
            'title': f"{session.name} ({hijri_date})",
            'start': session.date,
            'extendedProps': {
                'type': 'rohis_session'
            }
        })

    today = date.today()
    start_year = today.year - 1
    end_year = today.year + 1

    current = date(start_year, 1, 1)
    end = date(end_year, 12, 31)

    while current <= end:
        hijri_key, hijri = get_hijri_key_from_gregorian(current)

        if hijri_key in ISLAMIC_HOLIDAYS:
            calendar_events.append({
                'title': f"{ISLAMIC_HOLIDAYS[hijri_key]} ({hijri.day} {hijri.month_name} {hijri.year} H)",
                'start': current.isoformat(),
                'allDay': True,
                'backgroundColor': '#1e88e5',
                'borderColor': '#1565c0',
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': 'islamic_holiday',
                    'hijri': f"{hijri.day} {hijri.month_name} {hijri.year} H"
                }
            })

        current = current.fromordinal(current.toordinal() + 1)
    return jsonify(calendar_events)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question."})

    try:
        reply = call_chatbot_groq(user_message)
    except Exception as e:
        print("CHATBOT ERROR:", e)
        reply = "Error occurred. Check server logs."


    return jsonify({"reply": reply})

# Old pic management handler removed — use `manage_pics` (route: `/pics`).


@app.route("/api/notulensi/<int:session_id>", methods=["POST"])
@login_required
def save_notulensi(session_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    data = request.get_json()
    content = data.get("content", "").strip()

    if not content or content in ['<p><br></p>', '<p></p>', '<div><br></div>', '<div></div>']:
        return jsonify({"error": "Content cannot be empty"}), 400

    note = Notulensi.query.filter_by(session_id=session_id).first()

    if note:
        note.content = content
        note.updated_at = datetime.utcnow()
    else:
        note = Notulensi(session_id=session_id, content=content)
        db.session.add(note)

    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/notulensi/<int:notulensi_id>", methods=["DELETE"])
@login_required
def delete_notulensi(notulensi_id):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return jsonify({"error": "forbidden"}), 403
    
    note = Notulensi.query.get_or_404(notulensi_id)
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({"success": True})

@app.route("/notulensi-list")
@login_required
def notulensi_list():
    sessions = Session.query.order_by(Session.date.desc()).all()
    notulensis = Notulensi.query.all()
    notulensi_dict = {n.session_id: n for n in notulensis}
    
    return render_template("notulensi_list.html", sessions=sessions, notulensi_dict=notulensi_dict)

@app.route("/notulensi/<int:session_id>")
@login_required
def notulensi(session_id):
    session = Session.query.get_or_404(session_id)
    note = Notulensi.query.filter_by(session_id=session_id).first()
    
    can_edit = current_user.role in ['admin', 'ketua', 'pembina']
    
    return render_template("notulensi.html", session=session, note=note, can_edit=can_edit)

@app.route("/notulensi/view/<int:notulensi_id>")
@login_required
def notulensi_view(notulensi_id):
    """View full notulensi content (read-only for members)"""
    note = Notulensi.query.get_or_404(notulensi_id)
    session = Session.query.get_or_404(note.session_id)
    
    can_edit = current_user.role in ['admin', 'ketua', 'pembina']
    
    return render_template("notulensi_view.html", session=session, note=note, can_edit=can_edit)

@app.route('/api/news-feed')
@login_required
def news_feed():
    try:
        today = datetime.now().date()
        
        # Get upcoming sessions
        upcoming_sessions = Session.query.filter(
            Session.date >= str(today)
        ).order_by(Session.date.asc()).limit(3).all()
        
        # Get recent notulensi
        recent_notulensi = (
            db.session.query(Notulensi, Session)
            .join(Session, Notulensi.session_id == Session.id)
            .order_by(Notulensi.updated_at.desc())
            .limit(3)
            .all()
        )
        
        # Process upcoming sessions
        upcoming_data = []
        for session in upcoming_sessions:
            try:
                # Fetch PICs assigned to this session via SessionPIC
                pics = Pic.query.join(SessionPIC, Pic.id == SessionPIC.pic_id).filter(SessionPIC.session_id == session.id).all()
                if pics:
                    pic_names = ', '.join([p.name for p in pics])
                else:
                    pic_names = 'No PIC assigned'

                upcoming_data.append({
                    'id': session.id,
                    'name': session.name,
                    'date': session.date,
                    'pic': pic_names
                })
            except Exception as e:
                print(f"Error processing session {session.id}: {e}")
                continue
        
        # Process recent notulensi with better error handling
        recent_data = []
        for notulensi, session in recent_notulensi:
            try:
                # Try to generate summary, but have multiple fallbacks
                summary = "Meeting notes available."
                
                if notulensi and notulensi.content:
                    try:
                        # Only try to summarize if GROQ_API_KEY exists
                        if os.environ.get("GROQ_API_KEY"):
                            summary = summarize_notulensi(notulensi.content)
                        else:
                            #Fallback besik
                            from html import unescape
                            import re
                            clean_text = re.sub('<[^<]+?>', '', notulensi.content)
                            clean_text = unescape(clean_text).strip()
                            if len(clean_text) > 150:
                                summary = clean_text[:150] + "..."
                            else:
                                summary = clean_text if clean_text else "Meeting notes available."
                    except Exception as sum_error:
                        print(f"Summarization error for notulensi {notulensi.id}: {sum_error}")
                        # Fallback brok
                        try:
                            from html import unescape
                            import re
                            clean_text = re.sub('<[^<]+?>', '', notulensi.content)
                            clean_text = unescape(clean_text).strip()
                            summary = clean_text[:150] + "..." if len(clean_text) > 150 else (clean_text or "Meeting notes available.")
                        except:
                            summary = "Meeting notes available."
                
                recent_data.append({
                    'id': notulensi.id,
                    'session_name': session.name,
                    'session_date': session.date,
                    'summary': summary,
                    'updated_at': notulensi.updated_at.strftime('%d %b %Y') if notulensi.updated_at else notulensi.created_at.strftime('%d %b %Y')
                })
            except Exception as e:
                print(f"Error processing notulensi {notulensi.id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return jsonify({
            'success': True,
            'upcoming': upcoming_data,
            'recent': recent_data
        }), 200
        
    except Exception as e:
        print(f"CRITICAL News feed error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': True, 
            'upcoming': [],
            'recent': [],
            'error': str(e)
        }), 200  
    
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# ============================================================================
# CRON ENDPOINT - Called by external scheduler (cron-job.org)
# ============================================================================

@app.route('/api/cron/piket-reminder', methods=['POST'])
@app.route('/api/cron/piket-reminder', methods=['POST'])
def cron_piket_reminder():
    expected_token = os.environ.get('CRON_SECRET_TOKEN')
    
    if not expected_token:
        app.logger.error("CRON_SECRET_TOKEN not set - piket reminders disabled")
        return jsonify({
            'success': False,
            'error': 'Service not configured'
        }), 503 
    try:
        # Get current day in WIB timezone (UTC+7)
        wib = timezone(timedelta(hours=7))
        now_wib = datetime.now(wib)
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = now_wib.weekday()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[day_of_week]
        date_str = now_wib.strftime('%d %B %Y')
        
        # Find jadwal for today
        jadwal = JadwalPiket.query.filter_by(day_of_week=day_of_week).first()
        
        if not jadwal:
            # No jadwal configured for this day - log and return
            log = EmailReminderLog(
                day_of_week=day_of_week,
                day_name=day_name,
                recipients_count=0,
                recipients='[]',
                status='skipped',
                error_message='No jadwal piket configured for this day'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'No piket scheduled for {day_name}',
                'day': day_name,
                'date': date_str,
                'recipients_count': 0
            }), 200
        
        # Get assigned users for today
        assignments = PiketAssignment.query.filter_by(jadwal_id=jadwal.id).all()
        
        if not assignments:
            # Jadwal exists but no members assigned
            log = EmailReminderLog(
                day_of_week=day_of_week,
                day_name=day_name,
                recipients_count=0,
                recipients='[]',
                status='skipped',
                error_message='No members assigned to this day'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'No members assigned for {day_name}',
                'day': day_name,
                'date': date_str,
                'recipients_count': 0
            }), 200
        
        # Collect recipient emails
        recipients = []
        for assignment in assignments:
            user = assignment.user
            if user and user.email:
                recipients.append(user.email)
        
        if not recipients:
            # Assignments exist but no valid emails
            log = EmailReminderLog(
                day_of_week=day_of_week,
                day_name=day_name,
                recipients_count=0,
                recipients='[]',
                status='failed',
                error_message='No valid email addresses found for assigned members'
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': 'No valid email addresses found',
                'day': day_name,
                'date': date_str
            }), 500
        
        # Send emails
        email_service = get_email_service()
        result = email_service.send_piket_reminder(
            recipients=recipients,
            day_name=day_name,
            date_str=date_str,
            additional_info=""  # Can be customized
        )
        
        # Log the reminder
        log = EmailReminderLog(
            day_of_week=day_of_week,
            day_name=day_name,
            recipients_count=len(recipients),
            recipients=json.dumps(recipients),
            status='success' if result['success'] else 'partial',
            error_message=result.get('message') if not result['success'] else None
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': result['message'],
            'day': day_name,
            'date': date_str,
            'recipients_count': len(recipients),
            'failed_emails': result.get('failed_emails', [])
        }), 200
        
    except Exception as e:
        # Log the error
        try:
            error_log = EmailReminderLog(
                day_of_week=now_wib.weekday() if 'now_wib' in locals() else -1,
                day_name='Unknown',
                recipients_count=0,
                recipients='[]',
                status='failed',
                error_message=str(e)
            )
            db.session.add(error_log)
            db.session.commit()
        except:
            pass
        
        print(f"Piket reminder error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ADMIN ROUTES - Manage jadwal piket
# ============================================================================

@app.route('/admin/jadwal-piket', methods=['GET', 'POST'])
@login_required
def admin_jadwal_piket():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    
    if request.method == 'POST':
        try:
            data = request.form
            day_of_week = int(data.get('day_of_week'))
            user_ids = request.form.getlist('user_ids')
            
            # Validate day
            if day_of_week < 0 or day_of_week > 6:
                flash('Invalid day of week', 'error')
                return redirect(url_for('admin_jadwal_piket'))
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_name = day_names[day_of_week]
            
            # Get or create jadwal for this day
            jadwal = JadwalPiket.query.filter_by(day_of_week=day_of_week).first()
            if not jadwal:
                jadwal = JadwalPiket(
                    day_of_week=day_of_week,
                    day_name=day_name
                )
                db.session.add(jadwal)
                db.session.flush()  # Get the ID
            
            # Remove existing assignments for this day
            PiketAssignment.query.filter_by(jadwal_id=jadwal.id).delete()
            
            # Add new assignments
            for user_id in user_ids:
                if user_id:  # Skip empty values
                    assignment = PiketAssignment(
                        jadwal_id=jadwal.id,
                        user_id=int(user_id)
                    )
                    db.session.add(assignment)
            
            # Update timestamp
            jadwal.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash(f'Jadwal piket for {day_name} updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating jadwal piket: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Error updating schedule: {str(e)}', 'error')
        
        return redirect(url_for('admin_jadwal_piket'))
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    schedule = []
    for day_idx, day_name in enumerate(day_names):
        jadwal = JadwalPiket.query.filter_by(day_of_week=day_idx).first()
        
        assignments = []
        if jadwal:
            assignments = [
                {
                    'id': a.user.id,
                    'name': a.user.name,
                    'email': a.user.email,
                    'class': a.user.class_name
                }
                for a in jadwal.assignments
            ]
        
        schedule.append({
            'day_of_week': day_idx,
            'day_name': day_name,
            'jadwal_id': jadwal.id if jadwal else None,
            'assignments': assignments,
            'updated_at': jadwal.updated_at if jadwal else None
        })
    
    all_members = User.query.filter(User.role.in_(['member', 'admin', 'ketua'])).order_by(User.name).all()
    
    return render_template(
        'admin_jadwal_piket.html',
        schedule=schedule,
        all_members=all_members
    )


@app.route('/admin/jadwal-piket/clear/<int:day_of_week>', methods=['POST'])
@login_required
def clear_jadwal_piket(day_of_week):
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    
    try:
        jadwal = JadwalPiket.query.filter_by(day_of_week=day_of_week).first()
        if jadwal:
            PiketAssignment.query.filter_by(jadwal_id=jadwal.id).delete()
            db.session.commit()
            flash('Assignments cleared successfully', 'success')
        else:
            flash('No schedule found for this day', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing assignments: {str(e)}', 'error')
    
    return redirect(url_for('admin_jadwal_piket'))

# ============================================================================
# MEMBER ROUTES - View jadwal piket
# ============================================================================

@app.route('/jadwal-piket')
@login_required
def view_jadwal_piket():
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    wib = timezone(timedelta(hours=7))
    today = datetime.now(wib).weekday()
    
    schedule = []
    for day_idx, day_name in enumerate(day_names):
        jadwal = JadwalPiket.query.filter_by(day_of_week=day_idx).first()
        
        assignments = []
        if jadwal:
            assignments = [
                {
                    'name': a.user.name,
                    'class': a.user.class_name,
                    'is_current_user': a.user.id == current_user.id
                }
                for a in jadwal.assignments
            ]
        
        schedule.append({
            'day_of_week': day_idx,
            'day_name': day_name,
            'assignments': assignments,
            'is_today': day_idx == today
        })
    
    return render_template('view_jadwal_piket.html', schedule=schedule)


# ============================================================================
# ADMIN ROUTE - View email logs
# ============================================================================
@app.route('/admin/piket-logs')
@login_required
def view_piket_logs():
    """View email reminder logs (admin only)"""
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)
    
    logs = EmailReminderLog.query.order_by(EmailReminderLog.sent_at.desc()).limit(100).all()
    
    return render_template('piket_logs.html', logs=logs)


# ============================================================================
# MANUAL TRIGGER - Test the reminder system
# ============================================================================
@app.route('/admin/piket-test', methods=['POST'])
@login_required
def test_piket_reminder():
    if current_user.role not in ['admin']:
        abort(403)
    
    try:
        day_of_week = int(request.form.get('day_of_week', datetime.now().weekday()))
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[day_of_week]
        
        jadwal = JadwalPiket.query.filter_by(day_of_week=day_of_week).first()
        
        if not jadwal or not jadwal.assignments:
            flash(f'No assignments found for {day_name}', 'warning')
            return redirect(url_for('admin_jadwal_piket'))
        
        recipients = [a.user.email for a in jadwal.assignments if a.user.email]
        
        if not recipients:
            flash('No valid email addresses found', 'error')
            return redirect(url_for('admin_jadwal_piket'))
        
        email_service = get_email_service()
        result = email_service.send_piket_reminder(
            recipients=recipients,
            day_name=day_name,
            date_str=datetime.now().strftime('%d %B %Y'),
            additional_info="⚠️ This is a TEST reminder from the admin panel."
        )
        
        if result['success']:
            flash(f"Test reminder sent to {len(recipients)} recipients", 'success')
        else:
            flash(f"Error: {result['message']}", 'error')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin_jadwal_piket'))

#Start the entire hundreds line of code program taht i made 
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)  