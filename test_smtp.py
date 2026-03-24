#!/usr/bin/env python3
"""
Direct SMTP connection test for Hotmail/Outlook
This script helps diagnose connection issues without the full scheduler
"""

import os
import sys
import smtplib
import ssl
import socket
from datetime import datetime

def test_smtp_connection():
    """Test SMTP connection directly."""
    
    print("\n" + "=" * 60)
    print("HOTMAIL/OUTLOOK SMTP CONNECTION TEST")
    print("=" * 60 + "\n")
    
    # Get credentials from environment
    email = os.getenv('GITHUB_EMAIL', '').strip()
    password = os.getenv('GITHUB_EMAIL_PASSWORD', '').strip()
    smtp_server = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com').strip()
    smtp_port = int(os.getenv('SMTP_PORT', '465'))
    
    # Validate inputs
    if not email:
        print("✗ Error: GITHUB_EMAIL environment variable not set!")
        print("  Set it with: export GITHUB_EMAIL=your_email@hotmail.com")
        return False
    
    if not password:
        print("✗ Error: GITHUB_EMAIL_PASSWORD environment variable not set!")
        print("  Set it with: export GITHUB_EMAIL_PASSWORD=your_app_password")
        return False
    
    print(f"Email:        {email}")
    print(f"SMTP Server:  {smtp_server}")
    print(f"SMTP Port:    {smtp_port}")
    print(f"Protocol:     {'SSL' if smtp_port == 465 else 'TLS'}")
    print()
    
    # Step 1: Test TCP connection
    print("[STEP 1] Testing TCP connection to server...")
    try:
        socket.create_connection((smtp_server, smtp_port), timeout=10)
        print(f"✓ TCP connection successful")
    except socket.timeout:
        print(f"✗ TCP connection timed out after 10 seconds")
        print("  The server is not responding. Check your internet connection.")
        return False
    except socket.error as e:
        print(f"✗ TCP connection failed: {e}")
        return False
    
    # Step 2: SMTP connection
    print("\n[STEP 2] Connecting to SMTP server...")
    try:
        context = ssl.create_default_context()
        
        if smtp_port == 465:
            print(f"  Initiating SSL connection with 15s timeout...")
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=15)
        else:
            print(f"  Initiating TLS connection with 15s timeout...")
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=15)
            print(f"  Upgrading to TLS...")
            server.starttls(context=context)
        
        print(f"✓ SMTP connection established")
        
        # Step 3: Login
        print("\n[STEP 3] Authenticating...")
        try:
            server.login(email, password)
            print(f"✓ Authentication successful")
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ Authentication failed: {e}")
            print("  Make sure you're using an App Password, not your regular password!")
            print("  Generate one at: https://account.microsoft.com/security-info -> App passwords")
            server.quit()
            return False
        
        # Step 4: Send test email
        print("\n[STEP 4] Sending test email...")
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = f"Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg.attach(MIMEText("This is a test email from the GitHub Email Scheduler.", 'plain'))
            
            print(f"  Sending message...")
            server.sendmail(email, email, msg.as_string())
            print(f"✓ Email sent successfully")
        except smtplib.SMTPException as e:
            print(f"✗ Failed to send email: {e}")
            server.quit()
            return False
        
        # Step 5: Close connection
        print("\n[STEP 5] Closing connection...")
        server.quit()
        print(f"✓ Connection closed")
        
        return True
        
    except socket.timeout:
        print(f"✗ SMTP connection timed out after 15 seconds")
        print("  The server is not responding in time.")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_smtp_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED - Your scheduler should work!")
        print("  Run: python email_scheduler.py")
    else:
        print("✗ TEST FAILED - Fix the issues above and try again")
        print("\nTroubleshooting tips:")
        print("  1. Make sure you're using an App Password (not regular password)")
        print("  2. Generate at: https://account.microsoft.com/security-info")
        print("  3. Check your internet connection")
        print("  4. Try port 587 instead: export SMTP_PORT=587")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)
