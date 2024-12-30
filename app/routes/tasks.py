from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.tasks import Task
from app import db

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(owner_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

@tasks_bp.route('/add', methods=['POST'])
@login_required
def add_task():
    task_title = request.form.get('task')
    new_task = Task(title=task_title, owner_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.owner_id == current_user.id:
        task.completed = True
        db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.owner_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('tasks.index'))
