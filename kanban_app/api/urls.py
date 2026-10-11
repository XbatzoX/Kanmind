from django.urls import path
from .views import BoardListView, TaskListView, BoardDetailView, EmailCheckView, TaskDetailView, \
    CommentListCreateView, CommentDestroyView, UserTasksListView, ReviewedTasksListView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='boards-list'),
    path('tasks/', TaskListView.as_view(), name="tasks-list"),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name="board-detail"),
    path('email-check/', EmailCheckView.as_view(), name="email-check"),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name="task-detail"),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name="comments-list"),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDestroyView.as_view(), name="comment-destroy"),
    path('tasks/assigned-to-me/', UserTasksListView.as_view(), name="user-tasks-list"),
    path('tasks/reviewing/', ReviewedTasksListView.as_view(), name="reviewed-tasks-list"),
]
