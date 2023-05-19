from rest_framework import serializers

from ebos2206.models.m06_prl_trn import (
    T06Prl10,
    T06Prl11,
    T06Prl12,
    T06Prl13,
    T06Prl14,
    T06Prl15,
    T06Prl16,
)

from .s06_att_trn import AttendanceGenericSerializer


class T06Prl10Serializer(AttendanceGenericSerializer):
    class Meta:
        model = T06Prl10
        fields = "__all__"


class PayrollGenericSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "payroll_id_pk": "payroll_id__pk",
        "payroll_period_pk": "payroll_id__payroll_period__pk",
    }
    payroll_id = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, attrs):
        attrs.update({"payroll_id_id": self.context["view"].kwargs["payroll_id_pk"]})
        return super().validate(attrs)


class T06Prl11Serializer(PayrollGenericSerializer):
    class Meta:
        model = T06Prl11
        fields = "__all__"


class T06Prl12Serializer(PayrollGenericSerializer):
    class Meta:
        model = T06Prl12
        fields = "__all__"


class T06Prl13Serializer(PayrollGenericSerializer):
    class Meta:
        model = T06Prl13
        fields = "__all__"


class T06Prl14Serializer(PayrollGenericSerializer):
    class Meta:
        model = T06Prl14
        fields = "__all__"


class T06Prl15Serializer(PayrollGenericSerializer):
    class Meta:
        model = T06Prl15
        fields = "__all__"


class T06Prl16Serializer(PayrollGenericSerializer):
    class Meta:
        model = T06Prl16
        fields = "__all__"
