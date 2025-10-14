from app import db
from datetime import datetime


class Task(db.Model):
    """Task model for to-do items"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=2)  # 1=Low, 2=Medium, 3=High
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and not self.completed:
            return datetime.now() > self.due_date
        return False

    @property
    def priority_label(self):
        """Get human-readable priority label"""
        labels = {1: 'Low', 2: 'Medium', 3: 'High'}
        return labels.get(self.priority, 'Medium')

    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'priority_label': self.priority_label,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_overdue': self.is_overdue,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'owner_id': self.owner_id
        }


task_shares = db.Table('task_shares',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
