from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os
from models import Pic, db, User, Session, Attendance
from datetime import datetime, date
from ummalqura.hijri_date import HijriDate
import json
from werkzeug.utils import secure_filename
from ai import call_chatbot_groq
from flask_migrate import Migrate


UPLOAD_FOLDER = 'static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c0585ef7ad68d55b7fd83abf82d9e93cbd3af7bfb6702710f55c4b16e3fb0a74'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def can_mark_attendance(user, target_pic_id):
    if user.role == "admin":
        return True
    if user.can_mark_attendance and user.pic_id == target_pic_id:
        return True
    
    return False

INITIAL_PASSWORD = "rohis2025"

members = [
    {"email": "muhammad.syathir@gdajogja.sch.id", "name": "Muhammad Syathir", "class": "10-D", "role": "admin"},
    {"email": "aqillah.hasanah@gdajogja.sch.id", "name": "Aqillah Hasanah", "class": "10-C", "role": "admin"},
    {"email": "ghozy.suciawan@gdajogja.sch.id", "name": "Ghozy Suciawan", "class": "10-D", "role": "ketua"},
    {"email": "haidar.nasirodin@gdajogja.sch.id", "name": "Haidar Nasirodin", "class": "10-A", "role": "admin"},
    {"email": "khoirun.istiqomah@gdajogja.sch.id", "name": "Khoirun Istiqomah", "class": "10-C", "role": "admin"},
    {"email": "mufadilla.legisa@gdajogja.sch.id", "name": "Mufadilla Legisa", "class": "10-B", "role": "admin"},
    {"email": "rauf.akmal@gdajogja.sch.id", "name": "Rauf Akmal", "class": "10-A", "role": "admin"},
    {"email": "rifqy.daaris@gdajogja.sch.id", "name": "Rifqy Daaris", "class": "10-A", "role": "admin"},
    {"email": "aiesha.makaila@gdajogja.sch.id", "name": "Aiesha Makaila", "class": "10-D", "role": "member"},
    {"email": "arya.rahadian@gdajogja.sch.id", "name": "Arya Rahadian", "class": "10-B", "role": "member"},
    {"email": "aulia.meilinda@gdajogja.sch.id", "name": "Aulia Meilinda", "class": "10-A", "role": "member"},
    {"email": "devone.nalandra@gdajogja.sch.id", "name": "Devone Nalandra", "class": "10-B", "role": "member"},
    {"email": "dzakya.prasetya@gdajogja.sch.id", "name": "Dzakya Prasetya", "class": "10-A", "role": "member"},
    {"email": "evan.farizqi@gdajogja.sch.id", "name": "Evan Farizqi", "class": "10-B", "role": "member"},
    {"email": "faiq.asyam@gdajogja.sch.id", "name": "Faiq Asyam", "class": "10-A", "role": "member"},
    {"email": "hammam.prasetyo@gdajogja.sch.id", "name": "Hammam Prasetyo", "class": "10-B", "role": "member"},
    {"email": "husein.syamil@gdajogja.sch.id", "name": "Husein Syamil", "class": "10-C", "role": "member"},
    {"email": "irfan.ansari@gdajogja.sch.id", "name": "Irfan Ansari", "class": "10-B", "role": "member"},
    {"email": "kemas.tamada@gdajogja.sch.id", "name": "Kemas Tamada", "class": "10-D", "role": "member"},
    {"email": "muhammad.ismoyo@gdajogja.sch.id", "name": "Muhammad Ismoyo", "class": "10-D", "role": "member"},
    {"email": "nabila.patricia@gdajogja.sch.id", "name": "Nabila Patricia", "class": "10-A", "role": "member"},
    {"email": "naufal.syuja@gdajogja.sch.id", "name": "Naufal Syuja", "class": "10-D", "role": "member"},
    {"email": "tengku.harahap@gdajogja.sch.id", "name": "Tengku Harahap", "class": "10-B", "role": "member"},
    {"email": "zahra.layla@gdajogja.sch.id", "name": "Zahra Layla", "class": "10-D", "role": "member"},
    {"email": "zalfa.zahira@gdajogja.sch.id", "name": "Zalfa Zahira", "class": "10-C", "role": "member"}
]

def seed_members():
    for m in members:
        hashed_pw = bcrypt.generate_password_hash(INITIAL_PASSWORD).decode('utf-8')  
        user = User(
            email=m["email"],
            password=hashed_pw,
            name=m["name"],
            class_name=m["class"],
            role=m["role"],
            must_change_password=True
        )
        db.session.add(user)
    db.session.commit()
    print("✅ All members seeded!")

# ...existing code...
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
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


@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role in ['admin', 'ketua', 'pembina']:
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_member'))
    else:
        return redirect(url_for('login'))

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

@app.route('/create-session', methods=['GET', 'POST'])
@login_required
def create_session():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return "Access denied"
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']

        new_session = Session(name=name, date=date)
        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for('dashboard_admin'))
    return render_template('create_session.html')

from datetime import date

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if not current_user.can_mark_attendance and current_user.role != 'admin':
        abort(403)
    # load members for the current user's pic
    members = User.query.filter_by(pic_id=current_user.pic_id).all()

    # load available sessions and determine selected session
    sessions = Session.query.order_by(Session.date.desc()).all()
    selected_session_id = None
    if request.method == 'POST':
        # session id should come from the form
        session_id_raw = request.form.get('session_id')
        try:
            selected_session_id = int(session_id_raw) if session_id_raw else None
        except (ValueError, TypeError):
            selected_session_id = None

        if not selected_session_id:
            flash('Please select a valid session.', 'error')
            return redirect(url_for('attendance'))

        for member in members:
            status = request.form.get(f"status_{member.id}")

            if not status:
                continue

            record = Attendance.query.filter_by(
                session_id=selected_session_id,
                user_id=member.id
            ).first()

            if not record:
                record = Attendance(
                    session_id=selected_session_id,
                    user_id=member.id,
                    status=status,
                    timestamp=datetime.now()
                )
                db.session.add(record)
            else:
                record.status = status

        db.session.commit()
        flash("Attendance saved successfully", "success")
        return redirect(url_for('attendance', session_id=selected_session_id))

    # GET: determine which session to show (query param or latest)
    if request.args.get('session_id'):
        try:
            selected_session_id = int(request.args.get('session_id'))
        except (ValueError, TypeError):
            selected_session_id = None

    if not selected_session_id and sessions:
        try:
            selected_session_id = sessions[0].id
        except Exception:
            selected_session_id = None

    # load attendance records for the selected session
    records = []
    if selected_session_id:
        records = Attendance.query.filter_by(session_id=selected_session_id).all()

    return render_template(
        'attendance.html',
        members=members,
        sessions=sessions,
        records=records,
        selected_session_id=selected_session_id
    )

@app.route('/pics', methods=['GET', 'POST'])
@login_required
def manage_pics():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash("PIC name cannot be empty", "error")
            return redirect(url_for('manage_pics'))

        existing = Pic.query.filter_by(name=name).first()
        if existing:
            flash("PIC already exists!", "error")
        else:
            new_pic = Pic(name=name)
            db.session.add(new_pic)
            db.session.commit()
            flash(f"PIC '{name}' created!", "success")

        return redirect(url_for('manage_pics'))

    pics = Pic.query.all()
    return render_template('manage_pic.html', pics=pics)


@app.route('/pic/delete/<int:id>', methods=['POST'])
@login_required
def delete_pic(id):
    if current_user.role != 'admin':
        abort(403)

    pic = Pic.query.get_or_404(id)

    for user in pic.members:
        user.pic_id = None
        user.can_mark_attendance = False  # 🔥 IMPORTANT

    db.session.delete(pic)
    db.session.commit()

    flash("PIC deleted and permissions revoked", "success")
    return redirect(url_for('manage_pics'))

@app.route('/attendance-mark', methods=['GET', 'POST'])
@login_required
def attendance_mark():
    if current_user.role not in ['admin', 'ketua', 'pembina']:
        return redirect(url_for('invalid_credential'))
    
    sessions = Session.query.all()
    members = User.query.filter_by(role='member').all()  

    if request.method == 'POST':
        try:
            session_id = int(request.form['session_id'])
            
            from datetime import datetime
            for user in members:
                status = request.form.get(f'status_{user.id}')
                if status in ['present', 'absent', 'excused']: 
                    existing_attendance = Attendance.query.filter_by(
                        session_id=session_id, 
                        user_id=user.id
                    ).first()
                    
                    if existing_attendance:
                        existing_attendance.status = status
                    else:
                        new_attendance = Attendance(
                            session_id=session_id,
                            user_id=user.id,
                            status=status,
                            timestamp=datetime.now()
                        )
                        db.session.add(new_attendance)
            
            db.session.commit()
            flash("Attendance recorded successfully", "success")
            return redirect(url_for('attendance_mark'))
        except (ValueError, TypeError):
            flash("Invalid session selected", "error")
    
    return render_template('attendance_mark.html', sessions=sessions, users=members)

@app.route('/attendance-history')
@login_required
def attendance_history():

    records = db.session.query(
        Attendance,
        Session.name.label('session_name'),
        Session.date.label('session_date')
    ).join(Session, Attendance.session_id == Session.id)\
     .filter(Attendance.user_id == current_user.id).all()

    summary = {
        'present': sum(1 for r, _, _ in records if r.status=='present'),
        'absent': sum(1 for r, _, _ in records if r.status=='absent'),
        'excused': sum(1 for r, _, _ in records if r.status=='excused')
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

    records = db.session.query(
        Attendance,
        Session.name.label('session_name'),
        Session.date.label('session_date')
    ).join(Session, Attendance.session_id == Session.id)\
     .filter(Attendance.user_id == user_id).all()
    
    summary = {
        'present': sum(1 for r, _, _ in records if r.status=='present'),
        'absent': sum(1 for r, _, _ in records if r.status=='absent'),
        'excused': sum(1 for r, _, _ in records if r.status=='excused')
    }
    return render_template('attendance_history_admin_view.html', user=selected_user, records=records, summary=summary)

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
    if not allowed_file(file.filename):
        flash('Invalid file type. Allowed types: png, jpg, jpeg, webp', 'error')
        return redirect(url_for('profile'))
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"user_{current_user.id}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    current_user.profile_picture = filename
    db.session.commit()
    flash('Profile picture updated successfully', 'success')
    return redirect(url_for('profile'))

ISLAMIC_HOLIDAYS = {
    # Muharram
    "01-01": "Islamic New Year (1 Muharram)",
    "01-09": "Day of Tasua",
    "01-10": "Day of Ashura",

    # Rabi' al-Awwal
    "03-12": "Mawlid al-Nabi (Prophet Muhammad's Birthday)",

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
    "09-27": "Laylat al-Qadr (most observed)",
    "09-29": "Laylat al-Qadr (possible)",

    # Shawwal
    "10-01": "Eid al-Fitr",
    "10-02": "Eid al-Fitr (2nd day – some regions)",

    # Dhu al-Qi'dah
    "11-01": "Start of Dhu al-Qi'dah",

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
        return f"{h.day} {h.month_name()} {h.year} H"
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

    # Rohis sessions
    for session in sessions:
        hijri_date = get_hijri_date(session.date)
        calendar_events.append({
            'title': f"{session.name} ({hijri_date})",
            'start': session.date,
            'extendedProps': {
                'type': 'rohis_session'
            }
        })

    # Islamic holidays (FIXED)
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

@app.route('/pic-management', methods=['GET', 'POST'])
@login_required
def pic_management():

    if current_user.role not in ['admin', 'ketua', 'pembina']:
        abort(403)

    pics = Pic.query.all()
    users = User.query.filter_by(role='member').all()

    if request.method == 'POST':
        user_ids = request.form.getlist('user_ids')
        pic_id = request.form.get('pic_id')
        marker_id = request.form.get('marker_id')

        if not user_ids or not pic_id:
            flash("Please select users and a PIC.", "danger")
            return redirect(url_for('pic_management'))

        try:
            user_ids = [int(uid) for uid in user_ids]
            pic_id = int(pic_id)
        except (ValueError, TypeError):
            flash("Invalid input values.", "danger")
            return redirect(url_for('pic_management'))

        try:
            marker_id = int(marker_id) if marker_id else None
        except (ValueError, TypeError):
            marker_id = None

        # Ensure only one user in this pic has marking permission
        User.query.filter_by(pic_id=pic_id, can_mark_attendance=True).update({"can_mark_attendance": False})

        for uid in user_ids:
            user = User.query.get(uid)
            if user:
                user.pic_id = pic_id
                user.can_mark_attendance = True if (marker_id and uid == marker_id) else False
                db.session.add(user)

        db.session.commit()

        flash(f"Assigned {len(user_ids)} members to the PIC.", "success")
        return redirect(url_for('pic_management'))

    return render_template(
        'pic_management.html',
        pics=pics,
        users=users
    )

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        if User.query.count() == 0:
            seed_members()
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port, debug=True)