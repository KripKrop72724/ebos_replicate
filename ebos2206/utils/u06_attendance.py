import csv
import os

from django.conf import settings
from django.core.files.storage import default_storage
from ebos2201.utils import get_path

from ebos2206.models.m06_att_trn import T06Tam10, T06Tbd10, T06Tbm10


class AttendanceCSV:
    def render(self, fields, objs, file_name):
        folder = get_path("attendnace")

        # checking if the directory attendance exist or not.
        if not os.path.isdir(f"{settings.MEDIA_ROOT}/{folder}"):
            # if the attendance directory is not present then create it.
            os.makedirs(f"{settings.MEDIA_ROOT}/{folder}")

        CSV_FILE_NAME = f"{folder}/{file_name}"
        file_path = os.path.join(str(settings.MEDIA_ROOT), CSV_FILE_NAME)

        # Existing file remove
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

        writer = csv.writer(open(file_path, "w"))
        writer.writerow(fields)

        for obj in objs:
            writer.writerow([getattr(obj, field) for field in fields])

        return CSV_FILE_NAME

    def export_machine_data(self, pk):
        model = T06Tam10
        field_names = [field.name for field in model._meta.fields]
        file_name = "machine_attendance.csv"
        objs = model.objects.filter(payroll_period_id=pk)

        return self.render(field_names, objs, file_name)

    def export_daily(self, pk):
        model = T06Tbd10
        field_names = [field.name for field in model._meta.fields]
        file_name = "daily_attendance.csv"
        objs = model.objects.filter(payroll_period_id=pk)

        return self.render(field_names, objs, file_name)

    def export_monthly(self, pk):
        model = T06Tbm10
        field_names = [field.name for field in model._meta.fields]
        file_name = "monthly_attendance.csv"
        objs = model.objects.filter(payroll_period_id=pk)

        return self.render(field_names, objs, file_name)
