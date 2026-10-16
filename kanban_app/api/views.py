from rest_framework import generics
from django.db import models
from kanban_app.models import Board, Task, Comment
from .serializers import BoardListSerializer, TaskSerializer, BoardDetailSerializer, TaskUserSerializer, \
    TaskDetailSerializer, CommentSerializer, BoardUpdateSerializer
from .permissions import IsCommentAuthor, IsBoardOwnerOrReadOnlyForMembers, \
    IsBoardMemberOrOwnerForTask
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class BoardListView(generics.ListCreateAPIView):
    """Handles listing existing boards for the user and creating new boards."""
    permission_classes = [IsAuthenticated]
    serializer_class = BoardListSerializer

    def get_queryset(self):
        """Returns boards where the authenticated user is either the owner or a member."""
        user = self.request.user
        return Board.objects.filter(models.Q(owner=user) | models.Q(members=user)).distinct()

    def perform_create(self, serializer):
        """Automatically assigns the logged-in user as the owner during board creation."""
        serializer.save(owner=self.request.user)

class TaskListView(generics.ListCreateAPIView):
    """Handles listing tasks for allowed boards and creating new tasks with permission checks."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Returns tasks from boards where the authenticated user is either the owner or a member."""
        user = self.request.user
        return Task.objects.filter(models.Q(board__owner=user) | models.Q(board__members=user)).distinct()

    def perform_create(self, serializer):
        """Validates board membership and assigns the logged-in user as the task creator."""
        board_id = self.request.data.get("board")
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise NotFound(detail="Board not found.")
        if board.owner != self.request.user and not board.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied(detail="Forbbiden for this board")
        serializer.save(creator=self.request.user, board=board)

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, or deleting a specific board instance based on permissions."""
    permission_classes = [IsAuthenticated, IsBoardOwnerOrReadOnlyForMembers]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """Dynamically switches to BoardUpdateSerializer for PATCH requests to reshape the response."""
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_queryset(self):
        """Returns all boards to allow object-level permission checking (403 Forbidden)."""
        return Board.objects.all()

class EmailCheckView(APIView):
    """Provides an endpoint to verify if a user exists by checking their email address."""
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """Checks query parameters for an email, validates existence, and returns user details."""
        email_to_check = request.query_params.get("email", None)
        if not email_to_check:
            return Response({"error" : "please insert mail address."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email_to_check)
            serializer = TaskUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({"error" : "No user found with this mail."}, status=status.HTTP_404_NOT_FOUND)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, or deleting a specific task instance based on board and task permissions."""
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwnerForTask]
    serializer_class = TaskDetailSerializer

    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        """Returns all tasks to allow object-level permission checking (403 Forbidden)."""
        return Task.objects.all()

    def perform_create(self, serializer):
        """Ensures the logged-in user is set as the task creator during instantiation."""
        serializer.save(creator=self.request.user)

class CommentListCreateView(generics.ListCreateAPIView):
    """Handles listing comments for a specific task and creating new comments with board membership validation."""
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Validates task existence and board membership before returning the associated comments."""
        task_id = self.kwargs.get("task_id")
        user = self.request.user
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound(detail="Task nicht gefunden")
        is_member = Task.objects.filter(models.Q(id=task_id) & (models.Q(board__owner=user) | models.Q(board__members=user))).exists()
        if not is_member:
            raise PermissionDenied(detail="User has to be a member")
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        """Validates permissions and links the authenticated user as the author of the new comment."""
        task_id = self.kwargs.get("task_id")
        user = self.request.user
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound(detail="Task not found")
        is_member = Task.objects.filter(models.Q(id=task_id) & (models.Q(board__owner=user) | models.Q(board__members=user))).exists()
        if not is_member:
            raise PermissionDenied(detail="User has to be a member")
        serializer.save(author=user, task=task)

class CommentDestroyView(generics.DestroyAPIView):
    """Handles deleting a specific comment instance after verifying task and author permissions."""
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    serializer_class = CommentSerializer

    def get_object(self):
        """Validates the associated task and comment existence before checking object deletion rights."""
        user = self.request.user
        task = get_validated_task(self.kwargs.get("task_id"), user)
        try:
            comment = Comment.objects.get(id=self.kwargs.get("comment_id"), task=task)
        except Comment.DoesNotExist:
            raise NotFound(detail="task or comment not found")
        self.check_object_permissions(self.request, comment)
        return comment

class UserTasksListView(generics.ListAPIView):
    """Handles listing all tasks that are specifically assigned to the authenticated user."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Filters and returns tasks where the logged-in user is set as the assignee."""
        user = self.request.user
        return Task.objects.filter(assignee=user)

class ReviewedTasksListView(generics.ListAPIView):
    """Handles listing all tasks where the authenticated user is assigned as the reviewer."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Filters and returns tasks where the logged-in user is set as the reviewer."""
        return Task.objects.filter(reviewer=self.request.user)

def get_validated_task(task_id, user):
    """Validates task existence and ensures the user has access via board ownership or membership.
        Returns the task instance if valid, otherwise raises NotFound or PermissionDenied.
    """
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        raise NotFound(detail="task or comment not found")
    is_member = Task.objects.filter(models.Q(id=task_id) & (models.Q(board__owner=user) | models.Q(board__members=user))).exists()
    if not is_member:
        raise PermissionDenied(detail="Forbidden, you have to be user or member")
    return task

    

