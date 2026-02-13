#!/usr/bin/env python3
"""
Gmail Connectivity Test Script
Tests IMAP connection to read emails and SMTP connection to send emails
"""

import imaplib
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import sys
from datetime import datetime
import email
from email.header import decode_header

# Gmail credentials
EMAIL = "fishel.shuai@gmail.com"
PASSWORD = "gtdb rbnu yjrm cqpi"  # App password

def decode_email_header(header):
    """Decode email header if it's encoded"""
    if header is None:
        return ""
    
    decoded_parts = decode_header(header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding if encoding else 'utf-8', errors='replace'))
        else:
            result.append(str(part))
    return ''.join(result)

def test_imap_connection():
    """Test IMAP connection and fetch recent emails"""
    print("\n" + "="*60)
    print("Testing IMAP connection...")
    print("="*60)
    
    try:
        # Connect to Gmail IMAP server
        print(f"Connecting to imap.gmail.com:993...")
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        
        # Login
        print(f"Logging in as {EMAIL}...")
        mail.login(EMAIL, PASSWORD)
        print("✓ Successfully connected and logged in via IMAP")
        
        # Select INBOX
        mail.select('INBOX')
        
        # Fetch the 3 most recent emails
        print("\nFetching the 3 most recent emails...")
        typ, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        
        total_emails = len(mail_ids)
        print(f"Total emails in INBOX: {total_emails}")
        
        # Get the last 3 email IDs
        recent_ids = mail_ids[-3:] if len(mail_ids) >= 3 else mail_ids
        
        emails = []
        for i, email_id in enumerate(reversed(recent_ids), 1):
            typ, data = mail.fetch(email_id, '(RFC822)')
            raw_email = data[0][1]
            
            # Parse email headers
            email_message = email.message_from_bytes(raw_email)
            subject = decode_email_header(email_message['Subject'])
            sender = decode_email_header(email_message['From'])
            
            emails.append({
                'id': i,
                'subject': subject,
                'sender': sender
            })
        
        mail.close()
        mail.logout()
        
        return True, emails
        
    except Exception as e:
        error_msg = f"IMAP connection failed: {str(e)}"
        print(f"✗ {error_msg}")
        return False, error_msg

def test_smtp_connection():
    """Test SMTP connection and send a test email"""
    print("\n" + "="*60)
    print("Testing SMTP connection...")
    print("="*60)
    
    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = EMAIL
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = f"Gmail Connectivity Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""This is an automated test email from the Gmail connectivity test script.

Test Details:
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- From: {EMAIL}
- To: {EMAIL}

If you receive this email, it means:
✓ SMTP connection to smtp.gmail.com:465 (SSL) is working
✓ Authentication was successful
✓ Email sending functionality is working correctly

Test completed successfully!
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP server with SSL
        print(f"Connecting to smtp.gmail.com:465 (SSL)...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            print(f"Logging in as {EMAIL}...")
            server.login(EMAIL, PASSWORD)
            print("✓ Successfully connected and logged in via SMTP")
            
            # Send the email
            print(f"Sending test email to {EMAIL}...")
            text = msg.as_string()
            server.sendmail(EMAIL, EMAIL, text)
            print("✓ Test email sent successfully!")
            
        return True, "Test email sent successfully"
        
    except Exception as e:
        error_msg = f"SMTP connection or sending failed: {str(e)}"
        print(f"✗ {error_msg}")
        return False, error_msg

def main():
    """Main test function"""
    print("="*60)
    print("Gmail Connectivity Test")
    print("="*60)
    print(f"Target Email: {EMAIL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test IMAP connection (reading emails)
    imap_success, imap_result = test_imap_connection()
    
    # Test SMTP connection (sending email)
    smtp_success, smtp_result = test_smtp_connection()
    
    # Print email list if IMAP was successful
    if imap_success:
        print("\n" + "="*60)
        print("Recent Emails (Top 3)")
        print("="*60)
        for email_info in imap_result:
            print(f"\n{email_info['id']}. Subject: {email_info['subject']}")
            print(f"   From: {email_info['sender']}")
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"IMAP Connection (Reading): {'✓ PASS' if imap_success else '✗ FAIL'}")
    if not imap_success:
        print(f"  Error: {imap_result}")
    print(f"SMTP Connection (Sending): {'✓ PASS' if smtp_success else '✗ FAIL'}")
    if not smtp_success:
        print(f"  Error: {smtp_result}")
    print("="*60)
    
    # Return exit code
    return 0 if (imap_success and smtp_success) else 1

if __name__ == "__main__":
    sys.exit(main())
