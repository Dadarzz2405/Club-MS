"""
Database Migration: Store Profile Pictures as BLOB

Add this as a new migration file or run manually to update the User model
"""

from app import app, db
from models import User
from flask_migrate import Migrate
import os
import base64

# Step 1: Update models.py - Add this to User model:
"""
class User(db.Model, UserMixin):
    # ... existing fields ...
    
    # Replace the profile_picture String field with:
    profile_picture_data = db.Column(db.LargeBinary, nullable=True)  # Store image as BLOB
    profile_picture_filename = db.Column(db.String(255), default='default.png')  # Store filename for reference
"""

# Step 2: Create migration script
def create_migration():
    """
    Run this to create a new migration
    """
    print("Creating migration for profile pictures...")
    print("\nRun these commands:")
    print("1. flask db migrate -m 'Add profile picture BLOB field'")
    print("2. flask db upgrade")
    print("\nThen run the migration function below")

def migrate_existing_pictures():
    """
    Migrate existing profile pictures from filesystem to database
    """
    with app.app_context():
        users = User.query.all()
        upload_folder = 'static/uploads/profiles'
        
        migrated = 0
        errors = 0
        
        for user in users:
            try:
                # Get current profile picture filename
                filename = user.profile_picture if user.profile_picture else 'default.png'
                filepath = os.path.join(upload_folder, filename)
                
                # Read file and convert to binary
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        image_data = f.read()
                    
                    user.profile_picture_data = image_data
                    user.profile_picture_filename = filename
                    migrated += 1
                    print(f"✓ Migrated {user.name}: {filename}")
                else:
                    print(f"⚠ File not found for {user.name}: {filepath}")
                    
            except Exception as e:
                print(f"✗ Error migrating {user.name}: {e}")
                errors += 1
        
        db.session.commit()
        
        print(f"\n{'='*50}")
        print(f"Migration complete!")
        print(f"Successfully migrated: {migrated}")
        print(f"Errors: {errors}")
        print(f"{'='*50}")

# Step 3: Updated routes for app.py
"""
# Update the upload_pfp route:
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

# Update templates to use new route:
# Change: src="{{ url_for('static', filename='uploads/profiles/' ~ user.profile_picture) }}"
# To: src="{{ url_for('serve_profile_picture', user_id=user.id) }}"
"""

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "migrate":
        migrate_existing_pictures()
    else:
        create_migration()