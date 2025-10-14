"""
Task management service.
"""
from typing import List, Optional
from datetime import datetime
from app import db
from app.models.tasks import Task


class TaskService:
    """Service for task operations"""

    @staticmethod
    def create_task(title: str, owner_id: int, description: str = None,
                   due_date: datetime = None, priority: int = 2) -> Task:
        """
        Create a new task

        Args:
            title: Task title
            owner_id: ID of the task owner
            description: Optional task description
            due_date: Optional due date
            priority: Task priority (1=Low, 2=Medium, 3=High)

        Returns:
            Task instance
        """
        task = Task(
            title=title,
            owner_id=owner_id,
            description=description,
            due_date=due_date,
            priority=priority,
            completed=False
        )
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def get_user_tasks(user_id: int, include_completed: bool = True,
                      order_by: str = 'created_at') -> List[Task]:
        """
        Get all tasks for a user

        Args:
            user_id: User ID
            include_completed: Whether to include completed tasks
            order_by: Field to order by (created_at, due_date, priority)

        Returns:
            List of Task instances
        """
        query = Task.query.filter_by(owner_id=user_id)

        if not include_completed:
            query = query.filter_by(completed=False)

        # Order by
        if order_by == 'due_date':
            query = query.order_by(Task.due_date.asc().nullslast())
        elif order_by == 'priority':
            query = query.order_by(Task.priority.desc())
        else:  # default: created_at
            query = query.order_by(Task.created_at.desc())

        return query.all()

    @staticmethod
    def get_task_by_id(task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        return Task.query.get(task_id)

    @staticmethod
    def update_task(task: Task, title: str = None, description: str = None,
                   due_date: datetime = None, priority: int = None) -> Task:
        """
        Update a task

        Args:
            task: Task instance to update
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            priority: New priority (optional)

        Returns:
            Updated Task instance
        """
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if priority is not None:
            task.priority = priority

        db.session.commit()
        return task

    @staticmethod
    def toggle_task_completion(task: Task) -> Task:
        """Toggle task completion status"""
        task.completed = not task.completed
        db.session.commit()
        return task

    @staticmethod
    def complete_task(task: Task) -> Task:
        """Mark a task as completed"""
        task.completed = True
        db.session.commit()
        return task

    @staticmethod
    def uncomplete_task(task: Task) -> Task:
        """Mark a task as not completed"""
        task.completed = False
        db.session.commit()
        return task

    @staticmethod
    def delete_task(task: Task) -> None:
        """Delete a task"""
        db.session.delete(task)
        db.session.commit()

    @staticmethod
    def get_task_stats(user_id: int) -> dict:
        """
        Get task statistics for a user

        Returns:
            Dictionary with task counts
        """
        total = Task.query.filter_by(owner_id=user_id).count()
        completed = Task.query.filter_by(owner_id=user_id, completed=True).count()
        pending = total - completed

        overdue = Task.query.filter(
            Task.owner_id == user_id,
            Task.completed == False,
            Task.due_date < datetime.now()
        ).count()

        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue
        }

    @staticmethod
    def is_task_owner(task: Task, user_id: int) -> bool:
        """Check if user is the owner of the task"""
        return task.owner_id == user_id
