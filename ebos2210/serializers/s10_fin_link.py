from datetime import datetime
from decimal import Decimal

from rest_framework import serializers

from ebos2201.models.m01_core_mas import T01Cur11, T01Voc12
from ebos2201.serializers.s01_core_mas import T01Cur10Serializer, T01Voc11Serializer
from ebos2201.serializers.s01_fin_mas import (
    T01Coa10ReadSerializer,
    T01Sld10ReadSerializer,
    UserBasedDivision,
)
from ebos2210.models.m10_fin_link import (
    T10Gld10,
    T10Gld11,
    T10Gld12,
    T10Tax10,
    T10Wor10,
)


class T10Wor10WriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = T10Wor10
        fields = (
            "id",
            "division",
            "wo_code",
            "wo_name",
            "wo_num",
            "coa",
            "sub_ledger",
            "wo_address",
            "actual_value",
            "estimated_value",
            "wo_status",
            "warehouse",
        )


class T10Wor10ReadSerializer(T10Wor10WriteSerializer):
    division = UserBasedDivision()


class T10Tax10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T10Tax10
        fields = (
            "id",
            "tax_filling_country",
            "tax_code",
            "tax_name",
            "line_group",
            "line_description",
            "inv_region",
            "inv_country",
            "tax_percent",
        )


class T10Gld11Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = T10Gld11
        fields = (
            "id",
            "vou_id",
            "vou_period",
            "vou_year",
            "vou_coa",
            "vou_subledger",
            "base_curr",
            "bcurr_debit",
            "bcurr_credit",
            "foreign_curr",
            "fcurr_debit",
            "fcurr_credit",
            "curr_rate",
            "narration",
            "work_order",
            "cc_number",
            "cc_expiry_date",
            "cc_auth_code",
            "chq_num",
            "chq_date",
            "chq_status",
            "prepared_amt",
            "restatement_amt",
            "alloc_amt_tot",
            "alloc_date",
            "due_date",
            "bank_reco_id",
            "chq_pmt_id",
            "vou_line_ref",
        )
        read_only_fields = (
            "vou_id",
            "vou_period",
            "vou_year",
        )

    def validate(self, attrs):
        bcurr_debit_value = attrs.get("bcurr_debit", None)
        bcurr_credit_value = attrs.get("bcurr_credit", None)
        fcurr_debit_value = attrs.get("fcurr_debit", None)
        fcurr_credit_value = attrs.get("fcurr_credit", None)

        # Convert amount field none to 0.00
        if bcurr_debit_value is None:
            attrs["bcurr_debit"] = Decimal(0.00)
        if bcurr_credit_value is None:
            attrs["bcurr_credit"] = Decimal(0.00)

        if fcurr_debit_value is None:
            attrs["fcurr_debit"] = Decimal(0.00)
        if fcurr_credit_value is None:
            attrs["fcurr_credit"] = Decimal(0.00)

        # Negative value validation
        if (
            Decimal(attrs["bcurr_debit"]) < Decimal(0.00)
            or Decimal(attrs["bcurr_credit"]) < Decimal(0.00)
            or Decimal(attrs["fcurr_debit"]) < Decimal(0.00)
            or Decimal(attrs["fcurr_credit"]) < Decimal(0.00)
        ):
            raise serializers.ValidationError("Negative value is not allowed.")

        if attrs.get("foreign_curr", None):
            if Decimal(attrs["fcurr_debit"]) == Decimal("0.00") and Decimal(
                attrs["fcurr_credit"]
            ) == Decimal("0.00"):
                raise serializers.ValidationError("Debit and credit both cannot be 0.")
            if Decimal(attrs["fcurr_debit"]) > Decimal("0.00") and Decimal(
                attrs["fcurr_credit"]
            ) > Decimal("0.00"):
                raise serializers.ValidationError(
                    "Debit and credit both cannot be greater than 0."
                )
        else:
            # in one line, should have debit or credit not both (both cannot be 0, both cannot be > 0)
            if Decimal(attrs["bcurr_debit"]) == Decimal("0.00") and Decimal(
                attrs["bcurr_credit"]
            ) == Decimal("0.00"):
                raise serializers.ValidationError("Debit and credit both cannot be 0.")
            if Decimal(attrs["bcurr_debit"]) > Decimal("0.00") and Decimal(
                attrs["bcurr_credit"]
            ) > Decimal("0.00"):
                raise serializers.ValidationError(
                    "Debit and credit both cannot be greater than 0."
                )

        return attrs


class T10Gld11ReadSerializer(T10Gld11Serializer):
    vou_coa = T01Coa10ReadSerializer()
    base_curr = T01Cur10Serializer()
    foreign_curr = T01Cur10Serializer()
    vou_subledger = T01Sld10ReadSerializer()
    work_order = T10Wor10ReadSerializer()
    chq_status = serializers.CharField(source="get_chq_status_display")


class T10Gld12Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = T10Gld12
        fields = (
            "id",
            "vou_id",
            "tax_code",
            "tax_booked_dt",
            "taxable_amount",
            "tax_amount",
            "adj_amount",
        )
        read_only_fields = ("vou_id",)


class T10Gld12ReadSerializer(T10Gld12Serializer):
    tax_code = T10Tax10Serializer()


class T10Gld10Serializer(serializers.ModelSerializer):
    gld11_set = T10Gld11Serializer(many=True)
    gld12_set = T10Gld12Serializer(many=True)

    class Meta:
        model = T10Gld10
        fields = (
            "id",
            "division",
            "vou_num",
            "vou_type",
            "vou_date",
            "comment1",
            "comment2",
            "vou_curr",
            "subledger",
            "mode_of_pay",
            "issued_to",
            "issued_ref",
            "vou_hdr_ref",
            "voc_status",
            "auto_entry_flag",
            "delete_flag",
            "post_flag",
            "total_amount",
            "paid_flag",
            "email_sent_flag",
            "gld11_set",
            "gld12_set",
        )
        read_only_fields = (
            "vou_num",
            "voc_status",
            "auto_entry_flag",
            "delete_flag",
            "post_flag",
            "total_amount",
            "paid_flag",
            "email_sent_flag",
        )

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        # division, vou_type, vou_date can not edit in update page
        if self.instance:
            extra_kwargs.update(
                {
                    "division": {"read_only": True},
                    "vou_type": {"read_only": True},
                    "vou_date": {"read_only": True},
                }
            )
        return extra_kwargs

    def auto_post_voucher(self, validated_data):
        # Call the post_voucher(), if voucher_type.post_option is 'Auto post on save'
        if (
            validated_data.get("post_flag") == False
            and validated_data.get("vou_type").post_option == "2"
        ):
            try:
                T10Gld10.post_voucher(
                    voc_num=validated_data.get("voc_num"),
                    voc_type=validated_data.get("vou_type"),
                    vou_date=validated_data.get("vou_date"),
                )
            except Exception as e:
                raise ValueError(e)

        return 1

    def validate(self, validated_data):
        total_bcurr_debit = Decimal(0.00)
        total_bcurr_credit = Decimal(0.00)
        total_fcurr_debit = Decimal(0.00)
        total_fcurr_credit = Decimal(0.00)

        vou_curr = validated_data.get("vou_curr")
        vou_date = validated_data.get("vou_date")
        division = validated_data.get("division")
        vou_type = validated_data.get("vou_type")

        if self.instance and self.instance.pk:
            vou_date = self.instance.vou_date
            division = self.instance.division
            vou_type = self.instance.vou_type

        # T10Gld11 data
        gld11_set = validated_data.pop("gld11_set")

        for gld11 in gld11_set:
            b_curr = division.currency
            fr_curr = None if vou_curr == division.currency else vou_curr

            if fr_curr is None or fr_curr == b_curr:
                curr_rate = 0
            else:
                if self.instance and self.instance.pk:
                    # for update
                    t10gld10_obj = T10Gld10.objects.get(id=self.instance.pk)
                    base_curr = t10gld10_obj.division.currency.id
                    vou_date = t10gld10_obj.vou_date.strftime("%Y-%m-%d")
                else:
                    if type(vou_date) == "str":
                        vou_date = datetime.strptime(vou_date, "%Y-%m-%d")
                    base_curr = b_curr

                # get currancy rate
                try:
                    curr_rate = T01Cur11.get_curr_rate(
                        conv_curr_from=fr_curr,
                        conv_curr_to=base_curr,
                        rate_as_of=vou_date,
                        module="gl",
                    )
                except Exception as e:
                    raise serializers.ValidationError(e)

            if b_curr != vou_curr:
                gld11["bcurr_debit"] = gld11["fcurr_debit"] * curr_rate
                gld11["bcurr_credit"] = gld11["fcurr_credit"] * curr_rate

            gld11.update(
                {
                    "vou_period": vou_date.month,
                    "vou_year": vou_date.year,
                    "base_curr": b_curr,
                    "foreign_curr": fr_curr,
                    "curr_rate": curr_rate,
                }
            )

            total_bcurr_debit += Decimal(gld11.get("bcurr_debit") or 0.00)
            total_bcurr_credit += Decimal(gld11.get("bcurr_credit") or 0.00)
            total_fcurr_debit += Decimal(gld11.get("fcurr_debit") or 0.00)
            total_fcurr_credit += Decimal(gld11.get("fcurr_credit") or 0.00)

        # Compare total debit = credit
        if total_bcurr_debit != total_bcurr_credit:
            raise serializers.ValidationError("Debit and credit are not equal.")
        if total_fcurr_debit != total_fcurr_credit:
            raise serializers.ValidationError("Debit and credit are not equal.")

        validated_data["gld11_set"] = gld11_set

        # The total amount of T10Gld10
        if total_fcurr_debit > 0.00:
            validated_data["total_amount"] = total_fcurr_debit
        elif total_bcurr_debit > 0.00:
            validated_data["total_amount"] = total_bcurr_debit

        if self.instance and self.instance.id:
            validated_data["vou_num"] = self.instance.vou_num
        else:
            try:
                # Create next number
                next_num, next_num_pfx_sfx = T01Voc12.next_number(vou_type, vou_date)
                validated_data["vou_num"] = next_num
            except Exception as e:
                raise serializers.ValidationError(e)

        return validated_data

    def create(self, validated_data):
        gld11_set = validated_data.pop("gld11_set")
        gld12_set = validated_data.pop("gld12_set")
        gld10 = T10Gld10.objects.create(**validated_data)

        for gld11 in gld11_set:
            T10Gld11.objects.create(**gld11, vou_id=gld10)

        for gld12 in gld12_set:
            T10Gld12.objects.create(**gld12, vou_id=gld10)

        self.auto_post_voucher(validated_data)

        return gld10

    def update(self, instance, validated_data):
        if instance.post_flag:
            raise serializers.ValidationError("Posted voucher cannot edit.")

        gld11_set = validated_data.pop("gld11_set")
        gld12_set = validated_data.pop("gld12_set")

        super(self.__class__, self).update(instance, validated_data)

        # T10Gld11 data
        keep_gld11_childs = []
        for gld11 in gld11_set:
            if "id" in gld11.keys():
                gld11_obj = T10Gld11.objects.filter(id=gld11["id"])
                if gld11_obj.exists():
                    gld = gld11_obj.update(**gld11)
                    keep_gld11_childs.append(gld11["id"])
                else:
                    continue
            else:
                gld = T10Gld11.objects.create(**gld11, vou_id=instance)
                keep_gld11_childs.append(gld.id)

        for gld in instance.gld11_set:
            if gld.id not in keep_gld11_childs:
                gld.delete()

        # T10Gld12 data
        keep_gld12_childs = []
        for gld12 in gld12_set:
            if "id" in gld12.keys():
                gld12_obj = T10Gld12.objects.filter(id=gld12["id"])
                if gld12_obj.exists():
                    gld = gld12_obj.update(**gld12)
                    keep_gld12_childs.append(gld12["id"])
                else:
                    continue
            else:
                gld = T10Gld12.objects.create(**gld12, vou_id=instance)
                keep_gld12_childs.append(gld.id)

        for gld in instance.gld12_set:
            if gld.id not in keep_gld12_childs:
                gld.delete()

        self.auto_post_voucher(validated_data)
        return instance


class T10Gld10ReadSerializer(T10Gld10Serializer):
    division = UserBasedDivision()
    vou_type = T01Voc11Serializer()
    vou_curr = T01Cur10Serializer()
    subledger = T01Sld10ReadSerializer()
    mode_of_pay = serializers.CharField(source="get_mode_of_pay_display")
    voc_status = serializers.CharField(source="get_voc_status_display")
    gld11_set = T10Gld11ReadSerializer(many=True)
    gld12_set = T10Gld12ReadSerializer(many=True)


class T10Gld10IdsSerializer(serializers.Serializer):
    voucher_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T10Gld10.objects.all(), required=True
    )
