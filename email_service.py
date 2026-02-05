"""
Email service for sending jadwal piket reminders.
Uses Resend API (free tier: 100 emails/day, 3,000/month)
No 2FA or app passwords needed - just an API key!
"""

import os
import requests
from datetime import datetime
from typing import List, Dict
import json


class EmailService:
    """Handle email sending for piket reminders using Resend API"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
        self.sender_name = os.environ.get('SENDER_NAME', 'Rohis Attendance System')
        self.api_url = 'https://api.resend.com/emails'
        
        # Validate configuration
        if not self.api_key:
            raise ValueError(
                "RESEND_API_KEY environment variable is not set. "
                "Get your API key from https://resend.com/api-keys"
            )
    
    def send_piket_reminder(
        self, 
        recipients: List[str], 
        day_name: str,
        date_str: str,
        additional_info: str = ""
    ) -> Dict[str, any]:
        """
        Send piket reminder email to a list of recipients using Resend API.
        
        Args:
            recipients: List of email addresses
            day_name: Name of the day (e.g., "Monday")
            date_str: Formatted date string (e.g., "05 February 2026")
            additional_info: Optional additional message
            
        Returns:
            Dict with 'success' (bool), 'message' (str), 'failed_emails' (list)
        """
        if not recipients:
            return {
                'success': False,
                'message': 'No recipients provided',
                'failed_emails': []
            }
        
        # Email content
        subject = f"🧹 Reminder: Jadwal Piket {day_name}"
        
        html_body = self._generate_email_html(
            day_name=day_name,
            date_str=date_str,
            additional_info=additional_info
        )
        
        text_body = self._generate_email_text(
            day_name=day_name,
            date_str=date_str,
            additional_info=additional_info
        )
        
        # Send emails using Resend API
        failed_emails = []
        successful_count = 0
        
        for recipient in recipients:
            try:
                # Prepare email payload
                payload = {
                    "from": f"{self.sender_name} <{self.sender_email}>",
                    "to": [recipient],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body
                }
                
                # Send via Resend API
                response = requests.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    successful_count += 1
                else:
                    print(f"Failed to send to {recipient}: {response.status_code} - {response.text}")
                    failed_emails.append(recipient)
                    
            except Exception as e:
                print(f"Error sending email to {recipient}: {e}")
                failed_emails.append(recipient)
        
        # Return results
        if failed_emails:
            return {
                'success': True,
                'message': f'Sent {successful_count}/{len(recipients)} emails. Some failed.',
                'failed_emails': failed_emails
            }
        else:
            return {
                'success': True,
                'message': f'Successfully sent {successful_count} emails',
                'failed_emails': []
            }
    
    def _generate_email_html(self, day_name: str, date_str: str, additional_info: str) -> str:
        """Generate HTML email body"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Inter', Arial, sans-serif; background-color: #f8fafc;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #059669, #047857); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: 800;">🧹 Jadwal Piket Reminder</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.95;">Rohis Attendance System</p>
                </div>
                
                <!-- Content -->
                <div style="background: white; padding: 40px 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <div style="display: inline-block; background: #dcfce7; color: #065f46; padding: 12px 24px; border-radius: 8px; font-weight: 700; font-size: 18px;">
                            {day_name} • {date_str}
                        </div>
                    </div>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #1e293b; margin-bottom: 20px;">
                        Assalamu'alaikum,
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #1e293b; margin-bottom: 20px;">
                        This is a friendly reminder that <strong>you are scheduled for piket duty today ({day_name})</strong>.
                    </p>
                    
                    <div style="background: #f1f5f9; border-left: 4px solid #059669; padding: 20px; margin: 25px 0; border-radius: 8px;">
                        <h3 style="margin: 0 0 15px 0; color: #059669; font-size: 18px;">📋 Your Responsibilities:</h3>
                        <ul style="margin: 0; padding-left: 20px; color: #475569; line-height: 1.8;">
                            <li>Arrive 10 minutes before the scheduled time</li>
                            <li>Clean the designated area thoroughly</li>
                            <li>Ensure all tasks are completed before leaving</li>
                            <li>Report any issues to your PIC or admin</li>
                        </ul>
                    </div>
                    
                    {f'<div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 25px 0; border-radius: 8px;"><p style="margin: 0; color: #92400e; font-size: 15px;"><strong>📢 Additional Info:</strong><br>{additional_info}</p></div>' if additional_info else ''}
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #1e293b; margin-top: 25px;">
                        JazakAllah khair for your cooperation! 🙏
                    </p>
                    
                    <p style="font-size: 14px; color: #64748b; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                        <em>This is an automated reminder from Rohis Attendance System. If you have any questions, please contact your admin.</em>
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; padding: 20px; color: #94a3b8; font-size: 13px;">
                    <p style="margin: 0;">Rohis Management System</p>
                    <p style="margin: 5px 0 0 0;">GDA Jogja</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_email_text(self, day_name: str, date_str: str, additional_info: str) -> str:
        """Generate plain text email body (fallback)"""
        text = f"""
JADWAL PIKET REMINDER
Rohis Attendance System

{day_name} • {date_str}

Assalamu'alaikum,

This is a friendly reminder that you are scheduled for piket duty today ({day_name}).

YOUR RESPONSIBILITIES:
- Arrive 10 minutes before the scheduled time
- Clean the designated area thoroughly
- Ensure all tasks are completed before leaving
- Report any issues to your PIC or admin
"""
        
        if additional_info:
            text += f"\nADDITIONAL INFO:\n{additional_info}\n"
        
        text += """
JazakAllah khair for your cooperation!

---
This is an automated reminder from Rohis Attendance System.
If you have any questions, please contact your admin.

Rohis Management System
GDA Jogja
"""
        return text.strip()


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get or create the email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service