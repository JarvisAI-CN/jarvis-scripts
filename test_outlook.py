import smtplib
from email.mime.text import MIMEText

def test_outlook():
    sender = "jarvis-cn-ai@outlook.com"
    password = "cqgsgyomulsfjmfs"
    receiver = "fishel.shuai@gmail.com"
    
    msg = MIMEText("This is a test email from Jarvis via Outlook Relay.")
    msg['Subject'] = 'Outlook Relay Test'
    msg['From'] = sender
    msg['To'] = receiver
    
    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("✅ Outlook SMTP Relay Success!")
    except Exception as e:
        print(f"❌ Outlook SMTP Relay Failed: {e}")

if __name__ == "__main__":
    test_outlook()
