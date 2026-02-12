#!/usr/bin/env python3
"""
Database Seeder for Rohis Management System
Supports both SQLite (dev) and PostgreSQL (production)
"""
import os
import sys
from app import app, db, bcrypt
from models import User

# Default password for all initial accounts
INITIAL_PASSWORD = "rohis2026"

def seed_single_member(email, name, class_name, role):
    """Insert a single member into database"""
    with app.app_context():
        print("\n🌱 Seeding single member...\n")

        try:
            # Ensure tables exist
            db.create_all()

            # Check if user already exists
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"⏭️ User already exists: {email}")
                return

            # Hash password
            hashed_pw = bcrypt.generate_password_hash(
                INITIAL_PASSWORD
            ).decode("utf-8")

            # Create user
            user = User(
                email=email,
                password=hashed_pw,
                name=name,
                class_name=class_name,
                role=role,
                must_change_password=True
            )

            db.session.add(user)
            db.session.commit()

            print("✅ User successfully added!")
            print(f"📧 Email: {email}")
            print(f"🔑 Initial password: {INITIAL_PASSWORD}")
            print("⚠️ Must change password on first login.\n")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error inserting user: {e}")

if __name__ == '__main__':
    seed_single_member(
        'lita.mariana@gdajogja.sch.id', 
        'Lita Mariana', 
        'Supervisor', 
        'pembina'
    )
    seed_single_member(
        'amar.muchaqqi@gdajogja.sch.id', 
        'Amar Muchaqqi', 
        'Supervisor', 
        'pembina'
    )
    seed_single_member(
        'muhammad.hasan@gdajogja.sch.id', 
        'Muhammad Hasan', 
        'Supervisor', 
        'pembina'        
    )
