from django.contrib import admin, messages
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import ngettext

from ebos2201.admin.a01_core_mas import T01BaseAdmin
from ebos2210.admin.a10_fin_link import T10Gld10Admin, T10Gld11Inline

from ..forms.f10_fin_gl import *
from ..forms.f10_fin_main import (
    T10Abr10Form,
    T10Alc10Form,
    T10Gla10Form,
    T10Jvm10Form,
    T10Tic10Form,
    T10Tic11Form,
)
from ..formset import T10Alc11InlineFormSet, T10Alc12InlineFormSet
from ..models.m10_fin_gl import *
from ..models.m10_fin_link import *
from ..views import *


class T10Jvm10Admin(T10Gld10Admin):
    list_display = (
        "vou_type",
        "vou_num",
        "vou_date",
        "amount",
        "comment1",
        "comment2",
        "post_flag",
        "delete_flag",
        "division",
        "print_pdf",
    )
    list_display_links = (
        "vou_type",
        "vou_num",
        "vou_date",
        "amount",
        "comment1",
        "comment2",
        "post_flag",
        "delete_flag",
        "division",
    )
    fields = (
        "prg_type",
        ("division", "vou_type", "vou_curr"),
        ("vou_date", "vou_num", "vou_hdr_ref"),
        "comment1",
        "comment2",
    )
    form = T10Jvm10Form
    inlines = [T10Gld11Inline]
    vou_type = "JVM"
    change_form_template = "ebos2210/admin/t10_jvm_ap_ar_change_form.html"


admin.site.register(T10Jvm10, T10Jvm10Admin)


class T10Unp10Admin(T10Gld10Admin):
    list_filter = ("division", "vou_type")
    vou_type = "UNP"
    inlines = [T10Gld11Inline]

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(T10Unp10, T10Unp10Admin)


class T10Alc11Inline(admin.TabularInline):
    model = T10Alc11
    formset = T10Alc11InlineFormSet

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T10Alc12Inline(admin.TabularInline):
    model = T10Alc12
    formset = T10Alc12InlineFormSet

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T10Alc10Admin(admin.ModelAdmin):
    form = T10Alc10Form
    list_display = (
        "division",
        "vou_type",
        "vou_num",
        "vou_date",
        "subledger",
        "date_choice",
        "date_from",
        "date_to",
        "cr_date_from",
        "cr_date_upto",
        "alloc_lock_flag",
    )
    fields = (
        "prg_type",
        ("division", "vou_type", "vou_date"),
        ("subledger", "coa", "vou_num"),
        ("date_from", "date_to", "alloc_lock_flag"),
        (
            "cr_date_from",
            "cr_date_upto",
        ),
    )
    inlines = [T10Alc11Inline, T10Alc12Inline]
    readonly_fields = ("alloc_lock_flag", "vou_num")
    change_form_template = "ebos2210/admin/t10_allocation_change_form.html"

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return (
                "division",
                "vou_type",
                "vou_date",
                "subledger",
                "coa",
                "date_choice",
                "date_from",
                "date_to",
                "cr_date_from",
                "cr_date_upto",
            ) + self.readonly_fields
        return self.readonly_fields

    def has_change_permission(self, request, obj=None):
        if obj and obj.alloc_lock_flag:
            return False
        return True

    class Media:
        css = {
            "all": (
                "css/admin.css",
                "css/inline-grid.css",
            ),
        }

    # url to get division data
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("add/fetch_t10cfg10/<int:division>/", self.get_division),
        ]
        return custom_urls + urls

    # function to fetch division data
    def get_division(self, request, division):
        div_curr = T01Div10.objects.get(id=division).currency
        result = {"division_curr": div_curr.id, "base_curr": div_curr.currency_name}

        return JsonResponse(result)

    # On add form fill vou_date as current date
    def get_changeform_initial_data(self, request):

        return {
            "vou_date": date.today(),
        }


# First Child Model -- Proxy Models


class T10Tb01Admin(T01BaseAdmin):
    list_display = (
        "division",
        "type_of_rpt",
        "year",
        "month",
        "csv_button",
        "pdf_button",
    )
    exclude = ("rpt_code", "day", "company", "as_of_date")
    readonly_fields = ("file_csv", "file_pdf")


class T10Ctb01Admin(admin.ModelAdmin):
    list_display = ("company", "type_of_rpt", "year", "month", "csv_button")
    exclude = ("rpt_code", "day", "division", "file_pdf")
    readonly_fields = ["file_csv"]

    class Media:
        css = {
            "all": ("css/admin.css",),
        }
        js = ("admin/js/common.js",)

    def csv_button(self, obj):
        return format_html(
            "<a href='{}' class='button print-btn'>Download</a>",
            settings.SITE_DOMAIN + settings.MEDIA_URL + str(obj.file_csv),
        )

    csv_button.short_description = "CSV file"


class T10Bs01Admin(T01BaseAdmin):
    list_display = (
        "division",
        "type_of_rpt",
        "year",
        "month",
        "csv_button",
        "pdf_button",
    )
    exclude = ("rpt_code", "day", "company", "as_of_date")
    readonly_fields = ("file_csv", "file_pdf")


class T10Pl01Admin(T01BaseAdmin):
    list_display = (
        "division",
        "type_of_rpt",
        "year",
        "month",
        "csv_button",
        "pdf_button",
    )
    exclude = ("rpt_code", "day", "company", "as_of_date")
    readonly_fields = ("file_csv", "file_pdf")


class T10Tbc01Admin(T01BaseAdmin):
    list_display = ("division", "year", "month", "pdf_button")
    exclude = ("rpt_code", "type_of_rpt", "day", "company", "file_csv", "as_of_date")
    readonly_fields = ["file_pdf"]


class T10CshFlow01Admin(T01BaseAdmin):
    list_display = ("division", "year", "month", "pdf_button")
    exclude = ("rpt_code", "type_of_rpt", "day", "company", "file_csv")
    readonly_fields = ["file_pdf"]


class T10TbDt01Admin(T01BaseAdmin):
    list_display = ("division", "as_of_date", "csv_button", "pdf_button")
    exclude = (
        "rpt_code",
        "type_of_rpt",
        "year",
        "month",
        "day",
        "company",
    )
    readonly_fields = (
        "file_csv",
        "file_pdf",
    )


class T10BsDt01Admin(T01BaseAdmin):
    list_display = ("division", "as_of_date", "csv_button", "pdf_button")
    exclude = ("rpt_code", "type_of_rpt", "day", "year", "month", "company")
    readonly_fields = ("file_csv", "file_pdf")


class T10PlDt01Admin(T01BaseAdmin):
    list_display = ("division", "as_of_date", "csv_button", "pdf_button")
    exclude = ("rpt_code", "type_of_rpt", "day", "company", "year", "month")
    readonly_fields = ("file_csv", "file_pdf")


# Second Child Model -- Proxy Models


class T10GlrB01Admin(T01BaseAdmin):
    form = T10GlrB01Form
    list_display = (
        "division",
        "coa",
        "subledger",
        "dt_from",
        "dt_upto",
        "csv_button",
        "pdf_button",
    )
    readonly_fields = ("file_csv", "file_pdf")


class T10Glc01Admin(T01BaseAdmin):
    form = T10Glc01Form
    list_display = ("division", "coa", "subledger", "dt_from", "dt_upto", "pdf_button")
    readonly_fields = ["file_pdf"]


class T10Stm01Admin(T01BaseAdmin):
    form = T10Stm01Form
    list_display = (
        "division",
        "subledger",
        "vou_curr",
        "dt_from",
        "dt_upto",
        "pdf_button",
    )
    readonly_fields = ["file_pdf"]


class T10Stm02Admin(T01BaseAdmin):
    form = T10Stm02Form
    list_display = (
        "division",
        "subledger",
        "vou_curr",
        "dt_from",
        "dt_upto",
        "pdf_button",
    )
    readonly_fields = ["file_pdf"]


class T10Dbk01Admin(T01BaseAdmin):
    list_display = ("division", "dt_from", "dt_upto", "pdf_button")
    exclude = (
        "rpt_code",
        "coa",
        "subledger",
        "vou_curr",
        "aging1",
        "aging2",
        "aging3",
        "file_csv",
    )
    readonly_fields = ["file_pdf"]


class T10SlCoa01Admin(T01BaseAdmin):
    form = T10SlCoa01Form
    list_display = ("division", "dt_upto", "coa", "pdf_button")
    readonly_fields = ["file_pdf"]


class T10SlCoa02Admin(T01BaseAdmin):
    form = T10SlCoa02Form
    list_display = ("division", "dt_from", "dt_upto", "coa", "pdf_button")
    readonly_fields = ["file_pdf"]


class T10LdgAcc01Admin(T01BaseAdmin):
    form = T10LdgAcc01Form
    list_display = ("division", "dt_upto", "subledger", "pdf_button")
    readonly_fields = ["file_pdf"]


class T10ChrAcc01Admin(T01BaseAdmin):
    form = T10ChrAcc01Form
    list_display = ("division", "dt_upto", "coa", "pdf_button")
    readonly_fields = ["file_pdf"]


class T10AgRpt01Admin(T01BaseAdmin):
    form = T10AgRpt01Form
    list_display = (
        "division",
        "dt_upto",
        "subledger",
        "aging1",
        "aging2",
        "aging3",
        "csv_button",
        "pdf_button",
    )
    readonly_fields = ("file_csv", "file_pdf")


admin.site.register(T10Tb01, T10Tb01Admin)
admin.site.register(T10Ctb01, T10Ctb01Admin)
admin.site.register(T10Bs01, T10Bs01Admin)
admin.site.register(T10Pl01, T10Pl01Admin)
admin.site.register(T10Tbc01, T10Tbc01Admin)
admin.site.register(T10CshFlow01, T10CshFlow01Admin)
admin.site.register(T10TbDt01, T10TbDt01Admin)
admin.site.register(T10BsDt01, T10BsDt01Admin)
admin.site.register(T10PlDt01, T10PlDt01Admin)
admin.site.register(T10GlrB01, T10GlrB01Admin)
admin.site.register(T10Glc01, T10Glc01Admin)
# admin.site.register(T10Alc10, T10Alc10Admin)
admin.site.register(T10Stm01, T10Stm01Admin)
admin.site.register(T10Stm02, T10Stm02Admin)
admin.site.register(T10Dbk01, T10Dbk01Admin)
admin.site.register(T10SlCoa01, T10SlCoa01Admin)
admin.site.register(T10SlCoa02, T10SlCoa02Admin)
admin.site.register(T10LdgAcc01, T10LdgAcc01Admin)
admin.site.register(T10ChrAcc01, T10ChrAcc01Admin)
admin.site.register(T10AgRpt01, T10AgRpt01Admin)
admin.site.register([T10Cfg10, T10Wor10])


# Financial year closing
class T10Fyc10Admin(admin.ModelAdmin):
    fields = [
        "division",
        "gl_code",
        "closing_year",
        "closing_opt",
        "vou_hdr_ref",
        "net_profit_loss",
    ]
    readonly_fields = ["net_profit_loss"]
    list_display = ["division", "closing_year", "closing_opt", "net_profit_loss"]

admin.site.register(T10Fyc10, T10Fyc10Admin)


class T10Gla10Admin(T10Alc10Admin, T01BaseAdmin):
    form = T10Gla10Form
    exclude = [
        "currency",
        "hdr_comment",
        "issued_to",
        "tot_amount",
        "line_narration",
        "chq_num",
        "chq_date",
    ]
    actions = ["print_alc_rpt"]

    """ Print Allocation Report custom action functionality """

    def print_alc_rpt(self, request, queryset):
        try:
            gl_alloc = queryset[0]
            gl_alloc_rpt = GlAllocRpt()
            gl_alloc_rpt.init_pdf(gl_alloc)
            # passing debit details
            for db_detail in T10Alc11.objects.filter(alloc_id=gl_alloc.id):
                gl11_detail = T10Gld11.objects.get(id=db_detail.debit_id)
                gl_alloc_rpt.render_details(db_detail, gl11_detail, "debit")
            # passing credit details
            for cr_detail in T10Alc12.objects.filter(alloc_id=gl_alloc.id):
                gl11_detail = T10Gld11.objects.get(id=cr_detail.credit_id)
                gl_alloc_rpt.render_details(cr_detail, gl11_detail, "credit")
            return gl_alloc_rpt.print_pdf(gl_alloc)
        except Exception as e:
            self.message_user(request, "No record found", messages.ERROR)

    print_alc_rpt.short_description = "Print Allocation Report"


admin.site.register(T10Gla10, T10Gla10Admin)


class T10Brc11Inline(admin.TabularInline):
    model = T10Brc11

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + (
                "bank_reco_id",
                "gl_id",
                "gl_date",
                "gl_debit",
                "gl_credit",
                "narration",
                "chq_num",
                "chq_date",
            )
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False


class T10Brc12Inline(admin.TabularInline):
    model = T10Brc12

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class T10Brc10Admin(T01BaseAdmin):
    list_display = ("division", "bank_account", "date_from", "date_to")
    inlines = [T10Brc11Inline]
    readonly_fields = ("opening_gl_bal", "closing_gl_bal", "reco_gl_bal")
    change_form_template = "ebos2210/admin/t10_bank_reco_change_form.html"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # editing an existing object
            return (
                "division",
                "bank_account",
                "date_from",
                "date_to",
                "opening_gl_bal",
                "closing_gl_bal",
                "reco_gl_bal",
                "opening_stmt_bal",
                "closing_stmt_bal",
                "import_bank_stmt",
            )
        return readonly_fields


class T10Mbr10Admin(T10Brc10Admin):
    fields = (
        ("division", "bank_account"),
        ("date_from", "date_to"),
        ("opening_gl_bal", "opening_stmt_bal"),
    )
    exclude = (
        "proxy_code",
        "import_bank_stmt",
    )


admin.site.register(T10Mbr10, T10Mbr10Admin)


class T10Abr10Admin(T10Brc10Admin):
    form = T10Abr10Form
    fields = (
        ("division", "bank_account"),
        ("date_from", "date_to"),
        ("opening_gl_bal", "opening_stmt_bal"),
        "import_bank_stmt",
    )

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        return inlines + [T10Brc12Inline]


admin.site.register(T10Abr10, T10Abr10Admin)

# Transfer Account Balance & Intercompany posting
class T10Tic11Admin(admin.TabularInline):
    model = T10Tic11
    readonly_fields = ["to_amt", "alloc_date"]
    form = T10Tic11Form
    extra = 1


class T10Tic10Admin(admin.ModelAdmin):
    form = T10Tic10Form
    readonly_fields = ["from_amt", "flag_db_cr"]
    inlines = [T10Tic11Admin]
    actions = ["post_intercompany_balance"]
    change_form_template = "ebos2210/admin/t10_intercompany_change_form.html"

    def get_division_data(self, request, company):
        divisions = list(
            T01Div10.objects.filter(company_id=company).values("id", "division_name")
        )
        return JsonResponse({"divisions": divisions})

    def get_coa_sl_data(self, request, division):
        coas = list(
            T01Coa10.objects.filter(division_id=division, coa_control="2").values(
                "id", "account_name"
            )
        )
        subledgers = list(
            T01Sld10.objects.filter(division_id=division).values("id", "subledger_name")
        )

        return JsonResponse({"coas": coas, "subledgers": subledgers})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("add/get_division/<int:company>/", self.get_division_data),
            path("add/get_coa_sl/<int:division>/", self.get_coa_sl_data),
        ]
        return custom_urls + urls

    """Intercompany / division balance posting custom action functionality"""

    @admin.action(description="Post intercompany / division balance")
    def post_intercompany_balance(self, request, queryset):
        posted = 0
        intercom_list = []

        for q in queryset:
            if q.from_amt == 0:
                intercom_list.append(q.ic_coa)
            else:
                if q.post_intercompany_balance():
                    posted += 1

        if posted > 0:
            self.message_user(
                request,
                ngettext(
                    "%d successfully posted.",
                    "%d successfully posted.",
                    posted,
                )
                % posted,
                messages.SUCCESS,
            )
        else:
            self.message_user(request, "Something wrong", messages.ERROR)

        if intercom_list.exists():
            intercom_str = ",".join(intercom_list)
            self.message_user(
                request,
                f"Zero amount, nothing to allocate for {intercom_str}",
                messages.ERROR,
            )


admin.site.register(T10Tic10, T10Tic10Admin)
