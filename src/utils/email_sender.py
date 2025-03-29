import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .html_email_templates import HTMLEmailTemplates

def send_email(to_email, subject, body, from_name='CrowdNest', from_email=None):
    """
    Send an email using SMTP
    
    :param to_email: Recipient email address
    :param subject: Email subject
    :param body: Email body
    :param from_name: Sender name (optional)
    :param from_email: Sender email (optional)
    :return: Boolean indicating email sending success
    """
    try:
        # Load SMTP configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Validate SMTP configuration
        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            print("SMTP configuration is incomplete")
            return False
        
        # Use default from_email if not provided
        from_email = from_email or smtp_username
        
        # Create HTML email content
        html_content = HTMLEmailTemplates.create_generic_email_template(
            title=subject,
            message=body,
            sender_name=from_name
        )
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"Email sent successfully to {to_email}")
        return True
    
    except smtplib.SMTPException as smtp_err:
        print(f"SMTP Error sending email: {smtp_err}")
        return False
    
    except Exception as e:
        print(f"Unexpected error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False
