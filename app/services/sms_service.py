"""
SMS notification service using Twilio.
"""
from typing import Optional
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications via Twilio"""

    def __init__(self, client=None, from_number=None):
        """
        Initialize SMS service

        Args:
            client: Twilio client instance (optional, uses app config if not provided)
            from_number: Twilio phone number (optional, uses app config if not provided)
        """
        self.client = client
        self.from_number = from_number

    def send_sms(self, to_number: str, message: str) -> Optional[str]:
        """
        Send an SMS message

        Args:
            to_number: Recipient phone number in E.164 format
            message: Message text to send

        Returns:
            Message SID if successful, None if failed
        """
        # Check if Twilio is enabled
        if not current_app.config.get('TWILIO_ENABLED', False):
            logger.warning("Twilio is not enabled. SMS not sent.")
            return None

        try:
            from app import client, TWILIO_PHONE_NUMBER

            message_obj = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            logger.info(f"SMS sent successfully to {to_number}. SID: {message_obj.sid}")
            return message_obj.sid

        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return None

    def send_verification_code(self, phone_number: str, code: str) -> bool:
        """
        Send a verification code via SMS

        Args:
            phone_number: Recipient phone number
            code: Verification code to send

        Returns:
            True if successful, False otherwise
        """
        message = f"Your do2done verification code is: {code}"
        sid = self.send_sms(phone_number, message)
        return sid is not None

    def send_task_reminder(self, phone_number: str, task_title: str, due_date: str = None) -> bool:
        """
        Send a task reminder via SMS

        Args:
            phone_number: Recipient phone number
            task_title: Title of the task
            due_date: Optional due date string

        Returns:
            True if successful, False otherwise
        """
        if due_date:
            message = f"Reminder: '{task_title}' is due on {due_date}"
        else:
            message = f"Reminder: Don't forget about '{task_title}'"

        sid = self.send_sms(phone_number, message)
        return sid is not None

    def send_password_reset_code(self, phone_number: str, code: str) -> bool:
        """
        Send a password reset code via SMS

        Args:
            phone_number: Recipient phone number
            code: Reset code to send

        Returns:
            True if successful, False otherwise
        """
        message = f"Your do2done password reset code is: {code}"
        sid = self.send_sms(phone_number, message)
        return sid is not None
