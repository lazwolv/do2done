"""
Flask-WTF Forms for do2done application.
Provides form validation and CSRF protection.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from flask_babel import lazy_gettext as _
import phonenumbers


def validate_phone_number(form, field):
    """Custom validator for phone numbers"""
    try:
        # Remove all non-digit characters
        phone = ''.join(filter(str.isdigit, field.data))

        # Check if it's 10 digits (US format)
        if len(phone) != 10:
            raise ValidationError(_('Phone number must be 10 digits'))

        # Format and validate with phonenumbers library
        formatted = f"+1{phone}"
        parsed_number = phonenumbers.parse(formatted, "US")

        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(_('Invalid phone number'))

        # Store formatted number back to field
        field.data = formatted

    except phonenumbers.NumberParseException:
        raise ValidationError(_('Invalid phone number format'))


class SignupForm(FlaskForm):
    """User registration form"""
    first_name = StringField(
        _('First Name'),
        validators=[
            DataRequired(message=_('First name is required')),
            Length(min=2, max=50, message=_('First name must be between 2 and 50 characters'))
        ]
    )
    last_name = StringField(
        _('Last Name'),
        validators=[
            DataRequired(message=_('Last name is required')),
            Length(min=2, max=50, message=_('Last name must be between 2 and 50 characters'))
        ]
    )
    phone_number = StringField(
        _('Phone Number'),
        validators=[
            DataRequired(message=_('Phone number is required')),
            validate_phone_number
        ]
    )
    password = PasswordField(
        _('Password'),
        validators=[
            DataRequired(message=_('Password is required')),
            Length(min=6, message=_('Password must be at least 6 characters long'))
        ]
    )
    confirm_password = PasswordField(
        _('Confirm Password'),
        validators=[
            DataRequired(message=_('Please confirm your password')),
            EqualTo('password', message=_('Passwords must match'))
        ]
    )


class LoginForm(FlaskForm):
    """User login form"""
    phone_number = StringField(
        _('Phone Number'),
        validators=[
            DataRequired(message=_('Phone number is required')),
            validate_phone_number
        ]
    )
    password = PasswordField(
        _('Password'),
        validators=[DataRequired(message=_('Password is required'))]
    )
    remember_me = BooleanField(_('Remember Me'))


class VerificationForm(FlaskForm):
    """Phone verification code form"""
    code = StringField(
        _('Verification Code'),
        validators=[
            DataRequired(message=_('Verification code is required')),
            Length(min=6, max=6, message=_('Verification code must be 6 digits'))
        ]
    )


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    phone_number = StringField(
        _('Phone Number'),
        validators=[
            DataRequired(message=_('Phone number is required')),
            validate_phone_number
        ]
    )


class PasswordResetForm(FlaskForm):
    """Password reset form with verification code"""
    code = StringField(
        _('Verification Code'),
        validators=[
            DataRequired(message=_('Verification code is required')),
            Length(min=6, max=6, message=_('Verification code must be 6 digits'))
        ]
    )
    new_password = PasswordField(
        _('New Password'),
        validators=[
            DataRequired(message=_('New password is required')),
            Length(min=6, message=_('Password must be at least 6 characters long'))
        ]
    )
    confirm_password = PasswordField(
        _('Confirm Password'),
        validators=[
            DataRequired(message=_('Please confirm your password')),
            EqualTo('new_password', message=_('Passwords must match'))
        ]
    )


class ChangePasswordForm(FlaskForm):
    """Change password form for logged-in users"""
    old_password = PasswordField(
        _('Current Password'),
        validators=[DataRequired(message=_('Current password is required'))]
    )
    new_password = PasswordField(
        _('New Password'),
        validators=[
            DataRequired(message=_('New password is required')),
            Length(min=6, message=_('Password must be at least 6 characters long'))
        ]
    )
    confirm_password = PasswordField(
        _('Confirm Password'),
        validators=[
            DataRequired(message=_('Please confirm your password')),
            EqualTo('new_password', message=_('Passwords must match'))
        ]
    )


class EditProfileForm(FlaskForm):
    """Edit user profile form"""
    first_name = StringField(
        _('First Name'),
        validators=[
            DataRequired(message=_('First name is required')),
            Length(min=2, max=50, message=_('First name must be between 2 and 50 characters'))
        ]
    )
    last_name = StringField(
        _('Last Name'),
        validators=[
            DataRequired(message=_('Last name is required')),
            Length(min=2, max=50, message=_('Last name must be between 2 and 50 characters'))
        ]
    )
    phone_number = StringField(
        _('Phone Number'),
        validators=[
            DataRequired(message=_('Phone number is required')),
            validate_phone_number
        ]
    )


class TaskForm(FlaskForm):
    """Task creation/edit form"""
    title = StringField(
        _('Task Title'),
        validators=[
            DataRequired(message=_('Task title is required')),
            Length(min=1, max=200, message=_('Task title must be between 1 and 200 characters'))
        ]
    )
    description = TextAreaField(
        _('Description'),
        validators=[
            Optional(),
            Length(max=1000, message=_('Description must not exceed 1000 characters'))
        ]
    )
    due_date = DateField(
        _('Due Date'),
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    priority = SelectField(
        _('Priority'),
        choices=[
            ('1', _('Low')),
            ('2', _('Medium')),
            ('3', _('High'))
        ],
        default='2',
        coerce=str
    )
