"""
CLI commands for do2done application.
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from app import db
from app.models.users import User
from app.models.tasks import Task


@click.group()
def cli():
    """do2done management commands"""
    pass


@cli.command()
@with_appcontext
def init_db():
    """Initialize the database"""
    click.echo('Creating database tables...')
    db.create_all()
    click.echo('Database initialized successfully!')


@cli.command()
@with_appcontext
def drop_db():
    """Drop all database tables"""
    if click.confirm('This will delete all data. Are you sure?'):
        click.echo('Dropping database tables...')
        db.drop_all()
        click.echo('Database dropped successfully!')


@cli.command()
@with_appcontext
def reset_db():
    """Reset the database (drop and recreate)"""
    if click.confirm('This will delete all data and recreate tables. Are you sure?'):
        click.echo('Dropping database tables...')
        db.drop_all()
        click.echo('Creating database tables...')
        db.create_all()
        click.echo('Database reset successfully!')


@cli.command()
@with_appcontext
@click.option('--first-name', prompt=True, help='First name')
@click.option('--last-name', prompt=True, help='Last name')
@click.option('--phone', prompt=True, help='Phone number (10 digits)')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password')
def create_user(first_name, last_name, phone, password):
    """Create a new user"""
    # Format phone number
    phone_digits = ''.join(filter(str.isdigit, phone))
    if len(phone_digits) != 10:
        click.echo('Error: Phone number must be 10 digits')
        return

    formatted_phone = f"+1{phone_digits}"

    # Check if user exists
    if User.query.filter_by(phone_number=formatted_phone).first():
        click.echo('Error: User with this phone number already exists')
        return

    # Create user
    user = User(
        first_name=first_name,
        last_name=last_name,
        phone_number=formatted_phone,
        verified=True  # Auto-verify CLI created users
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    click.echo(f'User created successfully! ID: {user.id}')


@cli.command()
@with_appcontext
def list_users():
    """List all users"""
    users = User.query.all()
    if not users:
        click.echo('No users found.')
        return

    click.echo(f'Total users: {len(users)}\n')
    for user in users:
        status = 'Verified' if user.verified else 'Not Verified'
        click.echo(f'ID: {user.id} | {user.full_name} | {user.phone_number} | {status}')


@cli.command()
@with_appcontext
def db_stats():
    """Show database statistics"""
    user_count = User.query.count()
    task_count = Task.query.count()
    completed_count = Task.query.filter_by(completed=True).count()
    pending_count = task_count - completed_count

    click.echo('Database Statistics:')
    click.echo(f'  Users: {user_count}')
    click.echo(f'  Tasks: {task_count}')
    click.echo(f'    Completed: {completed_count}')
    click.echo(f'    Pending: {pending_count}')


@cli.command()
@with_appcontext
@click.option('--count', default=5, help='Number of sample tasks to create')
def seed_data(count):
    """Seed database with sample data for testing"""
    if not click.confirm(f'Create sample user and {count} tasks?'):
        return

    # Create sample user
    phone = "+15555551234"
    user = User.query.filter_by(phone_number=phone).first()

    if not user:
        user = User(
            first_name="Test",
            last_name="User",
            phone_number=phone,
            verified=True
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        click.echo(f'Created test user: {user.phone_number} / password123')

    # Create sample tasks
    from datetime import datetime, timedelta

    sample_tasks = [
        {'title': 'Buy groceries', 'priority': 2, 'days': 2},
        {'title': 'Finish project report', 'priority': 3, 'days': 1},
        {'title': 'Call dentist', 'priority': 2, 'days': 3},
        {'title': 'Exercise', 'priority': 1, 'days': 0},
        {'title': 'Read book', 'priority': 1, 'days': 7},
    ]

    for i in range(min(count, len(sample_tasks))):
        task_data = sample_tasks[i]
        task = Task(
            title=task_data['title'],
            priority=task_data['priority'],
            due_date=datetime.now() + timedelta(days=task_data['days']),
            owner_id=user.id
        )
        db.session.add(task)

    db.session.commit()
    click.echo(f'Created {min(count, len(sample_tasks))} sample tasks')


def register_cli_commands(app):
    """Register CLI commands with the Flask app"""
    app.cli.add_command(cli)
