from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions
from .models import EmailToken, EmailOTP
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    EmailTokenSerializer,
    EmailOTPSerializer,
)

User = get_user_model()


# -------------------------
# Registration & Email Verification
# -------------------------
# Register -> create EmailToken and return token metadata (debug-only token)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user with email or phone.",
        request_body=RegisterSerializer,
        responses={201: UserSerializer},
        security=[],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # create token for signup verification
        token_obj = EmailToken.create_for_user(user, purpose=EmailToken.PURPOSE_SIGNUP)

        # Build absolute verification URL using the current request host
        verify_path = reverse("verify-email")
        verification_link = request.build_absolute_uri(
            f"{verify_path}?token={token_obj.token}"
        )
        send_mail(
            subject="Verify Your Email",
            message=f"Click the link to verify your account: {verification_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Build response with timestamps included
        data = UserSerializer(user).data
        token_data = EmailTokenSerializer(token_obj).data

        # For testing convenience only: return token in response when DEBUG
        if settings.DEBUG:
            data["verification"] = token_data
        else:
            # still return safe metadata (timestamps + purpose) without token
            data["verification_meta"] = {
                "purpose": token_data["purpose"],
                "created_at": token_data["created_at"],
                "expires_at": token_data["expires_at"],
            }

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class VerifyEmailView(APIView):
    """Confirm email using token"""

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Verify user email with token",
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="Verification token from email",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                examples={
                    "application/json": {
                        "detail": "Email verified successfully",
                        "verified_at": "2025-09-24T15:00:00Z",
                    }
                },
            ),
            400: "Token expired",
            404: "Token not found",
        },
        security=[],
    )
    def get(self, request):
        token = request.query_params.get("token")
        token_obj = get_object_or_404(
            EmailToken, token=token, purpose=EmailToken.PURPOSE_SIGNUP
        )

        if not token_obj.is_valid():
            return Response(
                {"detail": "Token expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.is_verified = True
        user.save()
        token_obj.delete()
        return Response(
            {"detail": "Email verified successfully", "verified_at": timezone.now()}
        )


# -------------------------
# Login / Logout
# -------------------------
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    """Login user and return JWT tokens"""

    @swagger_auto_schema(
        operation_description="Login and receive JWT tokens",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="JWT access and refresh tokens",
                examples={
                    "application/json": {
                        "message": "Welcome back, Alice 🎉",
                        "user": {
                            "id": 1,
                            "first_name": "Alice",
                            "last_name": "Doe",
                            "email": "alice@example.com",
                            "phone": "",
                            "role": "user",
                            "is_verified": True,
                            "date_joined": "2025-09-24T15:00:00Z",
                        },
                        "refresh": "<refresh_token>",
                        "access": "<access_token>",
                    }
                },
            )
        },
        security=[],  # Disable auth for this endpoint
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        phone = serializer.validated_data.get("phone")
        password = serializer.validated_data.get("password")

        user = None
        if email:
            user = authenticate(request, email=email, password=password)
        elif phone:
            user = authenticate(request, phone=phone, password=password)

        if user:
            if not user.is_verified:
                return Response(
                    {"detail": "Please verify your email first"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": f"Welcome back, {user.first_name or user.email} 🎉",
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    """Blacklist JWT refresh token"""

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required"}, status=400)

        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logged out successfully"})


# -------------------------
# Forgot & Reset Password (OTP Flow)
# -------------------------
class ForgotPasswordView(APIView):
    """Send OTP for password reset"""

    @swagger_auto_schema(
        operation_description="Send an OTP code to the user's email for password reset.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["email"],
        ),
        responses={200: "OTP sent"},
        security=[],
    )
    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)

        otp_obj = EmailOTP.create_for_user(user, purpose=EmailOTP.PURPOSE_RESET)
        send_mail(
            subject="Password Reset Code",
            message=f"Your password reset code is: {otp_obj.code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        response = {
            "detail": "Password reset code sent to email",
            "sent_at": timezone.now(),
            "expires_at": otp_obj.expires_at,
        }
        # for testing return OTP metadata (and code in DEBUG)
        otp_meta = EmailOTPSerializer(otp_obj).data
        if settings.DEBUG:
            response["otp"] = otp_meta
        else:
            response["otp_meta"] = {
                "created_at": otp_meta["created_at"],
                "expires_at": otp_meta["expires_at"],
            }

        return Response(response)


class ResetPasswordView(APIView):
    """Reset password using OTP"""

    @swagger_auto_schema(
        operation_description="Reset password using email OTP code.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["email", "code", "password"],
        ),
        responses={200: "Password reset successful"},
        security=[],
    )
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("password")

        user = get_object_or_404(User, email=email)
        otp_obj = get_object_or_404(
            EmailOTP, user=user, code=code, purpose=EmailOTP.PURPOSE_RESET
        )

        if not otp_obj.is_valid():
            return Response({"detail": "Invalid or expired OTP"}, status=400)

        user.set_password(new_password)
        user.save()

        otp_obj.used = True
        otp_obj.save()

        return Response(
            {"detail": "Password reset successful", "reset_at": timezone.now()}
        )
