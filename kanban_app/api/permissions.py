from rest_framework import permissions

class IsCommentAuthor(permissions.BasePermission):
    """Grants access only if the logged-in user is the author of the comment."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsBoardOwnerOrReadOnlyForMembers(permissions.BasePermission):
    """Allows view/edit for all members, but restricts deletion to the board owner only."""
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.owner == request.user
        return True

class IsBoardOwnerOrTaskCreatorOnly(permissions.BasePermission):
    """Allows view/edit for all members, but restricts deletion to the board owner or task creator."""
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            is_board_owner = obj.board.owner == request.user
            is_task_creator = obj.creator == request.user
            return is_board_owner or is_task_creator
        return True