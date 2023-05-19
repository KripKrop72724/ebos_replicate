import random
from datetime import timedelta

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ebos2201.notification import send_email

from ..models.m01_core_mas import User


# Create your views here.
def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render())


@csrf_exempt
def sendemail(request):
    if request.method == "POST":
        fullname = request.POST["fullname"]
        email = request.POST["email"]
        company_name = request.POST["company_name"]
        contact = request.POST["contact"]
        template = loader.get_template("index.html")

        subject = "Demo Request Acknowledgment"
        message = (
            "Hi "
            + str(fullname)
            + ",\n\nThank you! for the Demo request.\nOne of our consultant will contact you to setup the system as per your business need.\nWelcome to Aiems\n\nBest Regards,\nAiems Team"
        )
        recipient_list = [
            request.POST["email"],
        ]
        # Send Email to user
        send_email(subject, message, recipient_list)

        success = True
        context = {
            "success": success,
        }

        # Send email to self
        m_subject = "Demo Request"
        m_message = (
            "Hi, Here is a Demo Request \n\n Name:"
            + str(fullname)
            + "\n Email: "
            + str(email)
            + "\n Company Name: "
            + str(company_name)
            + "\n Contact Number: "
            + str(contact)
        )
        recipient_list = [
            "800aiems@gmail.com",
        ]
        send_email(m_subject, m_message, recipient_list)
    else:
        return HttpResponseRedirect(reverse("index"))
    return HttpResponse(template.render(context, request))


@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        otpdevice = request.POST["otp_device"]
        request.session["username"] = username
        request.session["password"] = password
        otp = random.randint(100000, 999999)
        if otpdevice == "email":
            user_login = authenticate(username=username, password=password)
            if user_login is None:
                context = {
                    "login_msg": "Username or Password is wrong",
                    "class": "danger",
                }
                index_template = loader.get_template("index.html")
                return HttpResponse(index_template.render(context, request))
            elif user_login is not None:
                user_email = user_login.email
                if user_email:
                    subject = "OTP Token"
                    message = "OTP: " + str(otp) + ""
                    recipient_list = [
                        user_email,
                    ]

                    # Save OTP to User model
                    now = timezone.now()
                    expire_at = now + timedelta(minutes=5)
                    User.objects.filter(username=username).update(
                        otp=otp, otp_expire_at=expire_at
                    )

                    # Send Email to user
                    send_email(subject, message, recipient_list)
                    verify_template = loader.get_template("verify.html")
                    return HttpResponse(verify_template.render())
                else:
                    index_template = loader.get_template("index.html")
                    context = {
                        "login_msg": "Email is not registered",
                        "class": "danger",
                    }
                    return HttpResponse(index_template.render(context, request))

        elif otpdevice == "phone":
            pass

        elif otpdevice == "call":
            pass

    else:
        return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        first = request.POST["first"]
        second = request.POST["second"]
        third = request.POST["third"]
        fourth = request.POST["fourth"]
        fifth = request.POST["fifth"]
        sixth = request.POST["sixth"]
        otp = (
            ""
            + str(first)
            + str(second)
            + str(third)
            + str(fourth)
            + str(fifth)
            + str(sixth)
            + ""
        )
        user_login = authenticate(
            username=request.session["username"], password=request.session["password"]
        )
        if user_login is not None:
            if user_login.otp == otp:
                now = timezone.now()
                if now > user_login.otp_expire_at:
                    verify_template = loader.get_template("verify.html")
                    context = {"otp_msg": "OTP Expired", "class": "danger"}
                    return HttpResponse(verify_template.render(context, request))
                else:
                    login(request, user_login)
                    return HttpResponseRedirect(reverse("admin:index"))
            elif user_login.otp != otp:
                response = "OTP is not Valid"
                verify_template = loader.get_template("verify.html")
                context = {"otp_msg": "OTP is not valid", "class": "danger"}
                return HttpResponse(verify_template.render(context, request))
    else:
        return HttpResponseRedirect(reverse("index"))
