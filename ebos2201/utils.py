import calendar
from datetime import date, timedelta

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ebos2201.middleware import Thread_Local


# Change the folder name depend on the tanent
def get_path(filename: str) -> str:
    # For multi tanent
    if subdir := getattr(Thread_Local, "DB"):
        subdir = f"{subdir}"
    else:
        subdir = "default"

    return f"{subdir}/{filename}"


# Pass a date and return the last date of the month
def get_last_day_of_month(day: date) -> date:
    next_month = day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


#  Get how many days in a given month and year
def get_no_of_days(month: int, year: int) -> int:
    return calendar.monthrange(year, month)[1]


# #  Map the calender month with the company financial year begining month
def get_fin_period(calender_date: date, fin_begin_month: int):
    calender_month = calender_date.month
    calender_year = calender_date.year

    period_diff = fin_begin_month - 1
    fin_period = calender_month - period_diff
    fin_year = calender_year
    if fin_period <= 0:
        fin_period = fin_period + 12
        fin_year = calender_year - 1
    return fin_period, fin_year


# #  Create payment link
def get_payment_link(amount, currency, product):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    return stripe.PaymentLink.create(
        line_items=[
            {
                "price": stripe.Price.create(
                    unit_amount=round(amount * 100),
                    currency=currency,
                    product=stripe.Product.create(name=product),
                ),
                "quantity": 1,
            }
        ]
    )


# #  Payment details store into database
def save_payment(pay_link, description, src_model, ref_id, amt, curr):
    from ebos2201.models.m01_fin_mas import T01Stp10

    T01Stp10.objects.create(
        payment_id=pay_link["id"],
        description=description,
        src_model=src_model,
        src_model_id=ref_id,
        amount=amt,
        currency=curr,
        payment_link=pay_link["url"],
        expired_date=date.today() + timedelta(days=7),
    )

    return 1


# #  Payment success confirmation webhoo
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return JsonResponse({"error": str(e), "status": 400})
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({"error": str(e), "status": 400})

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")

        objects = event.data.object

        # Update payment link as expired
        stripe.PaymentLink.modify(
            objects.payment_link,
            active=False,
        )

        # update the stripe payment model
        t01stp10_obj = "ebos2201.T01Stp10".objects.filter(payment_id=objects.id)
        t01stp10_obj.update(
            email=objects.customer_details.email,
            payment_method_types=objects.payment_method_types[0],
            payment_status=objects.payment_status,
        )

        # update the source model paid status
        model = t01stp10_obj[0].src_model
        model.objects.filter(id=t01stp10_obj[0].src_model_id).update(paid_flag=True)

    # TODO: run some custom code here
    return JsonResponse({"success": True, "status": 200})
