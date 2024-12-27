import random
import phonenumbers
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, timedelta
from app.models.verification import VerificationCode
from models.users import User
from app import db, client, TWILIO_PHONE_NUMBER

auth = Blueprint('auth', __name__)

def send_verification_sms(phone_number, code):
    try:
        message = client.messages.create(
            body=f'Your verification code is: {code}',
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone_number')
        password = request.form.get('password')
    
        # Validate phone number format
        try:
            phone_number_obj = phonenumbers.parse(phone, "US")  # Change "US" to default country code
            if not phonenumbers.is_valid_number(phone_number_obj):
                flash('Invalid phone number')
                return redirect(url_for('auth.signup'))
            formatted_number = phonenumbers.format_number(phone_number_obj, 
                                                        phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            flash('Invalid phone number format')
            return redirect(url_for('auth.signup'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.signup'))
        
        if User.query.filter_by(phone_number=formatted_number).first():
            flash('Phone number already registered')
            return redirect(url_for('auth.signup'))
        
        user = User(username=username, phone_number=formatted_number)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    
        # Send verification SMS
        send_verification_sms(formatted_number, user.verification_code)
    
        return redirect(url_for('auth.verify_phone'))
    
    return render_template('signup.html')

@auth.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('login'))
            
        user = User.query.filter_by(phone_number=formatted_number).first()
        
        if user and user.check_password(password):
            if not user.verified:
                session['phone_number'] = formatted_number
                send_verification_sms(formatted_number)
                return redirect(url_for('verify_phone'))
                
            login_user(user)
            return redirect(url_for('index'))
            
        flash('Invalid phone number or password')
    return render_template('login.html')

@auth.route('/verify-phone', methods=['GET', 'POST'])
@login_required
def verify_phone():
    if request.method == 'POST':
        code = request.form.get('code')
        user = current_user
        
        if not user.verification_code:
            flash('No verification code was sent.')
            return redirect(url_for('profile'))
            
        if user.verification_attempts >= 3:
            if user.last_verification_attempt + timedelta(minutes=15) > datetime.utcnow():
                flash('Too many attempts. Please wait 15 minutes.')
                return redirect(url_for('profile'))
            user.verification_attempts = 0
            
        if code == user.verification_code:
            user.verified = True
            user.verification_code = None
            user.verification_attempts = 0
            db.session.commit()
            flash('Phone number verified successfully!')
        else:
            user.verification_attempts += 1
            user.last_verification_attempt = datetime.utcnow()
            db.session.commit()
            flash('Invalid verification code.')
            
        return redirect(url_for('profile'))

@auth.route('/reset-password', methods=['GET', 'POST'])
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('auth.login'))

@auth.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user = current_user
    db.session.delete(user)
    db.session.commit()
    logout_user()
    flash('Your account has been deleted.')
    return redirect(url_for('auth.register'))

@auth.route('/change-password', methods=['GET', 'POST'])
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

@auth.route('/recover-account', methods=['GET', 'POST'])
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

@auth.route('/verify-recovery', methods=['GET', 'POST'])
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
