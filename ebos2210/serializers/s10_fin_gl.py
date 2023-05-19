from django.utils.translation import gettext_lazy as _
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from ebos2201.models.m01_core_mas import T01Div10, T01Voc11
from ebos2201.models.m01_fin_mas import T01Coa10, T01Sld10
from ebos2201.serializers.s01_core_mas import T01Cur10Serializer, T01Voc11Serializer
from ebos2201.serializers.s01_fin_mas import (
    T01Coa10ReadSerializer,
    T01Sld10ReadSerializer,
    UserBasedDivision,
)
from ebos2210.models.m10_fin_gl import T10Alc10, T10Alc11, T10Alc12, T10Glr01, T10Glr02
from ebos2210.utils.u10_gl_bl import gl_balance
from ebos2210.utils.u10_glr_bl import glr_balance


class T10Glr01Serializer(serializers.ModelSerializer):
    RPT_CODE_CHOICES = (
        ("GLR", "GLR"),
        ("GLC", "GLC"),
        ("SAO", "SAO"),
        ("SAD", "SAD"),
        ("DBK", "DBK"),
        ("SLC", "SLC"),
        ("SLD", "SLD"),
        ("LEA", "LEA"),
        ("CRA", "CRA"),
        ("AGR", "AGR"),
    )
    rpt_code = serializers.ChoiceField(choices=RPT_CODE_CHOICES)

    class Meta:
        model = T10Glr01
        fields = (
            "id",
            "division",
            "rpt_code",
            "coa",
            "subledger",
            "vou_curr",
            "aging1",
            "aging2",
            "aging3",
            "dt_from",
            "dt_upto",
            "file_csv",
            "file_pdf",
        )
        read_only_fields = ("id", "file_csv", "file_pdf")

    def to_representation(self, instance):
        rep = super(T10Glr01Serializer, self).to_representation(instance)

        if division := instance.division:
            rep["division"] = division.division_name

        if coa := instance.coa:
            rep["coa"] = coa.account_name

        if subledger := instance.subledger:
            rep["subledger"] = subledger.subledger_name

        if vou_curr := instance.vou_curr:
            rep["vou_curr"] = vou_curr.currency_code

        return rep

    def create(self, validated_data):
        instance = super().create(validated_data)
        file_name_pdf, file_name_csv = gl_balance(instance)

        # Update File Fields
        instance.file_csv = file_name_csv
        instance.file_pdf = file_name_pdf
        instance.save()

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        file_name_pdf, file_name_csv = gl_balance(instance)

        # Update File Fields
        instance.file_csv = file_name_csv
        instance.file_pdf = file_name_pdf
        instance.save()

        return instance


class T10Glr02Serializer(serializers.ModelSerializer):
    RPT_CODE_CHOICES = (
        ("TB", "TB"),
        ("BS", "BS"),
        ("PL", "PL"),
        ("TBC", "TBC"),
        ("CTB", "CTB"),
        ("CSF", "CSF"),
        ("TBDT", "TBDT"),
        ("BSDT", "BSDT"),
        ("PLDT", "PLDT"),
    )
    rpt_code = serializers.ChoiceField(choices=RPT_CODE_CHOICES)

    class Meta:
        model = T10Glr02
        fields = (
            "id",
            "company",
            "division",
            "rpt_code",
            "type_of_rpt",
            "year",
            "month",
            "day",
            "as_of_date",
            "file_csv",
            "file_pdf",
        )
        read_only_fields = ("id", "file_csv", "file_pdf")

    def validate(self, attrs):
        if attrs.get("type_of_rpt") == "3" and not attrs.get("month"):
            raise serializers.ValidationError({"month": "Month is required."})

        if attrs.get("rpt_code") in ["TBDT", "BSDT", "PLDT"]:
            if not attrs.get("as_of_date"):
                raise serializers.ValidationError(
                    {"as_of_date": "As of date is required."}
                )
        else:
            if not attrs.get("year"):
                raise serializers.ValidationError({"year": "Year is required."})

        if attrs.get("rpt_code") in ["TBC", "CTB"] and not attrs.get("month"):
            raise serializers.ValidationError({"month": "Month is required."})

        if attrs.get("rpt_code") == "CSF" and not attrs.get("month") in range(1, 13):
            raise serializers.ValidationError({"month": "The month should be 1 to 12."})

        return super().validate(attrs)

    def to_representation(self, instance):
        rep = super(T10Glr02Serializer, self).to_representation(instance)

        if company := instance.company:
            rep["company"] = company.company_name

        if division := instance.division:
            rep["division"] = division.division_name

        if type_of_rpt := instance.type_of_rpt:
            rep["type_of_rpt"] = instance.get_type_of_rpt_display()

        if month := instance.month:
            rep["month"] = instance.get_month_display()

        return rep

    def create(self, validated_data):
        print("I AM CREATING REPORT")
        instance = super().create(validated_data)
        file_name_pdf, file_name_csv = glr_balance(instance)

        # Update File Fields
        instance.file_csv = file_name_csv
        instance.file_pdf = file_name_pdf
        instance.save()

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        file_name_pdf, file_name_csv = glr_balance(instance)

        # Update File Fields
        instance.file_csv = file_name_csv
        instance.file_pdf = file_name_pdf
        instance.save()

        return instance


class T10Alc11Serializer(serializers.ModelSerializer):
    class Meta:
        model = T10Alc11
        fields = "__all__"


class T10Alc12Serializer(serializers.ModelSerializer):
    class Meta:
        model = T10Alc12
        fields = "__all__"


class T10Alc10DebitSerializer(serializers.Serializer):
    division = serializers.PrimaryKeyRelatedField(queryset=T01Div10.objects.all())
    vou_type = serializers.PrimaryKeyRelatedField(
        queryset=T01Voc11.objects.filter(voucher_name__prg_type="GLA")
    )
    coa = serializers.PrimaryKeyRelatedField(
        queryset=T01Coa10.objects.all(), required=False
    )
    subledger = serializers.PrimaryKeyRelatedField(queryset=T01Sld10.objects.all())
    vou_date = serializers.DateField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()


class T10Alc10CreditSerializer(serializers.Serializer):
    division = serializers.PrimaryKeyRelatedField(queryset=T01Div10.objects.all())
    coa = serializers.PrimaryKeyRelatedField(
        queryset=T01Coa10.objects.all(), required=False
    )
    subledger = serializers.PrimaryKeyRelatedField(queryset=T01Sld10.objects.all())
    vou_date = serializers.DateField()
    cr_date_from = serializers.DateField()
    cr_date_upto = serializers.DateField()


class T10Alc10WriteSerializer(WritableNestedModelSerializer):
    allocation_db = T10Alc11Serializer(many=True, required=False)
    allocation_cr = T10Alc12Serializer(many=True, required=False)

    class Meta:
        model = T10Alc10
        fields = (
            "id",
            "division",
            "vou_type",
            "vou_date",
            "coa",
            "subledger",
            "date_choice",
            "date_from",
            "date_to",
            "cr_date_from",
            "cr_date_upto",
            "allocation_db",
            "allocation_cr",
        )

    def validate(self, attrs):
        # Check for debit = credit
        total_debit_alloc, total_credit_alloc = 0, 0

        if attrs.get("allocation_db"):
            for allc_db in attrs["allocation_db"]:
                total_debit_alloc += float(allc_db["debit_alloc"])

        if attrs.get("allocation_cr"):
            for allc_cr in attrs["allocation_cr"]:
                total_credit_alloc += float(allc_cr["credit_alloc"])

        if total_debit_alloc != total_credit_alloc:
            raise serializers.ValidationError(
                {"detail": _("Allocated debit and credit are not matching.")}
            )

        return attrs

    def create(self, validated_data):
        validated_data["alloc_lock_flag"] = False
        validated_data["vou_num"] = self.Meta.model.create_alloc_vou_num(
            validated_data["vou_type"], validated_data["vou_date"]
        )
        instance = super().create(validated_data)

        # Update T10Gld11
        instance.update_alloc_details()

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        # Update T10Gld11
        instance.update_alloc_details()

        return instance


class T10Alc10ReadSerializer(T10Alc10WriteSerializer):
    division = UserBasedDivision()
    vou_type = T01Voc11Serializer()
    currency = T01Cur10Serializer()
    subledger = T01Sld10ReadSerializer()
    coa = T01Coa10ReadSerializer()
    date_choice = serializers.CharField(source="get_date_choice_display")
    allocation_db = T10Alc11Serializer(many=True)
    allocation_cr = T10Alc12Serializer(many=True)

    class Meta(T10Alc10WriteSerializer.Meta):
        fields = T10Alc10WriteSerializer.Meta.fields + (
            "vou_num",
            "alloc_lock_flag",
            "currency",
            "hdr_comment",
            "issued_to",
            "tot_amount",
            "line_narration",
            "chq_num",
            "chq_date",
        )
