from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
import os 
import logging
from config import EMAIL_BODY, EMAIL_SUBJECT, RECEIVER_EMAIL

# ==================== Function 4: Send email ====================
# ================================================================
# Email functionality 

def send_email_notification():
    sender_email = os.environ.get('SENDER_EMAIL')
    receiver_email = RECEIVER_EMAIL
    password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not password:
        logging.error("Email credentials are not set in environment variables.")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = EMAIL_SUBJECT

    # Add body to the email
    message.attach(MIMEText(EMAIL_BODY, "plain"))

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
