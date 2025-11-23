"""
Email service for sending verification codes
"""
import smtplib
import os
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


def generate_verification_code():
    """Generate a 6-digit verification code"""
    return str(random.randint(100000, 999999))


def send_verification_email(to_email: str, verification_code: str, user_name: str = None):
    """
    Send verification code email using Gmail SMTP
    
    Args:
        to_email: Recipient email address
        verification_code: 6-digit verification code
        user_name: Optional user name for personalization
    """
    # Get email credentials from environment
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        raise ValueError("SMTP_EMAIL and SMTP_PASSWORD must be set in .env file")
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Verify Your ATS Scanner Account'
    msg['From'] = f'ATS Scanner <{smtp_email}>'
    msg['To'] = to_email
    
    # Create email body
    greeting = f"Hi {user_name}," if user_name else "Hi there,"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background-color: #FAF9F6;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                color: #312E81;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .code-box {{
                background-color: white;
                border: 2px solid #DAA520;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 30px 0;
            }}
            .code {{
                font-size: 36px;
                font-weight: bold;
                color: #1E3A8A;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 12px;
                color: #666;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #DAA520;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🎯 ATS Scanner</div>
                <p style="color: #666;">Welcome to ATS Scanner!</p>
            </div>
            
            <p>{greeting}</p>
            
            <p>Thank you for signing up! To complete your registration and start optimizing your resume, please verify your email address.</p>
            
            <div class="code-box">
                <p style="margin: 0 0 10px 0; color: #666;">Your verification code is:</p>
                <div class="code">{verification_code}</div>
            </div>
            
            <p>Enter this code on the verification page to activate your account.</p>
            
            <p style="color: #666; font-size: 14px;">
                <strong>Note:</strong> This code will expire in 15 minutes for security reasons.
            </p>
            
            <p>If you didn't create an account with ATS Scanner, you can safely ignore this email.</p>
            
            <div class="footer">
                <p>© 2025 ATS Scanner. All rights reserved.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text = f"""
    {greeting}
    
    Thank you for signing up for ATS Scanner!
    
    Your verification code is: {verification_code}
    
    Enter this code on the verification page to activate your account.
    
    This code will expire in 15 minutes.
    
    If you didn't create an account, you can safely ignore this email.
    
    © 2025 ATS Scanner
    """
    
    # Attach both versions
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    # Send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
            print(f"✅ Verification email sent to {to_email}")
            return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        raise Exception(f"Failed to send verification email: {str(e)}")


def send_welcome_email(to_email: str, user_name: str = None):
    """Send welcome email after successful verification"""
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        return
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Welcome to ATS Scanner! 🎉'
    msg['From'] = f'ATS Scanner <{smtp_email}>'
    msg['To'] = to_email
    
    greeting = f"Hi {user_name}," if user_name else "Hi there,"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background-color: #FAF9F6;
                border-radius: 10px;
                padding: 30px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                color: #312E81;
                font-size: 28px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🎯 ATS Scanner</div>
            </div>
            
            <p>{greeting}</p>
            
            <p>Your email has been verified successfully! Welcome to ATS Scanner. 🎉</p>
            
            <p>You can now:</p>
            <ul>
                <li>Upload your resume and analyze it against job descriptions</li>
                <li>Get AI-powered feedback and suggestions</li>
                <li>Save your scan history for future reference</li>
                <li>Track your progress over time</li>
            </ul>
            
            <p>Ready to optimize your resume? <a href="http://localhost:8080/index.html" style="color: #DAA520;">Start scanning now!</a></p>
            
            <p>Best regards,<br>The ATS Scanner Team</p>
        </div>
    </body>
    </html>
    """
    
    part = MIMEText(html, 'html')
    msg.attach(part)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
            print(f"✅ Welcome email sent to {to_email}")
    except Exception as e:
        print(f"⚠️ Failed to send welcome email: {str(e)}")
