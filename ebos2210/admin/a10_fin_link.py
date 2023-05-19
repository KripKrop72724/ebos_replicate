import datetime
from decimal import Decimal

from django.contrib import admin, messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import F, Sum
from django.forms import BaseInlineFormSet
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from ebos2201.admin.a01_fin_mas import T01BaseAdmin
from ebos2201.models.m01_core_mas import T01Cur11, T01Div10, T01Voc11, T01Voc12
from ebos2201.models.m01_fin_mas import T01Coa10, T01Sld10
from ebos2210.forms.f10_fin_link import T10Gld11Form
from ebos2210.models.m10_fin_gl import T10Cfg10
from ebos2210.models.m10_fin_link import (
    T10Abs10,
    T10Gld10,
    T10Gld11,
    T10Gld12,
    T10Pst10,
    T10Pst11,
    T10PurchaseTax,
    T10SalesTax,
    T10Sbs10,
    T10Tax10,
    T10Tax11,
    T10Tib11,
)
from ebos2210.utils.u10_action_handler import gl_voucher_print
from ebos2210.views.v10_tax_return import TaxReturnRpt


class T10Pst11Inline(admin.TabularInline):
    model = T10Pst11
    fields = (
        "amount_field",
        "coa_code",
        "flag_db_cr",
        "subledger_field",
        "voc_narration_dict",
        "allocation_flag",
    )


class T10Pst10Admin(admin.ModelAdmin):
    inlines = [T10Pst11Inline]


admin.site.register(T10Pst10, T10Pst10Admin)

# GL voucher
class T10Gld11InlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(T10Gld11InlineFormSet, self).__init__(*args, **kwargs)

        # vou_coa >> vou_subledger
        try:
            for i, form in enumerate(self.forms):
                # Enable disable the debit credit field based on vou_curr
                if self.data.get("division") and self.data.get("vou_curr"):
                    if T01Div10.objects.get(
                        id=self.data["division"]
                    ).currency.id == int(self.data["vou_curr"]):
                        form.fields["fcurr_debit"].disabled = True
                        form.fields["fcurr_credit"].disabled = True
                    else:
                        form.fields["bcurr_debit"].disabled = True
                        form.fields["bcurr_credit"].disabled = True
                else:
                    if self.instance.division and self.instance.vou_curr:
                        if self.instance.division.currency == self.instance.vou_curr:
                            form.fields["fcurr_debit"].disabled = True
                            form.fields["fcurr_credit"].disabled = True
                        else:
                            form.fields["bcurr_debit"].disabled = True
                            form.fields["bcurr_credit"].disabled = True
        except Exception as e:
            pass

    @property
    def empty_form(self):
        form = super().empty_form

        try:
            vou_type_val = None
            if self.instance.vou_type:
                vou_type_val = self.instance.vou_type.voucher_name
            else:
                if self.data.get("vou_type"):
                    vou_type_val = T01Voc11.objects.get(
                        id=self.data["vou_type"]
                    ).voucher_name

            if vou_type_val:
                sl_type = vou_type_val.subledger_type
                sl_cat = vou_type_val.subledger_cat

                # vou_type >> vou_coa
                vou_coa_obj = T01Coa10.objects.exclude(coa_control=1)

                if sl_cat:
                    vou_coa_obj = vou_coa_obj.filter(coa_sl_cat=sl_cat)
                if sl_type:
                    vou_coa_obj = vou_coa_obj.filter(coa_sl_type=sl_type)

                form.fields["vou_type_id"].initial = vou_type_val.id

        except Exception as e:
            pass

        return form

    def clean(self):
        super(T10Gld11InlineFormSet, self).clean()
        total_bcurr_debit = Decimal("0.00")
        total_bcurr_credit = Decimal("0.00")
        total_fcurr_debit = Decimal("0.00")
        total_fcurr_credit = Decimal("0.00")
        fcurr = False

        if self.instance.division and self.instance.vou_curr:
            if self.instance.division.currency != self.instance.vou_curr:
                fcurr = True

        for form in self.forms:
            if not form.is_valid():
                return  # other errors exist, so don't bother
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                # Convert amount field none to 0.00
                if form.cleaned_data["bcurr_debit"] is None:
                    form.cleaned_data["bcurr_debit"] = Decimal(0.00)
                if form.cleaned_data["bcurr_credit"] is None:
                    form.cleaned_data["bcurr_credit"] = Decimal(0.00)

                if form.cleaned_data["fcurr_debit"] is None:
                    form.cleaned_data["fcurr_debit"] = Decimal(0.00)
                if form.cleaned_data["fcurr_credit"] is None:
                    form.cleaned_data["fcurr_credit"] = Decimal(0.00)

                # Negative value validation
                if (
                    Decimal(form.cleaned_data["bcurr_debit"]) < Decimal(0.00)
                    or Decimal(form.cleaned_data["bcurr_credit"]) < Decimal(0.00)
                    or Decimal(form.cleaned_data["fcurr_debit"]) < Decimal(0.00)
                    or Decimal(form.cleaned_data["fcurr_credit"]) < Decimal(0.00)
                ):
                    raise ValidationError("Negative value is not allowed.")

                if fcurr:
                    if Decimal(form.cleaned_data["fcurr_debit"]) == Decimal(
                        "0.00"
                    ) and Decimal(form.cleaned_data["fcurr_credit"]) == Decimal("0.00"):
                        raise ValidationError(
                            "Fcurr debit and credit both cannot be 0."
                        )
                    if Decimal(form.cleaned_data["fcurr_debit"]) > Decimal(
                        "0.00"
                    ) and Decimal(form.cleaned_data["fcurr_credit"]) > Decimal("0.00"):
                        raise ValidationError(
                            "Fcurr debit and credit both cannot be greater than 0."
                        )

                    if form.cleaned_data["fcurr_debit"]:
                        total_fcurr_debit += form.cleaned_data["fcurr_debit"]
                    if form.cleaned_data["fcurr_credit"]:
                        total_fcurr_credit += form.cleaned_data["fcurr_credit"]

                else:
                    # in one line, should have debit or credit not both (both cannot be 0, both cannot be > 0)
                    if Decimal(form.cleaned_data["bcurr_debit"]) == Decimal(
                        "0.00"
                    ) and Decimal(form.cleaned_data["bcurr_credit"]) == Decimal("0.00"):
                        raise ValidationError(
                            "Bcurr debit and credit both cannot be 0."
                        )
                    if Decimal(form.cleaned_data["bcurr_debit"]) > Decimal(
                        "0.00"
                    ) and Decimal(form.cleaned_data["bcurr_credit"]) > Decimal("0.00"):
                        raise ValidationError(
                            "Bcurr debit and credit both cannot be greater than 0."
                        )

                    if form.cleaned_data["bcurr_debit"]:
                        total_bcurr_debit += form.cleaned_data["bcurr_debit"]
                    if form.cleaned_data["bcurr_credit"]:
                        total_bcurr_credit += form.cleaned_data["bcurr_credit"]

        # compare total debit = credit
        if total_bcurr_debit != total_bcurr_credit:
            raise ValidationError("Bcurr debit and credit are not equal.")
        if total_fcurr_debit != total_fcurr_credit:
            raise ValidationError("fcurr debit and credit are not equal.")


class T10Gld11Inline(admin.TabularInline):
    model = T10Gld11
    form = T10Gld11Form
    formset = T10Gld11InlineFormSet
    readonly_fields = (
        "foreign_curr",
        "curr_rate",
        "alloc_amt_tot",
        "alloc_date",
    )

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if request._obj_ is not None:
            if request._obj_.post_flag == True or request._obj_.delete_flag == True:
                fields.remove("vou_type_id")
        return fields

    def get_formset(self, request, obj=None, **kwargs):
        fs = super().get_formset(request, obj, **kwargs)

        # Remove the add, delete, change button in foriegn key
        coa_field = fs.form.base_fields["vou_coa"]
        coa_field.widget.can_add_related = False
        coa_field.widget.can_change_related = False
        coa_field.widget.can_delete_related = False

        subledger_field = fs.form.base_fields["vou_subledger"]
        subledger_field.widget.can_add_related = False
        subledger_field.widget.can_change_related = False
        subledger_field.widget.can_delete_related = False

        work_order_field = fs.form.base_fields["work_order"]
        work_order_field.widget.can_add_related = False
        work_order_field.widget.can_change_related = False
        work_order_field.widget.can_delete_related = False

        return fs


# Tax Booking Inline
class T10Gld12Inline(admin.TabularInline):
    model = T10Gld12
    fields = (
        "tax_code",
        "tax_booked_dt",
        "taxable_amount",
        "tax_amount",
        "adj_amount",
    )

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1


# Voucher type list
class GLVoucherTypeListFilter(admin.SimpleListFilter):
    title = _("Vou Type")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "vou_type"

    def lookups(self, request, model_admin):
        return (
            (obj.voucher_type, obj)
            for obj in T01Voc11.objects.filter(
                voucher_name__proxy_code="voc",
                voucher_name__prg_type=model_admin.vou_type,
            )
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(vou_type__voucher_type=self.value())


# Common admin class for GL, bank, cash voucher
class T10Gld10Admin(T01BaseAdmin):
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
    )
    list_display_links = (
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
    )
    fields = (
        "prg_type",
        (
            "division",
            "vou_type",
            "vou_date",
        ),
        ("subledger", "vou_hdr_ref", "vou_curr"),
        ("issued_to", "issued_ref", "vou_num"),
        "comment1",
        "comment2",
    )
    search_fields = (
        "vou_num",
        "vou_date",
        "vou_type__voucher_type",
        "comment1",
        "subledger__subledger_name",
        "issued_to",
        "vou_hdr_ref",
    )
    readonly_fields = ("vou_num",)
    actions = ["post_voucher", "unpost_voucher"]
    change_list_template = "ebos2210/admin/t10_jvm_ap_ar_change_list.html"

    def print_pdf(self, obj):
        return format_html(
            "<a class='button print-btn' onclick='print_voucher_js({})'>Print</a>",
            obj.id,
        )

    def get_list_filter(self, request):
        list_filter_fields = super(T01BaseAdmin, self).get_list_filter(request)
        return list_filter_fields + ['post_flag',]

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        form = super(T10Gld10Admin, self).get_form(request, obj, **kwargs)

        # Remove the add, delete, change button in foriegn key
        if subledger_field := form.base_fields.get("subledger"):
            subledger_field.widget.can_add_related = False
            subledger_field.widget.can_change_related = False
            subledger_field.widget.can_delete_related = False

        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            return readonly_fields + (
                "division",
                "vou_type",
                "vou_date",
                "amount",
            )
        return readonly_fields

    """Post VOucher custom action functionality"""

    @admin.action(description="Post Voucher")
    def post_voucher(self, request, queryset):
        posted = 0
        msg = "Voucher cannot be posted"
        total_balance_equal = True

        # While posting the voucher, check all selected vouchers total debit=total credit, if delete_flag=False, post_flag=False
        gld10_obj = queryset.filter(post_flag=False, delete_flag=False)
        total_balance = gld10_obj.aggregate(
            bcurr_debit_total=Sum("gld_header_set__bcurr_debit"), 
            bcurr_credit_total=Sum("gld_header_set__bcurr_credit"),
            fcurr_debit_total=Sum("gld_header_set__fcurr_debit"),
            fcurr_credit_total=Sum("gld_header_set__fcurr_credit"),
        )

        if total_balance:
            if total_balance["bcurr_debit_total"] != total_balance["bcurr_credit_total"] and total_balance["fcurr_debit_total"] != total_balance["fcurr_credit_total"]:
                # raise ValueError("Voucher cannot be posted. The vouchers debit credit are not equal.")
                msg = "Voucher cannot be posted. The vouchers debit credit are not equal."
                total_balance_equal = False

        if total_balance_equal:
            for q in queryset:
                if q.post_flag == False:
                    try:
                        T10Gld10.post_voucher(
                            voc_num=q.vou_num, voc_type=q.vou_type, vou_date=q.vou_date
                        )
                        posted += 1
                        msg = (
                            ngettext(
                                "%d voucher was successfully posted.",
                                "%d vouchers were successfully posted.",
                                posted,
                            )
                            % posted
                        )
                    except Exception as e:
                        msg = e
                else:
                    msg = "This voucher already posted"

        msg_code = messages.SUCCESS if posted > 0 else messages.ERROR
        self.message_user(request, msg, msg_code)

    """Unpost VOucher custom action functionality"""

    @admin.action(description="Unpost Voucher")
    def unpost_voucher(self, request, queryset):
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

    def delete_queryset(self, request, queryset):
        deleted_list = []
        not_deleted = []
        for obj in queryset:
            post_flag = obj.post_flag
            if post_flag == False:
                response = obj.delete()
                deleted_list.append(obj)
            else:
                not_deleted.append(obj)
        if not_deleted:
            messages.set_level(request, messages.WARNING)
            messages.warning(
                request,
                "Successfully deleted "
                + str(len(deleted_list))
                + " Records. In "
                + str(len(not_deleted))
                + " Records post flag is active.",
            )
        else:
            pass

        return True

    def has_change_permission(self, request, obj=None):
        try:
            if obj.vou_type.voucher_cat == str(2):
                return False
            if obj.post_flag == True:
                return False
            if obj.delete_flag == True:
                return False
        except:
            pass

        return True

    def has_delete_permission(self, request, obj=None):
        try:
            if obj.post_flag == True:
                return False
        except:
            pass

        return True

    # changeform fields
    def get_changeform_initial_data(self, request):
        return {
            "voc_status": "entered",
        }

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("add/get_t10cfg10/<int:division>/", self.get_division_data),
            path(
                "add/get_curr_rate/<int:foreign_curr>/<int:base_curr>/<str:vou_date>/",
                self.get_currency_rate,
            ),
            path(
                "<int:pk>/change/get_curr_rate/<int:foreign_curr>/",
                self.get_currency_rate,
            ),
            path("custom_print_button/<int:id>", self.custom_print),
            path("add/get_print_flag/<int:vou_type>", self.get_print_flag),
        ]
        return custom_urls + urls

    def get_lock_data_change(self, division):
        try:
            conf_obj_value = T10Cfg10.objects.get(division_id=division).lock_date_change
            conf_value = (
                {"lock_date_change": "true"}
                if conf_obj_value
                else {"lock_date_change": "false"}
            )
        except:
            conf_value = {"lock_date_change": "false"}

        return conf_value

    def get_division_data(self, request, division):
        div_curr = T01Div10.objects.get(id=division).currency
        result = {"division_curr": div_curr.id, "base_curr": div_curr.currency_name}
        result.update(**self.get_lock_data_change(division))
        return JsonResponse(result)

    def get_print_flag(self, request, vou_type):
        result = {"print_flag": T01Voc11.objects.get(id=vou_type).save_and_print}
        return JsonResponse(result)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["FILE_PATH"] = cache.get("file_path")
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id, form_url, extra_context=None):
        extra_context = extra_context or {}
        if vou_type := request.POST.get("vou_type"):
            extra_context["print_save_flag"] = T01Voc11.objects.get(
                id=vou_type
            ).save_and_print
        return super().changeform_view(request, object_id, form_url, extra_context)

    def check_save_and_print(self, request, instance):
        if instance.vou_type.save_and_print:
            file_path, new_tab = self.gl_voucher_print(instance)
            if not new_tab:
                return redirect(file_path)

            cache.add("file_path", file_path, timeout=30)
            msg = "Print output sent to new tab."
            self.message_user(request, msg, level=messages.INFO)

    def response_add(self, request, obj):
        if "_print_voucher" in request.POST:
            self.check_save_and_print(request, obj)

        return super().response_add(request, obj)

    def response_change(self, request, obj):
        if "_print_voucher" in request.POST:
            self.check_save_and_print(request, obj)

        return super().response_change(request, obj)

    def custom_print(self, request, id):
        file_path, new_tab = gl_voucher_print(T10Gld10.objects.get(id=id))
        return JsonResponse({"file_path": file_path})

    def get_currency_rate(
        self, request, foreign_curr, base_curr=None, vou_date=None, pk=None, module="gl"
    ):
        if pk:
            t10gld10_obj = T10Gld10.objects.get(id=pk)
            base_curr = t10gld10_obj.division.currency.id
            vou_date = t10gld10_obj.vou_date.strftime("%Y-%m-%d")
        else:
            if type(vou_date) == "str":
                vou_date = datetime.strptime(vou_date, "%Y-%m-%d")

        curr_rate = T01Cur11.get_curr_rate(
            conv_curr_from=foreign_curr,
            conv_curr_to=base_curr,
            rate_as_of=vou_date,
            module=module,
        )
        return JsonResponse({"curr_rate": curr_rate})

    def save_model(self, request, obj, form, change):
        if obj.pk is None:
            next_num, next_num_pfx_sfx = T01Voc12.next_number(
                obj.vou_type, obj.vou_date
            )
            obj.vou_num = next_num
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        total_bcurr_debit = Decimal(0.00)
        total_fcurr_debit = Decimal(0.00)

        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if formset.model == T10Gld11:
                obj = instance.vou_id
                vou_date = obj.vou_date
                instance.vou_period = vou_date.month
                instance.vou_year = vou_date.year
                instance.base_curr = obj.division.currency
                instance.bcurr_debit = instance.bcurr_debit or Decimal(0.00)
                instance.bcurr_credit = instance.bcurr_credit or Decimal(0.00)
                instance.fcurr_debit = instance.fcurr_debit or Decimal(0.00)
                instance.fcurr_credit = instance.fcurr_credit or Decimal(0.00)
                instance.foreign_curr = (
                    None if obj.vou_curr == instance.base_curr else obj.vou_curr
                )
                if (
                    instance.foreign_curr is None
                    or instance.foreign_curr == instance.base_curr
                ):
                    curr_rate = 0
                else:
                    if instance.pk:
                        t10gld10_obj = T10Gld10.objects.get(id=instance.pk)
                        base_curr = t10gld10_obj.division.currency.id
                        vou_date = t10gld10_obj.vou_date.strftime("%Y-%m-%d")
                    else:
                        if type(vou_date) == "str":
                            vou_date = datetime.strptime(vou_date, "%Y-%m-%d")
                        base_curr = instance.base_curr
                    curr_rate = T01Cur11.get_curr_rate(
                        conv_curr_from=instance.foreign_curr,
                        conv_curr_to=base_curr,
                        rate_as_of=vou_date,
                        module="gl",
                    )
                instance.curr_rate = curr_rate
                if instance.base_curr != obj.vou_curr:
                    instance.bcurr_debit = instance.fcurr_debit * instance.curr_rate
                    instance.bcurr_credit = instance.fcurr_credit * instance.curr_rate
            instance.save()

            try:
                if instance.bcurr_debit:
                    total_bcurr_debit += Decimal(instance.bcurr_debit)
                if instance.fcurr_debit:
                    total_fcurr_debit += Decimal(instance.fcurr_debit)
            except:
                pass

        formset.save_m2m()
        # save the total amount insert into T10Gld10
        if formset.model == T10Gld11:
            if total_fcurr_debit > 0.00:
                form.instance.total_amount = total_fcurr_debit
            elif total_bcurr_debit > 0.00:
                form.instance.total_amount = total_bcurr_debit
            form.instance.save()

        # Call the post_voucher(), if voucher_type.post_option is 'Auto post on save'
        if (
            form.instance.post_flag == False
            and form.instance.vou_type.post_option == "2"
        ):
            try:
                T10Gld10.post_voucher(
                    voc_num=form.instance.vou_num,
                    voc_type=form.instance.vou_type,
                    vou_date=form.instance.vou_date,
                )
            except Exception as e:
                raise ValueError(e)


# Coa filter: Showing Coa only for requested user
class CoaListFilter(admin.SimpleListFilter):
    title = _("Account Name")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "coa"

    def lookups(self, request, model_admin):
        return (
            (obj.account_name, obj)
            for obj in T01Coa10.objects.filter(division__user=request.user)
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(coa_id__account_name=self.value())


class BaseBalanceAdmin(T01BaseAdmin):
    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


# Account balance summery
class T10Abs10Admin(BaseBalanceAdmin):
    list_display = (
        "coa_id",
        "fin_year",
        "coa_opbal",
        "coa_audit_adj",
        "coa_clbal",
        "get_division",
    )
    search_fields = ("coa_id__account_name", "fin_year")
    dependent_key = "coa_id"

    def get_division(self, obj):
        return obj.coa_id.division

    get_division.short_description = "Division"

    def get_list_filter(self, request):
        list_filter_fields = super().get_list_filter(request)
        return list_filter_fields + [CoaListFilter, "fin_year"]


admin.site.register(T10Abs10, T10Abs10Admin)

# Subledger filter: Showing Subledger only for requested user
class SubledgerListFilter(admin.SimpleListFilter):
    title = _("Subledger Name")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "subledger_name"

    def lookups(self, request, model_admin):
        return (
            (obj.subledger_name, obj)
            for obj in T01Sld10.objects.filter(division__user=request.user)
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            return queryset.filter(subledger_id__subledger_name=self.value())


# Subledger balance summery
class T10Sbs10Admin(BaseBalanceAdmin):
    list_display = (
        "subledger_id",
        "fin_year",
        "sl_opbal",
        "sl_audit_adj",
        "sl_clbal",
        "get_division",
    )
    search_fields = ("subledger_id__subledger_name", "fin_year")
    dependent_key = "subledger_id"

    def get_division(self, obj):
        return obj.subledger_id.division

    get_division.short_description = "Division"

    def get_list_filter(self, request):
        list_filter_fields = super().get_list_filter(request)
        return list_filter_fields + [SubledgerListFilter, "fin_year"]


admin.site.register(T10Sbs10, T10Sbs10Admin)

# Tax module
class T10Tax10Admin(admin.ModelAdmin):
    fields = (
        "tax_code",
        "line_group",
        "line_description",
        "inv_region",
        "inv_country",
    )
    exclude = ("tax_filling_country",)
    list_display = (
        "tax_filling_country",
        "tax_code",
        "line_group",
        "inv_region",
        "inv_country",
    )
    search_fields = (
        "tax_filling_country",
        "tax_code",
        "line_group",
        "inv_region",
        "inv_country",
    )

    class Media:
        css = {
            "all": ("css/admin.css",),
        }


class T10SalesTaxInline(admin.TabularInline):
    model = T10SalesTax
    fields = (
        "tax_code",
        "line_description",
        "taxable_amount",
        "vat_amount",
        "adj_amount",
        "inv_region",
        "inv_country",
    )
    readonly_fields = (
        "tax_code",
        "line_description",
        "taxable_amount",
        "vat_amount",
        "adj_amount",
        "inv_region",
        "inv_country",
    )
    extra = 0
    max_num = 0

    def has_delete_permission(self, request, obj=None):
        return False


class T10PurchaseTaxInline(admin.TabularInline):
    model = T10PurchaseTax
    fields = (
        "tax_code",
        "line_description",
        "taxable_amount",
        "vat_amount",
        "adj_amount",
        "inv_region",
        "inv_country",
    )
    readonly_fields = (
        "tax_code",
        "line_description",
        "taxable_amount",
        "vat_amount",
        "adj_amount",
        "inv_region",
        "inv_country",
    )
    extra = 0
    max_num = 0

    def has_delete_permission(self, request, obj=None):
        return False


class T10Tax11Admin(admin.ModelAdmin):
    fields = (
        "company",
        "tax_reg_num",
        "tax_period_from",
        "tax_period_to",
        "tax_return_ref",
    )
    exclude = ("tax_filling_country",)
    list_display = (
        "tax_filling_country",
        "company",
        "tax_reg_num",
        "tax_period_from",
        "tax_period_to",
    )
    search_fields = (
        "tax_filling_country",
        "company",
        "tax_reg_num",
        "tax_period_from",
        "tax_period_to",
    )
    actions = ["import_tax_data", "print_tax_return"]

    def get_inlines(self, request, obj=None):
        if obj and obj.tax_return_set.exists():
            return [
                T10SalesTaxInline,
                T10PurchaseTaxInline,
            ]
        else:
            return []

    class Media:
        css = {
            "all": ("css/admin.css",),
        }

    """Tax Return data custom action functionality"""

    @admin.action(description="Tax return data")
    def import_tax_data(self, request, queryset):
        returned = 0
        for q in queryset:
            try:
                T10Tax11.import_tax_booked(q)
                returned += 1
            except Exception as e:
                raise ValueError(e)

        mess = messages.SUCCESS if returned > 0 else messages.ERROR
        self.message_user(
            request,
            ngettext(
                "%d tax was successfully returned.",
                "%d taxs were successfully returned.",
                returned,
            )
            % returned,
            mess,
        )

    # Print Tax Return custom action functionality
    def print_tax_return(self, request, queryset):
        for obj in queryset:
            pdf_report = TaxReturnRpt.initPDF(
                obj.company, obj.tax_return_ref, obj.tax_period_from
            )
            return pdf_report

    print_tax_return.short_description = "Print Tax Return"


class T10Tax12Admin(admin.ModelAdmin):
    fields = (
        "tax_code",
        "line_group",
        "line_description",
        "inv_region",
        "inv_country",
        "tax_return_ref",
        "taxable_amount",
        "vat_amount",
        "adj_amount",
    )
    exclude = ("tax_filling_country",)
    list_display = (
        "tax_filling_country",
        "tax_code",
        "line_group",
        "inv_region",
        "inv_country",
    )
    search_fields = (
        "tax_filling_country",
        "tax_code",
        "line_group",
        "inv_region",
        "inv_country",
    )

    class Media:
        css = {
            "all": ("css/admin.css",),
        }


admin.site.register(T10Tax10, T10Tax10Admin)
admin.site.register(T10Tax11, T10Tax11Admin)

# Tax invoice AP
class T10Tib11Inline(admin.TabularInline):
    model = T10Tib11
    fields = ("tax_code", "line_desc", "line_uom", "line_qty", "line_unit_rate")


class T10Tib10Admin(T01BaseAdmin):
    list_display = [
        "inv_type",
        "inv_date",
        "due_date",
        "inv_num",
        "subledger",
        "gl_code",
        "inv_curr",
        "division",
    ]
    readonly_fields = ["inv_num"]
    inlines = [T10Tib11Inline]
    actions = ["post_tax_invoice", "unpost_tax_invoice"]

    fields = (
        ("division", "inv_curr", "inv_type"),
        ("subledger", "gl_code", "recurring_status"),
        ("inv_date", "due_date", "inv_num"),
        "hdr_ref",
        "hdr_comment",
        "pmt_term",
        "prg_type",
    )

    """Post tax invoice custom action functionality"""

    @admin.action(description="Post tax invoice")
    def post_tax_invoice(self, request, queryset):
        posted = 0
        for q in queryset:
            if q.post_flag:
                self.message_user(request, "Already posted", messages.ERROR)
            else:
                try:
                    tax_code_group = (
                        T10Tib11.objects.values("tax_code")
                        .filter(line_id=q.id)
                        .annotate(tax_booked_dt=F("line_id__inv_date"))
                        .annotate(
                            taxable_amount=Sum(F("line_qty") * F("line_unit_rate"))
                        )
                        .annotate(
                            tax_amount=Sum(
                                (F("line_qty") * F("line_unit_rate"))
                                * (F("tax_code__tax_percent"))
                            )
                        )
                    )

                    mapping_dict = q.__dict__
                    line_obj_dict = {"vou_date": q.inv_date, **mapping_dict}

                    line_obj_dict.update(
                        tax_code_group.aggregate(total_invo_amt=Sum("taxable_amount"))
                    )
                    line_obj_dict.update(
                        tax_code_group.aggregate(total_tax_amt=Sum("tax_amount"))
                    )
                    line_obj_dict.update(
                        tax_code_group.aggregate(
                            total_net_amt=Sum("taxable_amount") + Sum("tax_amount")
                        )
                    )

                    gl_ids = T10Gld10.auto_gl_post(
                        gl_code=q.gl_code.id,
                        vou_curr=q.division.currency,
                        line_obj_dict=line_obj_dict,
                        gld12_obj_list=list(tax_code_group),
                    )
                    posted += 1
                    q.post_flag = True
                    q.gl_ref = gl_ids[0]
                    q.save()
                except Exception as e:
                    # raise e
                    self.message_user(request, e, messages.ERROR)

        mess = messages.SUCCESS if posted > 0 else messages.ERROR
        self.message_user(
            request,
            ngettext(
                "%d tax invoice was successfully posted.",
                "%d tax invoices were successfully posted.",
                posted,
            )
            % posted,
            mess,
        )

    """Unpost tax invoice custom action functionality"""

    @admin.action(description="Unpost tax invoice")
    def unpost_tax_invoice(self, request, queryset):
        unposted = 0
        for q in queryset:
            if q.post_flag is False:
                self.message_user(request, "Already unposted", messages.ERROR)
            else:
                try:
                    T10Gld10.auto_gl_unpost(T10Gld10.objects.get(id=q.gl_ref))
                    unposted += 1
                    q.post_flag = False
                    q.gl_ref = 0
                    q.save()
                except Exception as e:
                    # raise e
                    self.message_user(request, e, messages.ERROR)

        mess = messages.SUCCESS if unposted > 0 else messages.ERROR
        self.message_user(
            request,
            ngettext(
                "%d tax invoice was successfully unposted.",
                "%d tax invoices were successfully unposted.",
                unposted,
            )
            % unposted,
            mess,
        )
