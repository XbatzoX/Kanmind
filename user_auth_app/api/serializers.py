from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

class RegistrationSerializer(serializers.ModelSerializer):
    """Handles new user registration, including password confirmation and field mappings."""
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password" : {
                "write_only" : True
            }
        }

    def validate_email(self, value):
        """Checks if the provided email address is already taken in the system."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists!")
        return value

    def save(self):
        """Validates matching passwords and creates a new User instance with hashed credentials."""
        pw = self.validated_data["password"]
        repeated_pw = self.validated_data["repeated_password"]
        if pw != repeated_pw:
            raise serializers.ValidationError({"error" : "password dont match"})
        account = User(
            username=self.validated_data["email"],
            email=self.validated_data["email"],
            first_name=self.validated_data["fullname"],
        )
        account.set_password(pw)
        account.save()
        return account

class EmailLoginSerializer(serializers.Serializer):
    """Handles user login validation using email credentials instead of a username."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, value):
        """Authenticates the user against the database based on provided email and password."""
        email = value.get("email")
        password = value.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError({"error": "Unable to log in with provided credentials."})
        else:
            raise serializers.ValidationError({"error": "Must include 'email' and 'password'."})
        value["user"] = user
        return value

        

