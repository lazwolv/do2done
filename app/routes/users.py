from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.users import User
from app import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@users_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        phone = request.form.get('phone_number')
        
        current_user.first_name = first_name
        current_user.phone_number = phone
        db.session.commit()
        
        return redirect(url_for('users.profile'))
        
    return render_template('users/edit_profile.html', user=current_user)
