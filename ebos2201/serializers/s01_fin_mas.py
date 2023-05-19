from django.http import QueryDict
from rest_framework import serializers

from ebos2201.models.m01_core_mas import T01Div10, User
from ebos2201.models.m01_fin_mas import (
    T01Act10,
    T01Cfl10,
    T01Coa10,
    T01Prj10,
    T01Sld10,
    T01Slt10,
)


def get_user_division(user: User) -> QueryDict:
    return T01Div10.objects.filter(user=user.id)


class UserBasedDivision(serializers.ModelSerializer):
    class Meta:
        model = T01Div10
        fields = ("id", "division_name")

    def get_queryset(self):
        user = self.context["request"].user
        return get_user_division(user)


class TreeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "parent", "level")


class T01Slt10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Slt10
        fields = ("id", "sl_type_desc", "sl_type_code")


class T01Act10Serializer(TreeBaseSerializer):
    division = UserBasedDivision()

    class Meta(TreeBaseSerializer.Meta):
        model = T01Act10
        fields = TreeBaseSerializer.Meta.fields + (
            "division",
            "activity_name",
            "activity_cat",
            "Act_control",
        )


class T01Cfl10Serializer(TreeBaseSerializer):
    division = UserBasedDivision()

    class Meta(TreeBaseSerializer.Meta):
        model = T01Cfl10
        fields = TreeBaseSerializer.Meta.fields + (
            "division",
            "cashflow_desc",
            "cashflow_cat",
            "Cfl_control",
        )


class T01Coa10WriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = T01Coa10
        fields = (
            "id",
            "division",
            "parent",
            "account_name",
            "account_type",
            "account_group",
            "coa_control",
            "account_num",
            "coa_sl_cat",
            "coa_sl_type",
            "activity_group",
            "cashflow_group",
        )

    def validate(self, validated_data):
        user = self.context["request"].user
        division = validated_data.get("division")

        if validated_data.get("division"):
            if not division.user.filter(id=user.id).exists():
                raise serializers.ValidationError(
                    {"division": "The division is not assigned to the request user."}
                )
            if account_num := validated_data.get("account_num"):
                coa_obj = T01Coa10.objects.filter(
                    division=division, account_num=account_num
                )
                if self.instance:
                    coa_obj = coa_obj.exclude(id=int(self.instance.id))
                if coa_obj.exists():
                    raise serializers.ValidationError(
                        f"This existing A/C number for the `{division}` is duplicate."
                    )

        if parent := validated_data.get("parent"):
            if parent.coa_control != str(1):
                raise serializers.ValidationError(
                    {"parent": "Only rollup account can be parent."}
                )
            elif division != parent.division:
                raise serializers.ValidationError(
                    {"parent": "Parent coa division not match with input division."}
                )

            if str(parent.account_group) != validated_data.get("account_group"):
                raise serializers.ValidationError(
                    {
                        "account_group": "Account group should be inherit from the parent account group."
                    }
                )

        if validated_data.get("coa_control") == str(1):
            if validated_data.get("coa_sl_cat"):
                raise serializers.ValidationError(
                    {
                        "coa_sl_cat": "Subledger category should be blank for rollup account."
                    }
                )
            if validated_data.get("coa_sl_type"):
                raise serializers.ValidationError(
                    {
                        "coa_sl_type": "Subledger type should be blank for rollup account."
                    }
                )

        if activity_group := validated_data.get("activity_group"):
            if division != activity_group.division:
                raise serializers.ValidationError(
                    {
                        "activity_group": "Activity group division not match with input division."
                    }
                )

        if cashflow_group := validated_data.get("cashflow_group"):
            if division != cashflow_group.division:
                raise serializers.ValidationError(
                    {
                        "cashflow_group": "Cashflow group division not match with input division."
                    }
                )

        return validated_data


class T01Coa10ReadSerializer(TreeBaseSerializer):
    division = UserBasedDivision()
    account_type = serializers.CharField(source="get_account_type_display")
    account_group = serializers.CharField(source="get_account_group_display")
    coa_control = serializers.CharField(source="get_coa_control_display")
    coa_sl_cat = serializers.CharField(source="get_coa_sl_cat_display")
    coa_sl_type = T01Slt10Serializer()
    activity_group = T01Act10Serializer()
    cashflow_group = T01Cfl10Serializer()

    class Meta(TreeBaseSerializer.Meta):
        model = T01Coa10
        fields = TreeBaseSerializer.Meta.fields + (
            "division",
            "account_name",
            "account_type",
            "account_group",
            "coa_control",
            "account_num",
            "coa_sl_cat",
            "coa_sl_type",
            "activity_group",
            "cashflow_group",
        )


class T01Sld10writeSerializer(serializers.ModelSerializer):
    class Meta:
        model = T01Sld10
        fields = (
            "id",
            "division",
            "proxy_code",
            "subledger_name",
            "subledger_no",
            "subledger_code",
            "subledger_type",
            "subledger_cat",
            "invoice_address1",
            "invoice_address2",
            "invoice_address3",
            "ship_to_address1",
            "ship_to_address2",
            "ship_to_address3",
            "telephone1",
            "telephone2",
            "fax",
            "primary_contact_name",
            "primary_email",
            "primary_mobile",
            "commission_percent",
            "credit_days",
            "credit_days_from",
            "mode_of_payment",
            "credit_limit",
            "credit_open",
            "due_amount",
            "as_of_date",
            "key_account_flag",
        )

    def validate(self, validated_data):
        user = self.context["request"].user
        division = validated_data.get("division")

        if validated_data.get("division"):
            if not division.user.filter(id=user.id).exists():
                raise serializers.ValidationError(
                    {"division": "The division is not assigned to the request user."}
                )
            if subledger_code := validated_data.get("subledger_code"):
                coa_obj = T01Sld10.objects.filter(
                    division=division, subledger_code=subledger_code
                )
                if self.instance:
                    coa_obj = coa_obj.exclude(id=int(self.instance.id))
                if coa_obj.exists():
                    raise serializers.ValidationError(
                        f"This existing SL code for the `{division}` is duplicate."
                    )

        return validated_data


class T01Sld10ReadSerializer(T01Sld10writeSerializer):
    division = UserBasedDivision()
    subledger_type = T01Slt10Serializer()
    subledger_cat = serializers.CharField(source="get_subledger_cat_display")


class T01Prj10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Prj10
        fields = "__all__"
