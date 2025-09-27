from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, EmailToken, EmailOTP

class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(read_only=True)  # returns ISO-8601 by default
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "phone", "role", "is_verified", "date_joined")

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "password", "location", "role")

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Normalize blanks to None
        email = validated_data.get("email") or None
        phone = validated_data.get("phone") or None

        # Enforce that at least one identifier is provided
        if not email and not phone:
            raise serializers.ValidationError({
                "non_field_errors": ["Provide either an email address or a phone number."]
            })

        validated_data["email"] = email
        validated_data["phone"] = phone

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

class EmailTokenSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = EmailToken
        fields = ("token", "purpose", "created_at", "expires_at")


class EmailOTPSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    expires_at = serializers.DateTimeField(read_only=True)
    used = serializers.BooleanField(read_only=True)

    class Meta:
        model = EmailOTP
        fields = ("id", "code", "purpose", "created_at", "expires_at", "used")
