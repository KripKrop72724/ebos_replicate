from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers

from ebos2201.exceptions import (
    AccountDisabledException,
    InvalidCredentialsException,
    SendingOTPException,
)
from ebos2201.notification import send_otp


class LoginSerializer(serializers.Serializer):
    """
    Serializer to login users with email or username.
    """

    OTP_METHOD_CHOICES = (
        ("sms", "SMS"),
        ("voice_call", "Voice Call"),
        ("email", "Email"),
    )

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    otp_method = serializers.ChoiceField(choices=OTP_METHOD_CHOICES)

    def _validate_user(self, username, password, otp_method):
        user = None

        if username and password and otp_method:
            user = authenticate(username=username, password=password)

        else:
            raise serializers.ValidationError(
                _("Enter an username or an email, password and otp method.")
            )

        return user

    def validate(self, validated_data):
        username = validated_data.get("username")
        password = validated_data.get("password")
        otp_method = validated_data.get("otp_method")

        user = None

        user = self._validate_user(username, password, otp_method)

        if not user:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise AccountDisabledException()

        try:
            # Send OTP to the specific method
            send_otp(user, otp_method)
        except ValueError as err:
            raise SendingOTPException()

        validated_data["user"] = user

        return validated_data


class OtpVerifySerializer(serializers.Serializer):
    """
    Serializer for verify otp
    """

    otp = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout
    """

    refresh_token = serializers.CharField()
