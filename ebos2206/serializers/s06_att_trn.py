import csv
import io

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ebos2201.exceptions import LockFlagException
from ebos2201.models.m01_fin_mas import T01Prj10
from ebos2206.exceptions import (
    DataExistsException,
    DataNotLockedException,
    PrlExistsException,
    PrlNotLockedException,
    PrsNotExistsException,
)
from ebos2206.models.m06_att_trn import T06Prs10, T06Tam10, T06Tbd10, T06Tbm10
from ebos2206.models.m06_emp_mas import T06Emp10
from ebos2206.models.m06_prl_trn import *
from ebos2206.utils.u06_prl_trn import PrintPrlCk, PrintPSlip

PRG_CHOICES = (
    ("TAM", "Machine data"),
    ("TBD", "Daily data"),
    ("TBM", "Monthly data"),
    ("PRL", "Payroll processing"),
    ("PPRL", "Post payroll"),
    ("UPRL", "Unpost payroll"),
    ("PPMT", "Post payment"),
    ("UPMT", "Unpost payment"),
    ("PRLCk", "Payroll checklist"),
    ("PSlip", "Payslip"),
)


class T06Prs10Serializer(serializers.ModelSerializer):
    prg_type = serializers.ChoiceField(choices=PRG_CHOICES, write_only=True)

    class Meta:
        model = T06Prs10
        fields = "__all__"
        extra_kwargs = {
            "divsion": {"required": True},
            "pay_month": {"required": True},
            "pay_year": {"required": True},
        }
        read_only_fields = (
            "id",
            "att_lock_flag",
            "prl_lock_flag",
            "prl_run_flag",
            "prl_post_flag",
            "pmt_post_flag",
            "payroll_checklist",
            "payslip",
        )
    
    def to_representation(self, instance):
        ins = super().to_representation(instance)
        ins['division'] = {"id": instance.division.id, "name": instance.division.division_name}
        return ins

    def validate(self, attrs):

        check_objs = self.Meta.model.objects.filter(
            division=attrs["division"],
            payroll_group=attrs["payroll_group"],
            pay_year=attrs["pay_year"],
            pay_month=attrs["pay_month"],
        )

        if check_objs.exists():
            if attrs.get("attn_machine_file"):
                # Check T06TAM10 data
                if check_objs[0].machine_data.exists():
                    raise DataExistsException

            elif attrs.get("daily_attn_file"):
                # Check T06TBD10 data
                if check_objs[0].daily_data.exists():
                    raise DataExistsException
        else:
            if attrs.get("prg_type") in [
                "PRL",
                "PPRL",
                "UPRL",
                "PPMT",
                "UPMT",
                "PRLCk",
                "PSlip",
            ]:
                raise PrsNotExistsException

        # Check att_lock_flag=False, prl_post_flag=False for attendace related insert
        if (
            attrs.get("prg_type") in ["TAM", "TBD", "TBM"]
            and check_objs.filter(
                Q(att_lock_flag=True) | Q(prl_post_flag=True)
            ).exists()
        ):
            raise LockFlagException

        # Check prl_post_flag=False for payroll process related insert
        elif (
            attrs.get("prg_type") in ["PRL"]
            and check_objs.filter(prl_post_flag=True).exists()
        ):
            raise LockFlagException

        # Validation for input file
        if attrs.get("prg_type") == "TAM":
            if check_objs.exists() and check_objs[0].attn_machine_file in ['', None]:
                raise serializers.ValidationError(
                    {"attn_machine_file": "This field is required"}
                )
            elif not check_objs.exists() and not attrs.get("attn_machine_file"):
                raise serializers.ValidationError(
                    {"attn_machine_file": "This field is required"}
                )
        elif attrs.get("prg_type") == "TBD":
            if check_objs.exists() and check_objs[0].daily_attn_file in ['', None]:
                raise serializers.ValidationError(
                    {"daily_attn_file": "This field is required"}
                )
            elif not check_objs.exists() and not attrs.get("daily_attn_file"):
                raise serializers.ValidationError(
                    {"daily_attn_file": "This field is required"}
                )
        elif attrs.get("prg_type") == "PRL":

            if not check_objs[0].att_lock_flag:
                raise DataNotLockedException

            if check_objs[0].prl_run_flag:
                raise PrlExistsException

            # Change the `prl_run_flag`
            attrs.update({"prl_run_flag": True})

        elif attrs.get("prg_type") == "PPRL":

            if not check_objs[0].prl_lock_flag:
                raise PrlNotLockedException

            if check_objs[0].prl_post_flag:
                raise serializers.ValidationError(
                    {"detail": "This period has already posted."}
                )

        elif attrs.get("prg_type") == "UPRL":

            if not check_objs[0].prl_lock_flag:
                raise PrlNotLockedException

            if not check_objs[0].prl_post_flag:
                raise serializers.ValidationError(
                    {"detail": "This period has already unposted."}
                )

        return super().validate(attrs)
    
    def _csv_data(self, column):
        
        from datetime import datetime

        if column[4]:
            attendance_date = datetime.strptime(column[4], "%Y-%m-%d")
            year = attendance_date.year
            month = attendance_date.month
            attendance_day = attendance_date.weekday()
        else:
            attendance_date, year, month, attendance_day = None, None, None, None

        try:
            employee_code = T06Emp10.objects.get(employee_code=column[0])
        except ObjectDoesNotExist:
            employee_code = None

        if column[3]:
            try:
                project_id = T01Prj10.objects.get(id=column[3]).id
            except ObjectDoesNotExist:
                project_id = None
        else:
            project_id = None

        try:
            data = {
                "pay_year": year,
                "pay_month": month,
                "division": column[1],
            }

            if column[2]:
                data.update({"payroll_group": column[2]})

            payroll_period = T06Prs10.objects.get(**data)
        except ObjectDoesNotExist:
            raise ValidationError(
                {"detail": "The payroll period are not match with uploaded file."}
            )
        
        return employee_code, payroll_period, attendance_date, attendance_day, project_id

    def _attn_machine_data_upload(self, obj):
        machine_data_objs = []
        file = obj.attn_machine_file
        data_set = file.read().decode("UTF-8")
        io_string = io.StringIO(data_set)
        next(io_string)

        for column in csv.reader(io_string, delimiter=","):
            
            employee_code, payroll_period, attendance_date, attendance_day, project_id = self._csv_data(column)

            # Create Record in T06Tam10 from csv file
            machine_data_objs.append(
                T06Tam10(
                    employee_code=employee_code,
                    payroll_period=payroll_period,
                    attendance_date=attendance_date,
                    attendance_day=attendance_day,
                    project_id=project_id,
                    time_in=column[5] if column[5] else None,
                    entry_code=column[6] if column[6] else None,
                    time_out=column[7] if column[7] else None,
                    exit_code=column[8] if column[8] else None,
                    weekend_flag=column[9] if column[9] else None,
                    public_holiday_flag=column[10] if column[10] else None,
                    transaction_type=column[11] if column[11] else None,
                    attendance_note=column[12] if column[12] else None,
                )
            )
        try:
            T06Tam10.objects.bulk_create(machine_data_objs)
        except IntegrityError:
            raise ValidationError(
                {
                    "detail": "The fields employee_code, attendance_date must make a unique set."
                }
            )

        return True

    def _daily_attn_data_upload(self, obj):
        if not T06Tam10.objects.filter(payroll_period=obj.id).exists():
            daily_attr_data_objs = []
            file = obj.daily_attn_file
            data_set = file.read().decode("UTF-8")
            io_string = io.StringIO(data_set)
            next(io_string)

            for column in csv.reader(io_string, delimiter=","):
                employee_code, payroll_period, attendance_date, attendance_day, project_id = self._csv_data(column)

                # Create Records in T06Tbd10
                daily_attr_data_objs.append(
                    T06Tbd10(
                        employee_code=employee_code,
                        payroll_period=payroll_period,
                        att_date=attendance_date,
                        att_day=attendance_day,
                        project_id=project_id,
                        normal_work_hrs=column[5] if column[5] else None,
                        normal_OT_hrs=column[6] if column[6] else None,
                        weekend_OT_hrs=column[7] if column[7] else None,
                        holiday_OT_hrs=column[8] if column[8] else None,
                        weekend_flag=column[9] if column[9] else None,
                        public_holiday_flag=column[10] if column[10] else None,
                        paid_weekend=column[11] if column[11] else None,
                        paid_public_holiday=column[12] if column[12] else None,
                    )
                )

            try:
                T06Tbd10.objects.bulk_create(daily_attr_data_objs)
            except IntegrityError:
                raise ValidationError(
                    {
                        "detail": "The fields employee_code, attendance_date must make a unique set."
                    }
                )
        return True

    def post_insert(self, instance, validated_data):
        # Call this function after create and update

        # upload attendance data
        if validated_data.get("prg_type") == "TAM":
            self._attn_machine_data_upload(instance)
        elif validated_data.get("prg_type") == "TBD":
            self._daily_attn_data_upload(instance)
        elif validated_data.get("prg_type") == "TBM":
            T06Tbm10.auto_entry(instance)
        elif validated_data.get("prg_type") == "PRL":
            # if data exists in T06Tbm10
            # and T06PRS10.prl_post_flag = false THEN Execute Following functions in the same order
            T06Prl10.get_monthly_att(instance)
            # T06Prl10.update_t06emp10(instance)
            T06Prl12.insert_t06prl12(instance)
            T06Prl13.insert_t06prl13(instance)
            T06Prl14.insert_t06prl14(instance)
            T06Prl15.insert_t06prl15(instance)
            T06Prl16.insert_t06prl16(instance)
            T06Prl10.update_monthly_att(instance)
            T06Prl12.update_t06prl12(instance)
            T06Prl12.update_t06emp12(instance)
            T06Prl11.insert_t06prl11(instance)
        elif validated_data.get("prg_type") == "PRLCk":
            # Payroll checklist
            PrintPrlCk(instance)

        elif validated_data.get("prg_type") == "PSlip":
            # Payslip
            PrintPSlip(instance)
        elif validated_data.get("prg_type") == "PPRL":
            # post payroll
            instance.auto_gl_post()
        elif validated_data.get("prg_type") == "UPRL":
            # unpost payroll
            instance.auto_gl_unpost()

        return True

    def create(self, validated_data):
        # if same payroll_group, division, month, year exist
        # Update the input, otherwise insert new row
        check_objs = self.Meta.model.objects.filter(
            division=validated_data["division"],
            payroll_group=validated_data["payroll_group"],
            pay_year=validated_data["pay_year"],
            pay_month=validated_data["pay_month"],
        )

        if check_objs.exists():
            data = validated_data
            if validated_data.get("prg_type") == "TAM" and validated_data["attn_machine_file"]:
                data["attn_machine_file"] = validated_data["attn_machine_file"]
            elif validated_data.get("prg_type") == "TBD" and validated_data["daily_attn_file"]:
                data["daily_attn_file"] = validated_data["daily_attn_file"]
            prs_obj = super().update(check_objs[0], data)
        else:
            prs_obj = super().create(validated_data)

        self.post_insert(prs_obj, validated_data)

        if validated_data.get("prg_type") in ["PRLCk", "PSlip"]:
            prs_obj = self.Meta.model.objects.get(id=prs_obj.id)

        return prs_obj

    def update(self, instance, validated_data):
        if not validated_data["attn_machine_file"]:
            del validated_data["attn_machine_file"]

        if not validated_data["daily_attn_file"]:
            del validated_data["daily_attn_file"]

        prs_obj = super().update(instance, validated_data)
        self.post_insert(prs_obj, validated_data)

        if validated_data.get("prg_type") in ["PRLCk", "PSlip"]:
            prs_obj = self.Meta.model.objects.get(id=prs_obj.id)

        return prs_obj


class T06Prs10LockSerializer(serializers.Serializer):
    payroll_run_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=T06Prs10.objects.all(), required=True
    )
    prg_type = serializers.ChoiceField(choices=PRG_CHOICES)


class AttendanceGenericSerializer(serializers.ModelSerializer):
    parent_lookup_kwargs = {
        "payroll_period_pk": "payroll_period__pk",
    }
    payroll_period = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        ins = super().to_representation(instance)
        ins.update({      
            'employee_id': instance.employee_code.id,      
            'employee_code': instance.employee_code.employee_code,
            'employee_name': f"{instance.employee_code.first_name} {instance.employee_code.last_name}",
        })
        return ins

    def validate(self, attrs):
        attrs.update(
            {"payroll_period_id": self.context["view"].kwargs["payroll_period_pk"]}
        )
        if pay_period := attrs.get("payroll_period") and (
            pay_period.att_lock_flag or pay_period.prl_lock_flag
        ):
            raise LockFlagException
        return super().validate(attrs)


class T06Tam10Serializer(AttendanceGenericSerializer):
    class Meta:
        model = T06Tam10
        fields = "__all__"


class T06Tbd10Serializer(AttendanceGenericSerializer):
    class Meta:
        model = T06Tbd10
        fields = "__all__"


class T06Tbm10Serializer(AttendanceGenericSerializer):
    class Meta:
        model = T06Tbm10
        fields = "__all__"


class T06Lve10Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Lve10
        fields = "__all__"

    def validate(self, attrs):
        if (
            attrs.get("approved_to_date")
            and attrs.get("approved_from_date")
            and attrs.get("approved_to_date") < attrs.get("approved_from_date")
        ):
            raise serializers.ValidationError(
                {
                    "approved_date": "approved to date to must be greater than or equal to approved from date"
                }
            )

        if (
            attrs.get("actual_date_to")
            and attrs.get("actual_date_from")
            and attrs.get("actual_date_to") < attrs.get("actual_date_from")
        ):
            raise serializers.ValidationError(
                {
                    "actual_date_to": "actual date to must be greater than or equal to actual date from"
                }
            )

        if (
            attrs.get("approved_to_date")
            and attrs.get("actual_date_to")
            and attrs.get("approved_to_date") > attrs.get("actual_date_to")
        ):
            raise serializers.ValidationError(
                {
                    "approved_date": "approved to date to must be less than or equal to actual to date"
                }
            )

        if (
            attrs.get("approved_from_date")
            and attrs.get("actual_date_from")
            and attrs.get("approved_from_date") < attrs.get("actual_date_from")
        ):
            raise serializers.ValidationError(
                {
                    "approved_date": "approved from date to must be grater or equal to actual from date"
                }
            )

        if attrs.get("request_date_to") and attrs.get("request_date_from"):
            if attrs.get("request_date_to") < attrs.get("request_date_from"):
                raise serializers.ValidationError(
                    {
                        "request_date_to": "Request date to must be greater than or equal to request date from"
                    }
                )

            # if payroll run setup att_flag = True, no insert edit, delete for the month
            if (
                T06Prs10.objects.filter(
                    models.Q(
                        pay_year=attrs.get("request_date_from").year,
                        pay_month=attrs.get("request_date_from").month,
                    )
                    | models.Q(
                        pay_year=attrs.get("request_date_to").year,
                        pay_month=attrs.get("request_date_to").month,
                    )
                )
                .filter(att_lock_flag=True)
                .exists()
            ):

                raise serializers.ValidationError(
                    "The payroll setup has been locked for this month."
                )

        return super().validate(attrs)


class T06Ess01Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Lve10
        fields = "__all__"
        read_only_fields = (
            "leave_status",
            "employee_code",
            "user_approved",
            "dt_of_approval",
            "approver_note",
            "approved_from_date",
            "approved_to_date",
            "actual_date_from",
            "actual_date_to",
        )

    def validate(self, attrs):
        if attrs.get("request_date_to") and attrs.get("request_date_from"):
            if attrs.get("request_date_to") < attrs.get("request_date_from"):
                raise serializers.ValidationError(
                    {
                        "request_date_to": "Request date to must be greater than or equal to request date from"
                    }
                )

            # if payroll run setup att_flag = True, no insert edit, delete for the month
            if (
                T06Prs10.objects.filter(
                    models.Q(
                        pay_year=attrs.get("request_date_from").year,
                        pay_month=attrs.get("request_date_from").month,
                    )
                    | models.Q(
                        pay_year=attrs.get("request_date_to").year,
                        pay_month=attrs.get("request_date_to").month,
                    )
                )
                .filter(att_lock_flag=True)
                .exists()
            ):

                raise serializers.ValidationError(
                    "The payroll setup has been locked for this month."
                )

        attrs.update(
            {
                "employee_code": T06Emp10.objects.get(
                    employee_code=self.context["request"].user.username
                )
            }
        )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if instance.leave_status in ["2", "3"]:
            status_txt = "approved" if instance.leave_status == "2" else "rejected"
            raise serializers.ValidationError(
                {"detail": f"This leave application has already been {status_txt}."}
            )

        return super().update(instance, validated_data)


class T06Ess05Serializer(serializers.ModelSerializer):
    class Meta:
        model = T06Prs10
        fields = (
            "id",
            "division",
            "payroll_group",
            "pay_year",
            "pay_month",
        )
