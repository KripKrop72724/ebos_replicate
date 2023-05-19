import django.contrib.auth.password_validation as validators
from django.contrib.auth.models import Group, Permission
from django.core import exceptions
from django.utils.translation import gettext as _
from rest_framework import serializers

from ebos2201.exceptions import ExistEmailException, ExistUsernameException
from ebos2201.models.m01_core_mas import (
    T01Atm10,
    T01Cat10,
    T01Com10,
    T01Cur10,
    T01Cur11,
    T01Dep10,
    T01Div10,
    T01Dsg10,
    T01Voc11,
    User,
)
from ebos2201.models.m01_fin_mas import T01Bnk10
from ebos2201.serializers.s01_fin_mas import TreeBaseSerializer

def validate_password(user, password):
    errors = dict()
    try:
        # validate the password and catch the exception
        validators.validate_password(password=password, user=user)

    # the exception raised here is different than serializers.ValidationError
    except exceptions.ValidationError as e:
        errors["password"] = list(e.messages)

    if errors:
        raise serializers.ValidationError(errors)

    return password


class T01Atm10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Atm10
        fields = "__all__"


class T01Com10WriteSerializer(serializers.ModelSerializer):
    logo_file_link = serializers.ImageField(required=False)

    class Meta:
        model = T01Com10
        fields = (
            "parent",
            "finyear_begin",
            "company_name",
            "company_address",
            "company_location",
            "logo_file_link",
            "document_header",
            "document_footer",
            "cost_type_co",
            "cost_level_co",
            "active_status",
        )


class T01Com10ReadSerializer(TreeBaseSerializer):
    finyear_begin = serializers.CharField(source="get_finyear_begin_display")

    class Meta(TreeBaseSerializer.Meta):
        model = T01Com10
        fields = TreeBaseSerializer.Meta.fields + (
            "finyear_begin",
            "company_name",
            "company_address",
            "company_location",
            "logo_file_link",
            "document_header",
            "document_footer",
            "cost_type_co",
            "cost_level_co",
            "active_status",
        )


class T01Cur10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Cur10
        fields = ("id", "currency_name", "currency_code", "currency_symbol")


class T01Cur11Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Cur11
        fields = (
            "id",
            "convert_curr_from",
            "convert_curr_to",
            "buy_rate_ap",
            "sell_rate_ar",
            "std_rate_gl",
            "date_effective_from",
        )


class T01Bnk10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Bnk10
        fields = ("id", "division", "bank_name")


class PermissionSerializer(serializers.ModelSerializer):
    content_type = serializers.StringRelatedField(source="content_type.name")

    class Meta:
        model = Permission
        fields = ("id", "name", "codename", "content_type")


class PermissionCodeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['codename']

class SimplifiedGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionCodeNameSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def create(self, validated_data):
        permissions_data = validated_data.pop('permissions', [])
        group = Group.objects.create(**validated_data)
        for permission_data in permissions_data:
            permission = Permission.objects.get(codename=permission_data['codename'])
            group.permissions.add(permission)
        return group

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', [])
        instance.name = validated_data.get('name', instance.name)
        instance.permissions.clear()
        for permission_data in permissions_data:
            permission = Permission.objects.get(codename=permission_data['codename'])
            instance.permissions.add(permission)
        instance.save()
        return instance


class VoucherSerializer(serializers.Serializer):
    general_voucher = serializers.CharField()
    payment_voucher = serializers.CharField()
    receipt_voucher = serializers.CharField()
    debit_note = serializers.CharField()
    credit_note = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password_confirmation = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    divisions = serializers.PrimaryKeyRelatedField(
        source="users", many=True, queryset=T01Div10.objects.all()
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone_number",
            "password",
            "password_confirmation",
            "is_active",
            "is_staff",
            "divisions",
            "groups"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields.pop("password")
            self.fields.pop("password_confirmation")

    def _validate_email(self, email):
        # Unique validation
        user = User.objects.filter(email__iexact=email)

        if self.instance:
            user = user.exclude(id=self.instance.id)

        if user.exists():
            raise ExistEmailException()

        return email

    def _validate_username(self, username):
        # Unique validation
        user = User.objects.filter(username__iexact=username)

        if self.instance:
            user = user.exclude(id=self.instance.id)

        if user.exists():
            raise ExistUsernameException()

        return username

    def validate(self, validated_data):
        username = validated_data.get("username", None)
        email = validated_data.get("email", None)
        password = validated_data.get("password", None)
        password_confirmation = validated_data.get("password_confirmation", None)

        # validate email
        self._validate_email(email)

        # If username is blank, take the username from email
        if not username and email:
            username = email.split("@")[0]
            validated_data["username"] = username

        # validate username
        self._validate_username(username)

        if not self.instance:
            # validate password
            user = User(username=username, password=password)
            validate_password(user, password)

            if password != password_confirmation:
                raise serializers.ValidationError(
                    _(
                        "The Password and Password confirmation do not match. Please enter again."
                    )
                )

        return validated_data

    def create(self, validated_data):
        divisions = validated_data.pop("users", None)
        groups = validated_data.pop("groups", None)  # Get groups data
        validated_data.pop("password_confirmation", None)

        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        if divisions:
            for division in divisions:
                division.user.add(user)

        if groups:  # Assign groups to user if there are any
            for group in groups:
                user.groups.add(group)

        return user


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    password_confirmation = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, validated_data):
        new_password = validated_data.get("new_password", None)
        password_confirmation = validated_data.get("password_confirmation", None)

        # validate password
        user = User(username=self.instance.username, password=new_password)
        validate_password(user, new_password)

        if new_password != password_confirmation:
            raise serializers.ValidationError(
                _(
                    "The New Password and Password confirmation do not match. Please enter again."
                )
            )

        return validated_data


class DeleteIdsSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())


class T01Div10WriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = T01Div10
        fields = (
            "id",
            "company",
            "division_name",
            "division_addr",
            "division_location",
            "currency",
            "wps_mol_uid",
            "wps_bank_code",
            "cost_type_div",
            "cost_level_div",
            "checklist_popup",
            "convert_to_caps",
            "invoice_ref_flag",
            "sellprice_flag",
            "user",
            "permission_data",
        )


class T01Div10ReadSerializer(T01Div10WriteSerializer):
    def to_representation(self, instance):
        rep = super(T01Div10ReadSerializer, self).to_representation(instance)

        if company := instance.company:
            rep["company"] = {"id": company.id, "company_name": company.company_name}

        if currency := instance.currency:
            rep["currency"] = {
                "id": currency.id,
                "currency_code": currency.currency_code,
                "currency_name": currency.currency_name,
                "currency_symbol": currency.currency_symbol,
            }

        if wps_bank := instance.wps_bank_code:
            rep["wps_bank_code"] = {"id": wps_bank.id, "bank_name": wps_bank.bank_name}

        if users := instance.user:
            rep["user"] = [
                {"id": user.id, "username": user.username} for user in users.all()
            ]

        return rep


class UserReadSerializer(serializers.ModelSerializer):
    divisions = T01Div10ReadSerializer(source="users", many=True, read_only=True)
    groups = SimplifiedGroupSerializer(many=True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "phone_number",
            "is_active",
            "is_staff",
            "divisions",
            "groups"
        )


class T01Dep10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Dep10
        fields = "__all__"


class T01Dsg10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Dsg10
        fields = "__all__"


class T01Cat10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T01Cat10
        fields = ("id", "category_code", "category_name", "system_code", "program_code")


class T01Voc11Serializer(serializers.ModelSerializer):
    prg_type = serializers.CharField(source="voucher_name.prg_type")
    reset_type = serializers.CharField(source="get_reset_type_display")
    voucher_cat = serializers.CharField(source="get_voucher_cat_display")
    post_option = serializers.CharField(source="get_post_option_display")
    unpost_option = serializers.CharField(source="get_unpost_option_display")
    delete_option = serializers.CharField(source="get_delete_option_display")

    class Meta:
        model = T01Voc11
        fields = (
            "id",
            "voucher_name",
            "voucher_type",
            "prg_type",
            "reset_type",
            "voucher_cat",
            "post_option",
            "unpost_option",
            "delete_option",
            "print_header",
            "save_and_print",
        )

    def to_representation(self, instance):
        rep = super(T01Voc11Serializer, self).to_representation(instance)
        rep["voucher_name"] = instance.voucher_name.voucher_name

        return rep
