import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.utils import timezone

from ebos2201.models.m01_core_mas import User


def send_otp(user: User, otp_method: str) -> None:
    otp = random.randint(100000, 999999)

    if otp_method == "email":
        try:
            if user.email:
                subject = "OTP Token"
                message = f"OTP: {otp}"
                recipient_list = [
                    user.email,
                ]

                # Save OTP to User model
                expire_at = timezone.now() + timedelta(minutes=5)
                User.objects.filter(id=user.id).update(otp=otp, otp_expire_at=expire_at)

                # Send Email to user
                send_email(subject, message, recipient_list)
        except Exception as err:
            raise ValueError(err)

    elif otp_method == "voice_call":
        pass

    elif otp_method == "sms":
        pass


""" Send email function """


def send_email(subject, message, mail_to, mail_from=None, attachement=None):
    try:
        from ebos2201.models.m01_core_mas import T01Cfg10
        print("ON EMAIL SENDER")
        config_obj = T01Cfg10.objects.filter().first()
        backend = EmailBackend(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username="fytfytfyt420@gmail.com",
            password="bpysybrpnzzajogt",
            use_tls=settings.EMAIL_USE_TLS,
            fail_silently=False,
        )
        print("1")
        if mail_from is None:
            mail_from = config_obj.email_sender
        sent = EmailMessage(subject, message, mail_from, mail_to, connection=backend)
        if attachement:
            sent.attach_file(attachement)
        sent.send()
        print("2")
        return True
    except Exception as err:
        print(err)
        raise ValueError(err)
