from app import app, db, bcrypt
from models import User

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
    {"email": "zalfa.zahira@gdajogja.sch.id", "name": "Zalfa Zahira", "class": "10-C", "role": "member"},
]

def seed_members():
    with app.app_context():
        db.create_all()

        for m in members:
            existing = User.query.filter_by(email=m["email"]).first()
            if existing:
                print(f"Skipped (already exists): {m['email']}")
                continue

            hashed_pw = bcrypt.generate_password_hash(
                INITIAL_PASSWORD
            ).decode("utf-8")

            user = User(
                email=m["email"],
                password=hashed_pw,
                name=m["name"],
                class_name=m["class"],
                role=m["role"],
                must_change_password=True
            )

            db.session.add(user)
            print(f"Added: {m['email']}")

        db.session.commit()

    print("✅ Seeding completed safely.")

if __name__ == "__main__":
    seed_members()
