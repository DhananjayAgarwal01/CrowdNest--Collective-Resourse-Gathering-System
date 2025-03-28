from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class HTMLEmailTemplates:
    # Brand colors
    PRIMARY_COLOR = "#4A90E2"  # Blue
    SECONDARY_COLOR = "#F5F7FA"  # Light Gray
    TEXT_COLOR = "#333333"  # Dark Gray
    ACCENT_COLOR = "#2ECC71"  # Green

    @staticmethod
    def _get_base_template(content):
        return f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>CrowdNest</title>
        </head>
        <body style="margin: 0; padding: 0;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f4f4f4;">
                <tr>
                    <td align="center" style="padding: 20px 0;">
                        <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <tr>
                                <td align="center" bgcolor="{HTMLEmailTemplates.PRIMARY_COLOR}" style="padding: 20px;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-family: Arial, sans-serif;">CrowdNest</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 30px; font-family: Arial, sans-serif;">
                                    {content}
                                </td>
                            </tr>
                            <tr>
                                <td align="center" bgcolor="{HTMLEmailTemplates.SECONDARY_COLOR}" style="padding: 20px;">
                                    <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; margin: 0; font-size: 14px; font-family: Arial, sans-serif;">CrowdNest Community - Connecting People Through Giving</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    @staticmethod
    def request_donation_template(requester_name, donator_name, donation_item, additional_message=None):
        content = f"""
        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">Dear {donator_name},</p>
        
        <div style="background-color: {HTMLEmailTemplates.SECONDARY_COLOR}; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; margin: 0;">I hope this email finds you well. My name is {requester_name}, and I am reaching out regarding the {donation_item} you have listed on CrowdNest.</p>
        </div>
        """

        if additional_message:
            content += f"""
            <div style="background-color: #FFF8E1; padding: 15px; border-left: 4px solid #FFC107; margin: 20px 0;">
                <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; margin: 0;"><strong>Additional Context:</strong> {additional_message}</p>
            </div>
            """

        content += f"""
        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">I would greatly appreciate your consideration in donating this item. If you are willing to help, please respond to this email, and we can discuss the details of the donation.</p>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">Thank you for your kindness and support.</p>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">
            Best regards,<br>
            {requester_name}<br>
            <span style="color: {HTMLEmailTemplates.PRIMARY_COLOR};">CrowdNest Community</span>
        </p>
        """

        return HTMLEmailTemplates._get_base_template(content)

    @staticmethod
    def donation_confirmation_template(donator_name, requester_name, donation_item):
        content = f"""
        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">Dear {requester_name},</p>

        <div style="background-color: {HTMLEmailTemplates.ACCENT_COLOR}; color: white; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="margin: 0;">I am pleased to confirm that I would like to donate the {donation_item} to you through the CrowdNest platform.</p>
        </div>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">Let's discuss the logistics of the donation. Please reply to this email with your preferred method of collection or delivery.</p>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">
            Best regards,<br>
            {donator_name}<br>
            <span style="color: {HTMLEmailTemplates.PRIMARY_COLOR};">CrowdNest Community</span>
        </p>
        """

        return HTMLEmailTemplates._get_base_template(content)

    @staticmethod
    def donation_received_template(donator_name, requester_name, donation_item):
        content = f"""
        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">Dear {donator_name},</p>

        <div style="background-color: {HTMLEmailTemplates.SECONDARY_COLOR}; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; margin: 0;">I wanted to express my heartfelt gratitude for donating the {donation_item}. Your generosity has made a significant difference in my life.</p>
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <p style="color: {HTMLEmailTemplates.PRIMARY_COLOR}; font-size: 18px; font-weight: bold;">Thank you for being a part of the CrowdNest community and helping those in need.</p>
        </div>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">
            Warmest regards,<br>
            {requester_name}<br>
            <span style="color: {HTMLEmailTemplates.PRIMARY_COLOR};">CrowdNest Community</span>
        </p>
        """

        return HTMLEmailTemplates._get_base_template(content)

    @staticmethod
    def verification_email_template(user_name, verification_link):
        content = f"""
        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">Dear {user_name},</p>

        <div style="background-color: {HTMLEmailTemplates.SECONDARY_COLOR}; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; margin: 0;">Thank you for joining CrowdNest! To get started, please verify your email address by clicking the button below.</p>
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_link}" style="background-color: {HTMLEmailTemplates.ACCENT_COLOR}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Verify Email Address</a>
        </div>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 14px; line-height: 1.6; margin-top: 20px;">
            If the button doesn't work, you can copy and paste this link into your browser:<br>
            <span style="color: {HTMLEmailTemplates.PRIMARY_COLOR};">{verification_link}</span>
        </p>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 14px; line-height: 1.6; margin-top: 20px;">
            This verification link will expire in 24 hours. If you didn't create an account with CrowdNest, please ignore this email.
        </p>

        <p style="color: {HTMLEmailTemplates.TEXT_COLOR}; font-size: 16px; line-height: 1.6;">
            Best regards,<br>
            <span style="color: {HTMLEmailTemplates.PRIMARY_COLOR};">The CrowdNest Team</span>
        </p>
        """

        return HTMLEmailTemplates._get_base_template(content)

    @staticmethod
    def create_mime_message(subject, html_content, from_email, to_email):
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = from_email
        message['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        return message