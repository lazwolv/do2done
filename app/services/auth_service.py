"""
Authentication and user management service.
"""
import random
from datetime import datetime, timedelta
from typing import Optional, Tuple
from flask import current_app
from app import db
from app.models.users import User, VerificationCode


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def create_verification_code(phone_number: str, code: str = None) -> VerificationCode:
        """
        Create and save a verification code for a phone number

        Args:
            phone_number: The phone number to verify
            code: Optional specific code, or generates a random one

        Returns:
            VerificationCode instance
        """
        if code is None:
            code = AuthService.generate_verification_code(
                current_app.config.get('VERIFICATION_CODE_LENGTH', 6)
            )

        expiry_minutes = current_app.config.get('VERIFICATION_CODE_EXPIRY_MINUTES', 10)
        verification = VerificationCode(
            phone_number=phone_number,
            code=code,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=expiry_minutes)
        )
        db.session.add(verification)
        db.session.commit()
        return verification

    @staticmethod
    def verify_code(phone_number: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify a code for a phone number

        Args:
            phone_number: The phone number
            code: The verification code to check

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        verification = VerificationCode.query.filter_by(
            phone_number=phone_number,
            code=code
        ).order_by(VerificationCode.created_at.desc()).first()

        if not verification:
            return False, "Invalid verification code"

        if verification.is_expired:
            return False, "Verification code has expired"

        return True, None

    @staticmethod
    def create_user(first_name: str, last_name: str, phone_number: str, password: str) -> User:
        """
        Create a new user

        Args:
            first_name: User's first name
            last_name: User's last name
            phone_number: User's phone number
            password: User's password (will be hashed)

        Returns:
            User instance
        """
        user = User(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            verification_attempts=0,
            verified=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_phone(phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        return User.query.filter_by(phone_number=phone_number).first()

    @staticmethod
    def verify_user(user: User) -> None:
        """Mark a user as verified"""
        user.verified = True
        user.verification_code = None
        user.verification_attempts = 0
        db.session.commit()

    @staticmethod
    def can_attempt_verification(user: User) -> Tuple[bool, Optional[str]]:
        """
        Check if user can attempt verification

        Returns:
            Tuple of (can_attempt: bool, error_message: Optional[str])
        """
        max_attempts = current_app.config.get('MAX_VERIFICATION_ATTEMPTS', 3)
        lockout_minutes = current_app.config.get('VERIFICATION_LOCKOUT_MINUTES', 15)

        if user.verification_attempts >= max_attempts:
            if user.last_verification_attempt:
                lockout_until = user.last_verification_attempt + timedelta(minutes=lockout_minutes)
                if datetime.now() < lockout_until:
                    minutes_left = int((lockout_until - datetime.now()).total_seconds() / 60)
                    return False, f"Too many attempts. Please wait {minutes_left} minutes."

            # Reset attempts after lockout period
            user.verification_attempts = 0
            db.session.commit()

        return True, None

    @staticmethod
    def record_verification_attempt(user: User, success: bool) -> None:
        """Record a verification attempt"""
        if not success:
            user.verification_attempts += 1
        user.last_verification_attempt = datetime.now()
        db.session.commit()

    @staticmethod
    def change_password(user: User, new_password: str) -> None:
        """Change user's password"""
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def update_profile(user: User, first_name: str, last_name: str, phone_number: str) -> None:
        """Update user profile"""
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        db.session.commit()

    @staticmethod
    def delete_user(user: User) -> None:
        """Delete a user account"""
        db.session.delete(user)
        db.session.commit()
