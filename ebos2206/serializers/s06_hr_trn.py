from datetime import date

from rest_framework import serializers

from ebos2206.models.m06_emp_mas import T06Emp10
from ebos2206.models.m06_hr_trn import (
    T06Eos10,
    T06Exc10,
    T06Hdt10,
    T06Mem10,
    T06Wps10,
    T06Wps11,
)


class T06Wps11Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Wps11
        fields = (
            "id",
            "wps_header",
            "emp_record_type",
            "emp_prl_id",
            "emp_UID",
            "emp_name",
            "emp_bnk_id",
            "emp_Bnk_acct",
            "sal_fixed_amt",
            "sal_Variable_amt",
            "emp_lve_days",
            "emp_housing_alw",
            "emp_transport_alw",
            "emp_tkt_amt",
            "emp_ot_amt",
            "emp_other_alw",
            "emp_lve_encashment",
        )


class T06Wps10Serializer(serializers.ModelSerializer):
    wps_header_set = T06Wps11Serializer(many=True, read_only=True)

    class Meta:
        model = T06Wps10
        fields = (
            "id",
            "wps_year",
            "wps_month",
            "division",
            "com_record_type",
            "com_UID",
            "com_bnk_name",
            "com_bnk_routing_code",
            "file_creation_dt",
            "sal_record_count",
            "tot_sal_amount",
            "pay_curr",
            "com_ref_note",
            "sif_file_name",
            "wps_header_set",
        )
        read_only_fields = (
            "file_creation_dt",
            "sif_file_name",
            "pay_curr",
            "com_bnk_name",
            "com_bnk_routing_code",
            "com_record_type",
            "com_UID",
            "sal_record_count",
            "tot_sal_amount",
        )


class T06Eos10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Eos10
        fields = "__all__"


class T06Exc10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Exc10
        fields = "__all__"

    def update(self, instance, validated_data):
        if instance.claim_status in ["3", "4"]:
            if instance.claim_status == "3":
                status_txt = "paid"
            else:
                status_txt = "rejected"
            raise serializers.ValidationError(
                {"detail": f"This claim has already been {status_txt}."}
            )

        return super().update(instance, validated_data)


class T06Hdt10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Hdt10
        fields = "__all__"

    def update(self, instance, validated_data):
        if instance.service_status == "3":
            status_txt = "closed"
            raise serializers.ValidationError(
                {"detail": f"This ticket has already been {status_txt}."}
            )

        return super().update(instance, validated_data)


class T06Ess02Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Exc10
        fields = "__all__"
        read_only_fields = (
            "employee_code",
            "gl_code",
            "claim_status",
            "claim_approver",
            "approver_note",
            "date_approved",
        )

    def validate(self, attrs):
        attrs.update(
            {
                "employee_code": T06Emp10.objects.get(
                    employee_code=self.context["request"].user.username
                )
            }
        )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if instance.claim_status in ["2", "3", "4"]:
            if instance.claim_status == "2":
                status_txt = "processing"
            elif instance.claim_status == "3":
                status_txt = "paid"
            else:
                status_txt = "rejected"
            raise serializers.ValidationError(
                {"detail": f"This claim has already been {status_txt}."}
            )

        return super().update(instance, validated_data)


class T06Ess03Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Hdt10
        fields = "__all__"
        read_only_fields = (
            "employee_code",
            "dt_of_request",
            "service_status",
            "service_due_date",
            "service_note",
            "serviced_by",
        )

    def validate(self, attrs):
        attrs.update(
            {
                "employee_code": T06Emp10.objects.get(
                    employee_code=self.context["request"].user.username
                ),
                "dt_of_request": date.today(),
            }
        )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if instance.service_status in ["2", "3"]:
            if instance.service_status == "2":
                status_txt = "processing"
            else:
                status_txt = "closed"
            raise serializers.ValidationError(
                {"detail": f"This ticket has already been {status_txt}."}
            )

        return super().update(instance, validated_data)


class T06Mem10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Mem10
        fields = "__all__"
