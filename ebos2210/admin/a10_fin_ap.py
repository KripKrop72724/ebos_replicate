from gettext import ngettext

from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from pyexpat.errors import messages

from ebos2201.admin.a01_fin_mas import T01BaseAdmin
from ebos2210.admin.a10_fin_link import T10Gld12Inline, T10Tib10Admin

from ..forms.f10_fin_main import (
    ApiInlineForm,
    BpvInlineForm,
    CpvInlineForm,
    CrnInlineForm,
    T10Api10Form,
    T10Apv10Form,
    T10Bpv10Form,
    T10Cpv10Form,
    T10Crn10Form,
    T10Pal10Form,
    T10Pps10Form,
    T10Tip10Form,
)
from ..models.m10_fin_ap import *
from ..views.v10_cheque_layout_print import *
from ..views.v10_voc_print import *
from .a10_fin_gl import T10Alc10Admin, T10Gld10Admin, T10Gld11Inline


# Bank payment voucher
class BpvT10Gld11Inline(T10Gld11Inline):
    form = BpvInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Bpv10Admin(T10Gld10Admin):
    list_display = (
        "vou_type",
        "vou_num",
        "vou_date",
        "amount",
        "comment1",
        "comment2",
        "subledger",
        "issued_to",
        "vou_hdr_ref",
        "post_flag",
        "delete_flag",
        "division",
        "print_pdf",
        "print_cheque",
    )
    form = T10Bpv10Form
    inlines = [BpvT10Gld11Inline]
    vou_type = "BPV"
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"
    actions = ["post_voucher", "unpost_voucher", "cancel_cheque"]

    def print_pdf(self, obj):
        return format_html(
            "<a class='button print-btn' onclick='print_voucher_js({})'>Print BPV</a>",
            obj.id,
        )

    def print_cheque(self, obj):
        return format_html(
            "<a class='button print-btn' onclick='print_cheque_js({})'>Print cheque</a>",
            obj.id,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("cheque_print_button/<int:id>", self.cheque_print),
        ]
        return custom_urls + urls

    """ Print Cheque custom functionality """

    def cheque_print(self, request, id):
        """
        Read T10Gld10_ID,  pass to T10Gld11 lines and check if any COA_ID is found in T10Chq10 (meaning there is a layout)
        if chq_id is blank
            use this layout, pass values from T10Gld11 (BPV) and print cheque as per layout.
            Store the data in T10Chq20, and copy the ID in T01Gld11 (to indicate the cheque is already printed)
        Else
            message "cheque already printed"

        Add new action item  'Cancel Cheque'
            on selecting a row and click 'cancel cheque' read the chq_id from T10Gld11 >> find the id in T10Chq20
            mark the status as 'cancelled' in T10Chq20
            update T10Gld11.chq_id = blank
        """
        file_path = CHQLayout.init_pdf(request, T10Gld10.objects.get(id=id))

        if file_path:
            file_url = settings.SITE_DOMAIN + settings.MEDIA_URL + file_path
        else:
            file_url = None
        return JsonResponse({"file_path": file_url})

    """ Cancel Cheque custom action functionality """

    def cancel_cheque(self, request, queryset):
        CHQLayout.cancel_pdf(request, queryset[0])

    cancel_cheque.short_description = "Cancel Cheque"


# Cash payment voucher
class CpvT10Gld11Inline(T10Gld11Inline):
    form = CpvInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Cpv10Admin(T10Gld10Admin):
    form = T10Cpv10Form
    vou_type = "CPV"
    inlines = [CpvT10Gld11Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"


# Credit Note
class CrnT10Gld11Inline(T10Gld11Inline):
    form = CrnInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Crn10Admin(T10Gld10Admin):
    form = T10Crn10Form
    prg_type = "CRN"
    inlines = [CrnT10Gld11Inline, T10Gld12Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"
    actions = ["post_creditnote", "unpost_creditnote", "print_creditnote"]

    """Post credit note custom action functionality"""

    @admin.action(description="Post credit note")
    def post_creditnote(self, request, queryset):
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

    """Unpost credit note custom action functionality"""

    @admin.action(description="Unpost credit note")
    def unpost_creditnote(self, request, queryset):
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

    def print_creditnote(self, request, queryset):
        for obj in queryset:
            vou_num = obj.vou_num
            vou_type = obj.vou_type
            vou_date = obj.vou_date
            voucher, voc_name = VOCPrint.voc_print(vou_num, vou_type, vou_date)
            return voucher

    print_creditnote.short_description = "Print Credit Note"


admin.site.register(T10Bpv10, T10Bpv10Admin)
admin.site.register(T10Cpv10, T10Cpv10Admin)
admin.site.register(T10Crn10, T10Crn10Admin)

# Account Payable Invoice
class ApiT10Gld11Inline(T10Gld11Inline):
    form = ApiInlineForm
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )


class T10Api10Admin(T10Gld10Admin):
    form = T10Api10Form
    prg_type = "API"
    inlines = [ApiT10Gld11Inline, T10Gld12Inline]
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"


admin.site.register(T10Api10, T10Api10Admin)


class T10Pal10Admin(T10Alc10Admin, T01BaseAdmin):
    form = T10Pal10Form
    exclude = [
        "currency",
        "hdr_comment",
        "issued_to",
        "tot_amount",
        "line_narration",
        "chq_num",
        "chq_date",
    ]


admin.site.register(T10Pal10, T10Pal10Admin)


class T10Apv10Admin(T10Alc10Admin, T01BaseAdmin):
    form = T10Apv10Form
    change_form_template = "ebos2210/admin/t10_alc_div_change_form.html"


admin.site.register(T10Apv10, T10Apv10Admin)


# Tax invoice payment
class T10Tip10Admin(T10Tib10Admin):
    form = T10Tip10Form
    fields = (
        ("division", "inv_curr", "inv_type"),
        ("subledger", "gl_code"),
        ("inv_date", "due_date", "inv_num"),
        "hdr_ref",
        "hdr_comment",
        "pmt_term",
        "prg_type",
    )


admin.site.register(T10Tip10, T10Tip10Admin)


""" PDC inline model """


class T10Ppd11InlineAdmin(admin.TabularInline):
    model = T10Ppd11
    fields = (
        "gl_id",
        "vou_type",
        "vou_date",
        "amount",
        "vou_curr",
        "hdr_ref",
        "comment",
        "chq_num",
        "chq_date",
        "chq_status",
    )
    readonly_fields = (
        "gl_id",
        "vou_type",
        "vou_date",
        "amount",
        "vou_curr",
        "hdr_ref",
        "comment",
        "chq_num",
        "chq_date",
    )
    extra = 0
    max_num = 0

    def has_delete_permission(self, request, obj=None):
        return False


class T10Pdc10Admin(T01BaseAdmin):
    fields = (
        ("division", "gl_date_from", "gl_date_to"),
        ("pdc_coa", "bank_coa", "gl_code"),
    )
    exclude = ("pdc_code",)
    list_display = ("division", "gl_date_from", "gl_date_to", "pdc_coa", "bank_coa")
    inlines = [
        T10Ppd11InlineAdmin,
    ]


admin.site.register(T10PdcAp10, T10Pdc10Admin)


# Prepayment Amortization (schedule)
class T10Pps10Admin(T01BaseAdmin):
    form = T10Pps10Form
    readonly_fields = (
        "prepay_amt",
        "allocated_amt",
        "status",
        "allocated_dt",
    )
    list_display = [
        "division",
        "voucher_id",
        "prepay_coa",
        "prepay_amt",
        "frequency",
        "allocated_amt",
        "prepay_schedule_from",
        "allocated_dt",
        "status",
    ]
    actions = ["prepayment_posting"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("division", "voucher_id"),
                    ("prepay_coa", "allocated_coa"),
                    ("frequency", "prepay_months"),
                    ("prepay_schedule_from", "allocated_dt"),
                    ("prepay_amt", "allocated_amt"),
                    ("gl_code", "status"),
                )
            },
        ),
    )

    def get_list_filter(self, request):
        filter_fields = super().get_list_filter(request)
        return filter_fields + [
            "status",
            ("allocated_dt", DateFieldListFilter),
        ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            return (
                "division",
                "voucher_id",
                "prepay_coa",
                "allocated_coa",
                "frequency",
                "prepay_months",
                "gl_code",
            ) + readonly_fields
        return readonly_fields

    """Generate prepayment posting custom action functionality"""

    @admin.action(description="Generate prepayment posting")
    def prepayment_posting(self, request, queryset):
        posted = 0
        for q in queryset:
            if q.status != "active":
                self.message_user(
                    request, "The schedule already closed", messages.ERROR
                )
            else:
                try:
                    if q.prepayment_posting():
                        posted += 1
                except Exception as e:
                    self.message_user(request, e, messages.ERROR)

        mess = messages.SUCCESS if posted > 0 else messages.ERROR
        self.message_user(
            request,
            ngettext(
                "%d schedule was successfully posted.",
                "%d schedules were successfully posted.",
                posted,
            )
            % posted,
            mess,
        )


admin.site.register(T10Pps10, T10Pps10Admin)


class T10Chq11Chq10Inline(admin.TabularInline):
    model = T10Chq11
    fields = ("chq_book_ref", "begin_num", "end_num", "Book_Status", "used_num")
    readonly_fields = ["used_num"]


class T10Chq20Chq10Inline(admin.TabularInline):
    model = T10Chq20
    fields = (
        "bpv_id",
        "chq_book_id",
        "chq_num",
        "chq_amt",
        "chq_status",
        "status_note",
    )
    readonly_fields = ["bpv_id"]


class T10Chq10Admin(admin.ModelAdmin):
    fields = (
        "bank_coa",
        "bank_name",
        "chq_image",
        "date_format",
        "date_xpixel",
        "date_ypixel",
        "pay_to_xpixel",
        "pay_to_ypixel",
        "amt_num_xpixel",
        "amt_num_ypixel",
        "amt_txt1_xpixel",
        "amt_txt1_ypixel",
        "amt_txt2_xpixel",
        "amt_txt2_ypixel",
    )
    list_display = (
        "bank_coa",
        "bank_name",
        "chq_image",
        "date_format",
        "date_xpixel",
        "date_ypixel",
        "pay_to_xpixel",
        "pay_to_ypixel",
        "amt_num_xpixel",
        "amt_num_ypixel",
        "amt_txt1_xpixel",
        "amt_txt1_ypixel",
        "amt_txt2_xpixel",
        "amt_txt2_ypixel",
    )
    inlines = [T10Chq11Chq10Inline, T10Chq20Chq10Inline]


admin.site.register(T10Chq10, T10Chq10Admin)
