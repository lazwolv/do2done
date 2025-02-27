import random
import phonenumbers
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.users import User, VerificationCode
from app import db, client, TWILIO_PHONE_NUMBER
from flask_babel import _

users_bp = Blueprint('users', __name__, url_prefix='/users')

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

@users_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = ''.join(filter(str.isdigit, request.form.get('phone_number')))
        password = request.form.get('password')
        
        # Validate phone number is exactly 10 digits
        if len(phone) != 10:
            flash(_('Phone number must be 10 digits'))
            return redirect(url_for('users.signup'))
            
        # Format to E.164 for Twilio (+1 for US numbers)
        formatted_number = f"+1{phone}"
        
        if User.query.filter_by(phone_number=formatted_number).first():
            flash('Phone number already registered')
            return redirect(url_for('users.signup'))
        
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
        
        session['user_id'] = user.id
        flash('Account created successfully. Please verify your phone number.')
        return redirect(url_for('users.verify_phone'))
    
    return render_template('signup.html')

@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = ''.join(filter(str.isdigit, request.form.get('phone_number')))
        formatted_number = f"+1{phone}" if len(phone) == 10 else None
        password = request.form.get('password')
        
        if not formatted_number:
            flash('Invalid phone number')
            return redirect(url_for('users.login'))
        
        user = User.query.filter_by(phone_number=formatted_number).first()

        if user and user.check_password(password):
            if not user.verified:
                flash('Please verify your phone number first by creating an account')
                return redirect(url_for('users.signup'))
            
            # User is verified, log them in directly
            login_user(user)
            return redirect(url_for('tasks.index'))
        
        flash('Invalid phone number or password')
    return render_template('login.html')

@users_bp.route('/verify-phone', methods=['GET', 'POST'])
def verify_phone():
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
        
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        code = request.form.get('code')
        
        if not user.verification_code:
            flash('No verification code was sent.')
            return redirect(url_for('users.signup'))
            
        # Check verification attempts
        if user.verification_attempts >= 3:
            if user.last_verification_attempt + timedelta(minutes=15) > datetime.now():
                flash('Too many attempts. Please wait 15 minutes.')
                return redirect(url_for('users.signup'))
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

@users_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Handle phone number submission
        if 'phone_number' in request.form and 'code' not in request.form:
            phone = ''.join(filter(str.isdigit, request.form.get('phone_number')))
            formatted_number = f"+1{phone}" if len(phone) == 10 else None

            if not formatted_number:
                flash('Invalid phone number')
                return redirect(url_for('users.reset_password'))
        
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

@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('users.login'))

@users_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted.')
    return redirect(url_for('users.signup'))

@users_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        if not current_user.check_password(old_password):
            flash('Current password is incorrect.')
            return redirect(url_for('users.change_password'))
            
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully.')
        return redirect(url_for('users.profile'))
        
    return render_template('change_password.html')

@users_bp.route('/recover-account', methods=['GET', 'POST'])
def recover_account():
    if request.method == 'POST':
        phone = ''.join(filter(str.isdigit, request.form.get('phone_number')))
        formatted_number = f"+1{phone}" if len(phone) == 10 else None
        
        if not formatted_number:
            flash('Invalid phone number')
            return redirect(url_for('users.recover_account'))
            
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
                return redirect(url_for('users.verify_recovery'))
            else:
                flash('Error sending verification code.')
        else:
            flash('No account found with that phone number.')
            
    return render_template('recover_account.html')

@users_bp.route('/verify-recovery', methods=['GET', 'POST'])
def verify_recovery():
    if 'recovery_phone' not in session:
        return redirect(url_for('users.recover_account'))
        
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
            return redirect(url_for('users.login'))
        else:
            flash('Invalid verification code.')
            
    return render_template('verify_recovery.html')

@users_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@users_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        phone = ''.join(filter(str.isdigit, request.form.get('phone_number')))
        
        if len(phone) != 10:
            flash('Phone number must be 10 digits')
            return redirect(url_for('users.edit_profile'))
            
        formatted_number = f"+1{phone}"
        
        # Check if phone number is already in use by another user
        existing_user = User.query.filter(
            User.phone_number == formatted_number,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            flash('Phone number already in use')
            return redirect(url_for('users.edit_profile'))
        
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone_number = formatted_number
        db.session.commit()
        
        flash('Profile updated successfully')
        return redirect(url_for('users.profile'))
        
    return render_template('edit_profile.html', user=current_user)
