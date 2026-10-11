from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Board(models.Model):
    """Represents a Kanban board owned by a user and shared with multiple members."""
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_boards")
    members = models.ManyToManyField(User, related_name="boards", blank=True)

    def __str__(self):
        """Returns the string representation of the board using its title."""
        return self.title

class Task(models.Model):
    """Represents a Kanban task or ticket belonging to a board, with status, priority, and assigned users."""
    STATUS_CHOICES = [
        ("to-do", "to-do"),
        ("in-progress", "in-progress"),
        ("review", "review"),
        ("done", "done")
    ]
    PRIORITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high")
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="to-do")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    due_date = models.DateField(blank=True, null=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_tasks")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tasks")

    def __str__(self):
        """Returns the task title and its current workflow status as a string."""
        return f"{self.title} ({self.status})"

class Comment(models.Model):
    """Represents a text comment made by a user on a specific Kanban task."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Returns a string indicating the author's first name and the related task's ID."""
        return f"Comment by {self.author.first_name} on Task #{self.task.pk}"