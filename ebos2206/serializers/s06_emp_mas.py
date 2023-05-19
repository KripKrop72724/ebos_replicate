from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from ebos2206.models.m06_emp_mas import (
    T06Dex10,
    T06Emp10,
    T06Emp11,
    T06Emp12,
    T06Emp13,
    T06Emp14,
    T06Emp15,
    T06Emp16,
    T06Emp17,
    T06Emp18,
)


class T06Emp10Serializer(serializers.ModelSerializer):
    nationality = CountryField(required=False)

    class Meta:
        model = T06Emp10
        fields = "__all__"


class EmployeeGenericSerializer(serializers.ModelSerializer):

    parent_lookup_kwargs = {
        'employee_pk': 'employee_code__id',
    }
    employee_code = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, attrs):
        attrs.update(
            {"employee_code_id": self.context["view"].kwargs["employee_pk"]}
        )
        return super().validate(attrs)


class T06Emp11Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp11
        fields = '__all__'


# For mupltiple insertion
class T06Emp11CreateSerializer(serializers.ModelSerializer):
    bank_acct_set = T06Emp11Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp11.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "bank_acct_set",
            "delete_ids",
        )


class T06Emp12Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp12
        fields = '__all__'


# For mupltiple insertion
class T06Emp12CreateSerializer(serializers.ModelSerializer):
    emp_leave_set = T06Emp12Serializer(many=True)

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_leave_set",
        )


class T06Emp13Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp13
        fields = '__all__'


# For mupltiple insertion
class T06Emp13CreateSerializer(serializers.ModelSerializer):
    emp_allow_set = T06Emp13Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp13.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_allow_set",
            "delete_ids",
        )


class T06Emp14Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp14
        fields = '__all__'


# For mupltiple insertion
class T06Emp14CreateSerializer(serializers.ModelSerializer):
    emp_tic_set = T06Emp14Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp14.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_tic_set",
            "delete_ids",
        )


class T06Emp15Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp15
        fields = '__all__'


# For mupltiple insertion
class T06Emp15CreateSerializer(serializers.ModelSerializer):
    emp_loan_set = T06Emp15Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp15.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_loan_set",
            "delete_ids",
        )


class T06Emp16Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp16
        fields = '__all__'


# For mupltiple insertion
class T06Emp16CreateSerializer(serializers.ModelSerializer):
    emp_deduc_set = T06Emp16Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp16.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_deduc_set",
            "delete_ids",
        )


class T06Emp17Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp17
        fields = '__all__'


# For mupltiple insertion
class T06Emp17CreateSerializer(serializers.ModelSerializer):
    emp_ass_set = T06Emp17Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp17.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_ass_set",
            "delete_ids",
        )


class T06Emp18Serializer(EmployeeGenericSerializer):
    class Meta:
        model = T06Emp18
        fields = '__all__'


# For mupltiple insertion
class T06Emp18CreateSerializer(serializers.ModelSerializer):
    emp_doc_set = T06Emp18Serializer(many=True)
    delete_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Emp18.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = T06Emp10
        fields = (
            "id",
            "emp_doc_set",
            "delete_ids",
        )


class T06Dex10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Dex10
        fields = "__all__"
        read_only_fields = ("report_file",)
