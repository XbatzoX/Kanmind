from .serializers import RegistrationSerializer, EmailLoginSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken

class RegistrationView(APIView):
    """Provides a public endpoint for new user registration and account creation."""
    permission_classes = [AllowAny]

    def post(self, request):
        """Validates credentials, creates a new user, and generates an auth token."""
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                "token" : token.key,
                "fullname" : saved_account.first_name,
                "email" : saved_account.email,
                "user_id": saved_account.pk
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class CustomerLoginView(ObtainAuthToken):
    """Provides a public login endpoint utilizing email-based credentials to generate auth tokens."""
    permission_classes = [AllowAny]
    serializer_class = EmailLoginSerializer

    def post(self, request):
        """Validates credentials via the email serializer and returns user details along with their token."""
        serializer = self.serializer_class(data=request.data)
        data = {}

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            data = {
                "token" : token.key,
                "fullname" : user.first_name,
                "email" : user.email,
                "user_id": user.pk
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)