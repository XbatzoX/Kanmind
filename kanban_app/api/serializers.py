from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from django.contrib.auth.models import User

class BoardListSerializer(serializers.ModelSerializer):
    """Serializes the board list with aggregated counts for members, tickets, and tasks."""
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "members", "member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner_id"]
        extra_kwargs = {
            "members" : {"write_only" : True}
        }

    def get_member_count(self, obj):
        """Returns the total number of board members."""
        return obj.members.count()

    def get_ticket_count(self,obj):
        """Returns the total number of tasks assigned to the board."""
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """Returns the number of tasks with 'to-do' status."""
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """Returns the number of tasks with 'high' priority."""
        return obj.tasks.filter(priority="high").count()

class TaskUserSerializer(serializers.ModelSerializer):
    """Serializes user information with details for assignee, reviewer, or author."""
    fullname = serializers.CharField(source="first_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

class BoardTaskSerializer(serializers.ModelSerializer):
    """Serializes compact task details including nested users and comment counts for board views."""
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority", "assignee", "reviewer",
            "due_date", "comments_count"
        ]
        read_only_fields = ["id", "board"]

    def get_comments_count(self,obj):
        """Returns the total number of comments associated with the task."""
        if hasattr(obj, "comments"):
            return obj.comments.count()
        return 0
    

class TaskSerializer(serializers.ModelSerializer):
    """Serializes full task objects with primary key relation handling for assignments."""
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    board = serializers.PrimaryKeyRelatedField(
        queryset = Board.objects.all()
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(), write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id", "board", "title", "description", "status", "priority",
            "assignee", "reviewer", "due_date", "comments_count",
            "assignee_id", "reviewer_id"
        ]

    def get_comments_count(self, obj):
        """Returns the total number of comments associated with the task."""
        if hasattr(obj, "comments"):
            return obj.comments.count()
        return 0

    def create(self, validated_data):
        """Creates a new task and manually resolves optional write-only user relations."""
        assignee_user = validated_data.pop("assignee_id", None)
        reviewer_user = validated_data.pop("reviewer_id", None)
        task = Task.objects.create(**validated_data)
        if assignee_user:
            task.assignee = assignee_user
        if reviewer_user:
            task.reviewer = reviewer_user
        task.save()
        return task

class BoardDetailSerializer(serializers.ModelSerializer):
    """Serializes full board details, including nested members and associated tasks for full views."""
    members = TaskUserSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id", "title", "owner_id", "members", "tasks"
        ]

class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializes partial board updates (PATCH) with custom validation for member assignments."""
    owner_data = TaskUserSerializer(source="owner", read_only=True)
    members_data = TaskUserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]

    def validate(self, attrs):
        """Validates input data, blocking unexpected fields and verifying member ID existence."""
        for key in self.initial_data.keys():
            if key not in self.Meta.fields and key != "members":
                raise serializers.ValidationError({key: f"Field '{key}' doesnt exist"})
        member_ids = self.initial_data.get("members", None)
        if member_ids is not None:
            if not isinstance(member_ids, list):
                raise serializers.ValidationError({"members" : "Members should be in a list"})
            existing_users_count = User.objects.filter(id__in=member_ids).count()
            if existing_users_count != len(member_ids):
                raise serializers.ValidationError({"members" : "Min one member doesnt exist"})
        return attrs


    def update(self, instance, validated_data):
        """Updates the board instance and handles the Many-to-Many relation for board members."""
        member_ids = self.initial_data.get("members", None)
        if member_ids is not None:
            instance.members.set(member_ids)
        return super().update(instance, validated_data)

    

class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializes detailed task objects for single instances, managing read-only objects and write-only IDs."""
    assignee = TaskUserSerializer(read_only=True)
    reviewer = TaskUserSerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(), source="assignee", write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(), source="reviewer", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "priority", "assignee", "reviewer", "assignee_id", "reviewer_id", "due_date"]

        read_only_fields = ["id", "board"]

    def validate(self, attrs):
        """Validates incoming PATCH fields, strictly blocking any undefined or unexpected keys."""
        for key in self.initial_data.keys():
            if key not in self.Meta.fields:
                raise serializers.ValidationError({key: f"The field '{key}' does not exist in task"})
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    """Serializes task comments, displaying the author's first name and formatting timestamps."""
    author = serializers.ReadOnlyField(source="author.first_name")
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]