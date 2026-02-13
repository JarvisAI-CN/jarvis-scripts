import smtplib
from email.mime.text import MIMEText

def test_gmail():
    sender = "fishel.shuai@gmail.com"
    password = "gtdb rbnu yjrm cqpi"
    receiver = "jarvis-cn-ai@outlook.com"
    
    msg = MIMEText("This is a test email from Jarvis via Gmail Relay.")
    msg['Subject'] = 'Relay Test'
    msg['From'] = sender
    msg['To'] = receiver
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("✅ Gmail SMTP Relay Success!")
    except Exception as e:
        print(f"❌ Gmail SMTP Relay Failed: {e}")

if __name__ == "__main__":
    test_gmail()
