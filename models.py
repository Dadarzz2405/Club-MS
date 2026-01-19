from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False) 
    must_change_password = db.Column(db.Boolean, default=True)  # Force change
    class_name = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255), default='default.png')
    pic_id = db.Column(db.Integer, db.ForeignKey('pic.id', name='fk_user_pic'), nullable=True)
    can_mark_attendance = db.Column(db.Boolean, default=False)  # New field
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    date = db.Column(db.String(50))
    pic_id = db.Column(db.Integer, db.ForeignKey('pic.id'))
    is_locked = db.Column(db.Boolean, default=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_type = db.Column(db.String(50), default='regular', nullable=False)
    
    session = db.relationship('Session', backref='attendances')
    user = db.relationship('User', backref='attendances')

    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='unique_session_user'),
    )

class Pic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    members = db.relationship('User', backref='pic', lazy=True)
