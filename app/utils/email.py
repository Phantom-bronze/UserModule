"""
Email Utilities
===============

This module provides functions for sending emails including:
- User invitations
- Password reset emails
- Notification emails
- System alerts

Email Provider: SMTP (configurable via settings)
Supported: Gmail, SendGrid, AWS SES, or any SMTP server

Email Templates:
- Invitation emails with unique token links
- Welcome emails
- Account notifications
- System alerts

All emails are sent asynchronously to avoid blocking API requests.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging
from datetime import datetime

from app.config import settings

# ============================================================
# Logger Configuration
# ============================================================
logger = logging.getLogger(__name__)


# ============================================================
# Email Sending Functions
# ============================================================

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.

    This function sends HTML emails with optional plain text fallback.
    It uses the SMTP settings from configuration.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML content of the email
        plain_content: Plain text content (fallback for non-HTML clients)

    Returns:
        bool: True if email sent successfully, False otherwise

    Example:
        >>> success = send_email(
        >>>     to_email="user@example.com",
        >>>     subject="Welcome!",
        >>>     html_content="<h1>Welcome to our platform!</h1>"
        >>> )
        >>> if success:
        >>>     print("Email sent successfully")
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Add plain text part (fallback)
        if plain_content:
            text_part = MIMEText(plain_content, "plain")
            message.attach(text_part)

        # Add HTML part
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Connect to SMTP server and send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()

            # Login if credentials are provided
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

            # Send email
            server.send_message(message)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


# ============================================================
# Invitation Email Templates
# ============================================================

def send_invitation_email(
    to_email: str,
    inviter_name: str,
    company_name: str,
    role: str,
    invitation_url: str
) -> bool:
    """
    Send an invitation email to a new user.

    This email invites the user to join the platform and includes
    a unique invitation link.

    Args:
        to_email: Email address of the invitee
        inviter_name: Name of the person who sent the invitation
        company_name: Name of the company they're being invited to
        role: Role they will have (admin or user)
        invitation_url: Unique invitation URL with token

    Returns:
        bool: True if email sent successfully, False otherwise

    Example:
        >>> send_invitation_email(
        >>>     to_email="newuser@example.com",
        >>>     inviter_name="John Admin",
        >>>     company_name="Acme Corp",
        >>>     role="user",
        >>>     invitation_url="https://app.example.com/accept?token=abc123"
        >>> )
    """
    subject = f"You've been invited to join {company_name} on Simple Digital Signage"

    # HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
            .role-badge {{
                display: inline-block;
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 3px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>You're Invited!</h1>
            </div>
            <div class="content">
                <p>Hi there,</p>
                <p><strong>{inviter_name}</strong> has invited you to join <strong>{company_name}</strong> on Simple Digital Signage.</p>
                <p>You will be joining as: <span class="role-badge">{role.upper()}</span></p>
                <p>Simple Digital Signage allows you to manage and display digital content on Smart TVs, perfect for digital signage solutions.</p>
                <p>Click the button below to accept the invitation and set up your account:</p>
                <p style="text-align: center;">
                    <a href="{invitation_url}" class="button">Accept Invitation</a>
                </p>
                <p><small>Or copy and paste this link into your browser:</small><br>
                <code>{invitation_url}</code></p>
                <p><strong>Note:</strong> This invitation link will expire in 72 hours.</p>
                <p>If you didn't expect this invitation, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.utcnow().year} Simple Digital Signage. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Plain text fallback
    plain_content = f"""
    You're Invited!

    Hi there,

    {inviter_name} has invited you to join {company_name} on Simple Digital Signage.

    You will be joining as: {role.upper()}

    Click the link below to accept the invitation and set up your account:
    {invitation_url}

    Note: This invitation link will expire in 72 hours.

    If you didn't expect this invitation, you can safely ignore this email.

    © {datetime.utcnow().year} Simple Digital Signage. All rights reserved.
    """

    return send_email(to_email, subject, html_content, plain_content)


# ============================================================
# Welcome Email
# ============================================================

def send_welcome_email(
    to_email: str,
    full_name: str,
    company_name: str,
    role: str
) -> bool:
    """
    Send a welcome email to a newly registered user.

    Args:
        to_email: User's email address
        full_name: User's full name
        company_name: Company name
        role: User's role

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = f"Welcome to Simple Digital Signage, {full_name}!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Simple Digital Signage!</h1>
            </div>
            <div class="content">
                <p>Hi {full_name},</p>
                <p>Welcome to <strong>{company_name}</strong> on Simple Digital Signage!</p>
                <p>Your account has been successfully created as a <strong>{role}</strong>.</p>
                <h3>Getting Started:</h3>
                <ul>
                    <li>Connect your Google Drive to import content</li>
                    <li>Create playlists with your images and videos</li>
                    <li>Link your Smart TVs using the mobile app</li>
                    <li>Display your content on any connected TV</li>
                </ul>
                <p>If you have any questions, feel free to reach out to your administrator.</p>
                <p>Best regards,<br>The Simple Digital Signage Team</p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.utcnow().year} Simple Digital Signage. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_content = f"""
    Welcome to Simple Digital Signage!

    Hi {full_name},

    Welcome to {company_name} on Simple Digital Signage!

    Your account has been successfully created as a {role}.

    Getting Started:
    - Connect your Google Drive to import content
    - Create playlists with your images and videos
    - Link your Smart TVs using the mobile app
    - Display your content on any connected TV

    If you have any questions, feel free to reach out to your administrator.

    Best regards,
    The Simple Digital Signage Team

    © {datetime.utcnow().year} Simple Digital Signage. All rights reserved.
    """

    return send_email(to_email, subject, html_content, plain_content)


# ============================================================
# Device Linked Notification
# ============================================================

def send_device_linked_email(
    to_email: str,
    full_name: str,
    device_name: str,
    device_code: str
) -> bool:
    """
    Send notification email when a new device is linked.

    Args:
        to_email: User's email address
        full_name: User's full name
        device_name: Name of the linked device
        device_code: Device pairing code used

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = "New Device Linked to Your Account"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h2>Device Linked Successfully</h2>
                <p>Hi {full_name},</p>
                <p>A new device has been linked to your Simple Digital Signage account:</p>
                <p><strong>Device Name:</strong> {device_name}<br>
                <strong>Pairing Code:</strong> {device_code}<br>
                <strong>Linked At:</strong> {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</p>
                <p>If you didn't link this device, please contact your administrator immediately.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_content = f"""
    Device Linked Successfully

    Hi {full_name},

    A new device has been linked to your Simple Digital Signage account:

    Device Name: {device_name}
    Pairing Code: {device_code}
    Linked At: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

    If you didn't link this device, please contact your administrator immediately.
    """

    return send_email(to_email, subject, html_content, plain_content)


# ============================================================
# Test Email Function
# ============================================================

def send_test_email(to_email: str) -> bool:
    """
    Send a test email to verify SMTP configuration.

    Args:
        to_email: Email address to send test to

    Returns:
        bool: True if email sent successfully, False otherwise

    Example:
        >>> send_test_email("admin@example.com")
        True
    """
    subject = "Test Email from Simple Digital Signage"

    html_content = """
    <!DOCTYPE html>
    <html>
    <body>
        <h2>Email Configuration Test</h2>
        <p>This is a test email from Simple Digital Signage backend.</p>
        <p>If you're reading this, your email configuration is working correctly!</p>
    </body>
    </html>
    """

    plain_content = """
    Email Configuration Test

    This is a test email from Simple Digital Signage backend.

    If you're reading this, your email configuration is working correctly!
    """

    return send_email(to_email, subject, html_content, plain_content)
