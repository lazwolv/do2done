from datetime import datetime, timedelta
import random
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.users import User
from app.models.verification import VerificationCode
from app import db, client, TWILIO_PHONE_NUMBER
import phonenumbers

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))

def send_verification_sms(phone_number, verification_code=None):
    if verification_code is None:
        verification_code = generate_verification_code()
    
    # Create verification record
    verification = VerificationCode(
        phone_number=phone_number, 
        code=verification_code,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(minutes=10)
    )
    db.session.add(verification)
    db.session.commit()
    
    # Send SMS
    message = client.messages.create(
        body=f'Your Do2Done verification code is: {verification_code}',
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone_number')
        password = request.form.get('password')
    
        # Validate phone number format
        try:
            phone_number_obj = phonenumbers.parse(phone, "US")
            if not phonenumbers.is_valid_number(phone_number_obj):
                flash('Invalid phone number')
                return redirect(url_for('auth.signup'))
            formatted_number = phonenumbers.format_number(phone_number_obj, 
                                                        phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            flash('Invalid phone number format')
            return redirect(url_for('auth.signup'))
        
        if User.query.filter_by(phone_number=formatted_number).first():
            flash('Phone number already registered')
            return redirect(url_for('auth.signup'))
        
        # Generate verification code
        verification_code = generate_verification_code()
        
        # Create and save user
        user = User(
            first_name=first_name,
            last_name=last_name,
            phone_number=formatted_number,
            verification_code=verification_code,
            verification_attempts=0,
            verified=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Send verification SMS
        send_verification_sms(formatted_number, verification_code)
        
        # Store phone in session for verification
        session['user_id'] = user.id
        
        flash('Account created successfully. Please verify your phone number.')
        return redirect(url_for('auth.verify_phone'))
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        
        try:
            phone_obj = phonenumbers.parse(phone_number, "US")
            formatted_number = phonenumbers.format_number(phone_obj,
                                                    phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            flash('Invalid phone number format')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(phone_number=formatted_number).first()
        
        if user and user.check_password(password):
            if not user.verified:
                flash('Please verify your phone number first by creating an account')
                return redirect(url_for('auth.signup'))
            
            # User is verified, log them in directly
            login_user(user)
            return redirect(url_for('tasks.index'))
        
        flash('Invalid phone number or password')
    return render_template('login.html')

@auth_bp.route('/verify-phone', methods=['GET', 'POST'])
def verify_phone():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code')
        
        if not user.verification_code:
            flash('No verification code was sent.')
            return redirect(url_for('auth.signup'))
            
        # Check verification attempts
        if user.verification_attempts >= 3:
            if user.last_verification_attempt + timedelta(minutes=15) > datetime.now():
                flash('Too many attempts. Please wait 15 minutes.')
                return redirect(url_for('auth.signup'))
            user.verification_attempts = 0
            
        # Verify code
        if code == user.verification_code:
            user.verified = True
            user.verification_code = None
            user.verification_attempts = 0
            db.session.commit()
            login_user(user)
            session.pop('user_id')
            flash('Phone number verified successfully!')
            return redirect(url_for('tasks.index'))
        
        user.verification_attempts += 1
        user.last_verification_attempt = datetime.now()
        db.session.commit()
        flash('Invalid verification code.')
        
    return render_template('verify_phone.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Handle phone number submission
        if 'phone_number' in request.form and 'code' not in request.form:
            phone_number = request.form.get('phone_number')
            try:
                phone_obj = phonenumbers.parse(phone_number, "US")
                formatted_number = phonenumbers.format_number(phone_obj, 
                                                            phonenumbers.PhoneNumberFormat.E164)
                user = User.query.filter_by(phone_number=formatted_number).first()
            
                if user:
                    session['reset_phone'] = formatted_number
                    send_verification_sms(formatted_number)
                    return render_template('reset_password.html', show_code_form=True)
            
                flash('Phone number not found')
            
            except phonenumbers.NumberParseException:
                flash('Invalid phone number format')
        
            return redirect(url_for('reset_password'))
    
        # Handle verification code and new password
        if 'code' in request.form and 'new_password' in request.form:
            if 'reset_phone' not in session:
                return redirect(url_for('reset_password'))
            
            code = request.form.get('code')
            new_password = request.form.get('new_password')
        
            verification = VerificationCode.query.filter_by(
                phone_number=session['reset_phone'],
                code=code
            ).order_by(VerificationCode.created_at.desc()).first()
        
            if verification:
                user = User.query.filter_by(phone_number=session['reset_phone']).first()
                user.set_password(new_password)
                db.session.commit()
                session.pop('reset_phone', None)
                flash('Password has been reset successfully')
                return redirect(url_for('login'))
            
            flash('Invalid verification code')
            return render_template('reset_password.html', show_code_form=True)
        
    return render_template('reset_password.html', show_code_form=False)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('auth.login'))

@auth_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted.')
    return redirect(url_for('auth.register'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        if not current_user.check_password(old_password):
            flash('Current password is incorrect.')
            return redirect(url_for('auth.change_password'))
            
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully.')
        return redirect(url_for('auth.profile'))
        
    return render_template('change_password.html')

@auth_bp.route('/recover-account', methods=['GET', 'POST'])
def recover_account():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        try:
            phone_number_obj = phonenumbers.parse(phone_number, "US")
            formatted_number = phonenumbers.format_number(phone_number_obj, 
                                                        phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            flash('Invalid phone number format')
            return redirect(url_for('auth.recover_account'))
            
        user = User.query.filter_by(phone_number=formatted_number).first()
        
        if user:
            verification_code = ''.join(random.choices('0123456789', k=6))
            user.verification_code = verification_code
            user.verification_attempts = 0
            user.last_verification_attempt = datetime.now()
            db.session.commit()
            
            if send_verification_sms(formatted_number, verification_code):
                session['recovery_phone'] = formatted_number
                flash('Verification code sent to your phone.')
                return redirect(url_for('auth.verify_recovery'))
            else:
                flash('Error sending verification code.')
        else:
            flash('No account found with that phone number.')
            
    return render_template('recover_account.html')

@auth_bp.route('/verify-recovery', methods=['GET', 'POST'])
def verify_recovery():
    if 'recovery_phone' not in session:
        return redirect(url_for('auth.recover_account'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        new_password = request.form.get('new_password')
        user = User.query.filter_by(phone_number=session['recovery_phone']).first()
        
        if user and code == user.verification_code:
            user.set_password(new_password)
            user.verification_code = None
            db.session.commit()
            session.pop('recovery_phone')
            flash('Password has been reset successfully.')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid verification code.')
            
    return render_template('verify_recovery.html')
