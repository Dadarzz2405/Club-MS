import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from email_service import get_email_service


def test_mailjet_connection():
    print("=" * 60)
    print("MAILJET EMAIL SERVICE TEST")
    print("=" * 60)
    print()

    # Check environment variables
    print("1. Checking environment variables...")
    api_key = os.environ.get('MAILJET_API_KEY')
    api_secret = os.environ.get('MAILJET_API_SECRET')
    sender_email = os.environ.get('SENDER_EMAIL')

    if not api_key:
        print("❌ MAILJET_API_KEY not found in environment")
        return False
    else:
        print(f"✅ MAILJET_API_KEY: {api_key[:6]}...")

    if not api_secret:
        print("❌ MAILJET_API_SECRET not found in environment")
        return False
    else:
        print(f"✅ MAILJET_API_SECRET: {api_secret[:6]}...")

    if not sender_email:
        print("⚠️ SENDER_EMAIL not set")
    else:
        print(f"✅ SENDER_EMAIL: {sender_email}")

    print()

    print("2. Initializing email service...")
    try:
        email_service = get_email_service()
        print("✅ Email service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

    print()
    print("3. Sending test email...")

    test_email = input("Enter your email address for testing: ").strip()

    if not test_email or "@" not in test_email:
        print("❌ Invalid email address")
        return False

    try:
        result = email_service.send_piket_reminder(
            recipients=[test_email],
            day_name="Monday",
            date_str="05 February 2026",
            additional_info="⚠️ This is a TEST email from Mailjet verification."
        )

        print(result["message"])
        return result["success"]

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def test_multiple_recipients():
    recipients = []
    x = input("How many emails do you want to send to? ").strip()
    try:
        num_emails = int(x)
    except ValueError:
        print("❌ Invalid number of emails")
        return

    for i in range(num_emails):
        email = input(f"Enter email address #{i+1}: ").strip()
        if email and "@" in email:
            recipients.append(email)
        else:
            print("Invalid email address, skipping.")
    print(f"Sending email to {len(recipients)} recipients...")

    try:
        email_service = get_email_service()

        result = email_service.send_piket_reminder(
            recipients=recipients,
            day_name="Monday",
            date_str="05 February 2026",
            additional_info="Multi-recipient Mailjet test email."
        )

        print("Result:", result["message"])

        if result.get("failed_emails"):
            print("Failed emails:", result["failed_emails"])

    except Exception as e:
        print("Error:", e)

def select_opt():
    opt = input("Select test to run (1=Single Recipient, 2=Multiple Recipients): ").strip()
    if opt == "1":
        test_mailjet_connection()
    elif opt == "2":
        test_multiple_recipients()
    else:
        print("Invalid option selected.")

if __name__ == "__main__":
    print("\n🧪 Mailjet Email Service Test\n")
    select_opt()
