from datetime import date

from django.contrib import admin, messages
from django.contrib.admin import DateFieldListFilter
from django.http import JsonResponse
from django.urls import path
from django.utils.translation import ngettext

from ebos2201.admin.a01_fin_mas import T01BaseAdmin
from ebos2201.notification import send_email
from ebos2201.utils import get_payment_link, save_payment
from ebos2210.admin.a10_fin_link import T10Gld12Inline, T10Tib10Admin
from ebos2210.forms.f10_fin_main import T10Arv10Form, T10Ral10Form, T10Tir10Form
from ebos2210.models.m10_fin_ar import *
from ebos2210.views.v10_voc_print import VOCPrint

from ..forms import (
    AriInlineForm,
    BrvInlineForm,
    CrvInlineForm,
    DbnInlineForm,
    T10Ari10Form,
    T10Brv10Form,
    T10Crv10Form,
    T10Dbn10Form,
    T10Rin10Form,
)
from .a10_fin_ap import T10Pdc10Admin, T10Ppd11InlineAdmin
from .a10_fin_gl import T10Alc10Admin, T10Gld10Admin, T10Gld11Inline


# Bank receipt voucher
class BrvT10Gld11Inline(T10Gld11Inline):
    form = BrvInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Brv10Admin(T10Gld10Admin):
    form = T10Brv10Form
    vou_type = "BRV"
    inlines = [BrvT10Gld11Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"


# Cash receipt voucher
class CrvT10Gld11Inline(T10Gld11Inline):
    form = CrvInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Crv10Admin(T10Gld10Admin):
    form = T10Crv10Form
    vou_type = "CRV"
    inlines = [CrvT10Gld11Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"


admin.site.register(T10Brv10, T10Brv10Admin)
admin.site.register(T10Crv10, T10Crv10Admin)


# Debit Note
class DbnT10Gld11Inline(T10Gld11Inline):
    form = DbnInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Dbn10Admin(T10Gld10Admin):
    form = T10Dbn10Form
    vou_type = "DBN"
    inlines = [DbnT10Gld11Inline, T10Gld12Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"
    actions = ["post_debitnote", "unpost_debitnote", "print_debitnote"]

    # def __init__(self, **kwargs):
    #     super(T10BaseModel, self).__init__(model=T10Dbn10)

    """Post debit note custom action functionality"""

    @admin.action(description="Post debit note")
    def post_debitnote(self, request, queryset):
        posted = 0
        for q in queryset:
            if q.post_flag == False:
                try:
                    T10Gld10.post_voucher(
                        voc_num=q.vou_num, voc_type=q.vou_type, vou_date=q.vou_date
                    )
                    posted += 1
                except Exception as e:
                    raise ValueError(e)

        mess = messages.SUCCESS if posted > 0 else messages.ERROR
        self.message_user(
            request,
            ngettext(
                "%d voucher was successfully posted.",
                "%d vouchers were successfully posted.",
                posted,
            )
            % posted,
            mess,
        )

    """Unpost debit note custom action functionality"""

    @admin.action(description="Unpost debit note")
    def unpost_debitnote(self, request, queryset):
        unposted = 0
        for q in queryset:
            if q.post_flag == True:
                try:
                    T10Gld10.unpost_voucher(
                        voc_num=q.vou_num, voc_type=q.vou_type, vou_date=q.vou_date
                    )
                    unposted += 1
                except:
                    pass

        mess = messages.SUCCESS if unposted > 0 else messages.ERROR
        self.message_user(
            request,
            ngettext(
                "%d voucher was successfully unposted.",
                "%d vouchers were successfully unposted.",
                unposted,
            )
            % unposted,
            mess,
        )

    """ Print Voucher custom action functionality """

    def print_debitnote(self, request, queryset):
        for obj in queryset:
            vou_num = obj.vou_num
            vou_type = obj.vou_type
            vou_date = obj.vou_date
            voucher, voc_name = VOCPrint.voc_print(vou_num, vou_type, vou_date)
            return voucher

    print_debitnote.short_description = "Print debit Note"


admin.site.register(T10Dbn10, T10Dbn10Admin)


# Account Receivable Invoice
class AriT10Gld11Inline(T10Gld11Inline):
    form = AriInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Ari10Admin(T10Gld10Admin):
    form = T10Ari10Form
    vou_type = "ARI"
    inlines = [AriT10Gld11Inline, T10Gld12Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"
    actions = [
        "post_voucher",
        "unpost_voucher",
        "print_invoice",
        "send_payment_link",
        "resend_payment_link",
    ]

    """ Print Invoice custom action functionality """

    def print_invoice(self, request, queryset):
        for obj in queryset:
            vou_num = obj.vou_num
            vou_type = obj.vou_type
            vou_date = obj.vou_date
            voucher, voc_name = VOCPrint.voc_print(vou_num, vou_type, vou_date)
            return voucher

    print_invoice.short_description = "Print Invoice"

    """Send payment link custom action functionality"""

    @admin.action(description="Send payment link")
    def send_payment_link(self, request, queryset):
        posted = 0
        err_msg = "Unknown Error, please contact technical support"
        model_name = queryset.model.__name__

        for q in queryset:

            if q.paid_flag:
                err_msg = "Already paid."
            elif q.email_sent_flag:
                err_msg = "Already sent payment link."
            elif q.subledger is None:
                err_msg = "Account subledger NOT found"
            elif q.subledger and q.subledger.primary_email in ["", None]:
                err_msg = "No email found in Accounts Subledger"
            else:
                description = f"Invoice: {q.vou_num}"
                payment_link = get_payment_link(
                    amount=q.total_amount,
                    currency=q.vou_curr.currency_code,
                    product=description,
                )

                subject = "Invoice payment link"
                msg = f"Hi, Please click on the link to pay {payment_link['url']}"

                if send_email(
                    subject,
                    msg,
                    [
                        q.subledger.primary_email,
                    ],
                ):
                    posted += 1
                    # save data into databse
                    save_payment(
                        payment_link,
                        description,
                        model_name,
                        q.id,
                        q.total_amount,
                        q.vou_curr,
                    )

                    q.email_sent_flag = True
                    q.save()
                else:
                    err_msg = "Email NOT sent, please contact technical support"

        if posted > 0:
            self.message_user(
                request,
                ngettext(
                    "%d link successfully sent.",
                    "%d links successfully sent.",
                    posted,
                )
                % posted,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, err_msg, messages.ERROR)

    """Resend payment link custom action functionality"""

    @admin.action(description="Resend payment link")
    def resend_payment_link(self, request, queryset):
        posted = 0
        err_msg = "Unknown Error, please contact technical support"
        model_name = queryset.model.__name__

        for q in queryset:
            if q.paid_flag:
                err_msg = "Already paid."
            elif q.email_sent_flag is False:
                err_msg = "Payment link NOT sent, Resend is not possible"
            elif q.subledger is None:
                err_msg = "Account subledger NOT found"
            elif q.subledger and q.subledger.primary_email in ["", None]:
                err_msg = "No email in Accounts subledger"
            else:
                description = f"Invoice: {q.vou_num}"

                t01stp10_obj = T01Stp10.objects.get(
                    src_model=model_name, src_model_id=q.id
                )
                if date.today() > t01stp10_obj.expired_date:
                    payment_link = get_payment_link(
                        amount=q.total_amount,
                        currency=q.vou_curr.currency_code,
                        product=description,
                    )
                    t01stp10_obj.payment_link = payment_link["url"]
                    t01stp10_obj.expired_date = date.today() + timedelta(days=7)
                    t01stp10_obj.save()

                    pay_url = payment_link["url"]
                else:
                    pay_url = t01stp10_obj.payment_link

                subject = "Invoice payment link"
                msg = f"Hi, Please click on the link to pay {pay_url}"

                if send_email(
                    subject,
                    msg,
                    [
                        q.subledger.primary_email,
                    ],
                ):
                    posted += 1
                else:
                    err_msg = "Email NOT sent, please contact technical support"

        if posted > 0:
            self.message_user(
                request,
                ngettext(
                    "%d link successfully resent.",
                    "%d links successfully resent.",
                    posted,
                )
                % posted,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, err_msg, messages.ERROR)


admin.site.register(T10Ari10, T10Ari10Admin)


class T10Ral10Admin(T10Alc10Admin, T01BaseAdmin):
    form = T10Ral10Form
    exclude = [
        "currency",
        "hdr_comment",
        "issued_to",
        "tot_amount",
        "line_narration",
        "chq_num",
        "chq_date",
    ]


admin.site.register(T10Ral10, T10Ral10Admin)


class T10Arv10Admin(T10Alc10Admin, T01BaseAdmin):
    form = T10Arv10Form
    change_form_template = "ebos2210/admin/t10_alc_div_change_form.html"


admin.site.register(T10Arv10, T10Arv10Admin)

admin.site.register(T10Rpd10, T10Pdc10Admin)

# Tax invoice AR
class T10Tir10Admin(T10Tib10Admin):
    form = T10Tir10Form


admin.site.register(T10Tir10, T10Tir10Admin)

# Recurring Sales Invoice
class T10Rin10Admin(T01BaseAdmin):
    form = T10Rin10Form
    readonly_fields = ["status", "recurring_from", "allocated_dt"]
    list_display = [
        "division",
        "invoice",
        "contract_months",
        "frequency",
        "recurring_from",
        "allocated_dt",
        "status",
    ]
    fields = (
        ("division", "invoice", "contract_months"),
        ("frequency", "recurring_from", "allocated_dt"),
        "status",
    )
    actions = ["terminate_contract", "recurring_invoice"]

    def get_list_filter(self, request):
        filter_fields = super().get_list_filter(request)
        return filter_fields + [
            "status",
            ("allocated_dt", DateFieldListFilter),
        ]

    def has_change_permission(self, request, obj=None):
        if obj and obj.id:
            return False
        return True

    """Terminate contract custom action functionality"""

    @admin.action(description="Terminate contract")
    def terminate_contract(self, request, queryset):
        queryset.filter(status="active").update(status="terminated")
        self.message_user(
            request, "Successfully terminated the selected contracts", messages.SUCCESS
        )

    """Generate recurring invoice custom action functionality"""

    @admin.action(description="Generate recurring invoice")
    def recurring_invoice(self, request, queryset):
        posted = 0
        errors = False
        for q in queryset:
            if q.status in ["closed", "terminate"]:
                self.message_user(request, f"The invoice is {q.status}", messages.ERROR)
                errors = True
            elif q.recurring_from != date.today():
                self.message_user(
                    request,
                    "Only can generate invoice for current date",
                    messages.ERROR,
                )
                errors = True
            else:
                if q.gernerate_recurring_invoice():
                    posted += 1

        if posted > 0:
            self.message_user(
                request,
                ngettext(
                    "%d successfully generated.",
                    "%d successfully generated.",
                    posted,
                )
                % posted,
                messages.SUCCESS,
            )
        elif not errors:
            self.message_user(
                request,
                "Unknown Error, please contact technical support",
                messages.ERROR,
            )


admin.site.register(T10Rin10, T10Rin10Admin)
