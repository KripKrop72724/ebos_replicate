from django.db import models

# Create your models here.


class T15rpa_policy_data(models.Model):

    policy_type = models.CharField(max_length=255)
    document_type = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=255)
    tcf_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    phone = models.IntegerField()
    inception_date = models.DateField()
    expiryDate = models.DateField()
    vehicle = models.CharField(max_length=255)
    chasis_number = models.CharField(max_length=255)
    engine_number = models.CharField(max_length=255)
    reg_Number = models.CharField(max_length=255)
    Purpose_of_use = models.CharField(max_length=100)
    body_type = models.CharField(max_length=255)
    manufacture_year = models.CharField(max_length=255)
    seating_capacity = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    cylinder = models.CharField(max_length=255)
    premium = models.CharField(max_length=100)
    sum_insured = models.CharField(max_length=100)

    class Meta:
        # managed = False
        db_table = "T15rpa_policy_data"
        verbose_name = "Extracted Policy Data"


#  The file upload should convert all company policy (position of field may vary but all fields will be there)


class T15rpa_eid_data(models.Model):
    # db_table = 'T15rpa_eid_data'
    # verbose_name = 'Extracted EID Data'
    id_num = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    sex = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    card_num = models.CharField(max_length=255, null=True)

    class Meta:
        # managed = False
        db_table = "T15rpa_eid_data"
        verbose_name = "Extracted EID Data"


class T15rpa_vehreg_data(models.Model):
    # db_table = 'T15rpa_vehreg_data'
    # verbose_name = 'Extracted Mulkiya Data'
    traffic_plate = models.CharField(max_length=255, null=True)
    place_of_issue = models.CharField(max_length=255, null=True)
    plate_cls = models.CharField(max_length=255, null=True)
    traffic_code = models.CharField(max_length=255, null=True)
    owner = models.CharField(max_length=255, null=True)
    ins_expiry = models.DateField(null=True)
    nationality = models.CharField(max_length=255, null=True)
    policy_no = models.CharField(max_length=255, null=True)
    reg_date = models.DateField(null=True)
    ins_type = models.CharField(max_length=255, null=True)
    expiry_date = models.DateField(null=True)
    passenger_no = models.CharField(max_length=255, null=True)
    year_model = models.CharField(max_length=255, null=True)
    origin = models.CharField(max_length=255, null=True)
    vehicle_clr = models.CharField(max_length=255, null=True)
    vehicle_clss = models.CharField(max_length=255, null=True)
    vehicle_type = models.CharField(max_length=255, null=True)
    empty_weight = models.CharField(max_length=255, null=True)
    gross_weight = models.CharField(max_length=255, null=True)
    engine_no = models.CharField(max_length=255, null=True)
    chasis_no = models.CharField(max_length=255, null=True)

    class Meta:
        # managed = False
        db_table = "T15rpa_vehreg_data"
        verbose_name = "Extracted RTA Vehicle Data"


class T15rpa_drvlic_data(models.Model):
    # db_table = 'T15rpa_drvlic_data'
    # verbose_name = 'Extracted DriverLicense Data'
    license = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    nationality = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    issue_date = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    place_of_issue = models.CharField(max_length=255, null=True)

    class Meta:
        # managed = False
        db_table = "T15rpa_drvlic_data"
        verbose_name = "Extracted Driving License Data"


class T15rpa_extract_data(models.Model):
    policy_id = models.ForeignKey(
        "T15Mop10",
        on_delete=models.SET_NULL,
        db_column="IdMotorPolicy",
        blank=True,
        null=True,
    )
    DOCTYPE_CHOICE = (
        ("E", "EID"),
        ("P", "Policy"),
        ("D", "Driver License"),
        ("R", "Registration Card"),
    )
    document_type = models.CharField(
        db_column="sDocType", max_length=1, choices=DOCTYPE_CHOICE, default="E"
    )
    attachment = models.FileField(
        upload_to="u15_motor_docs/", db_column="uMotorDocs", null=True
    )
    document_no = models.CharField(
        db_column="sDocNum", max_length=25, blank=True
    )  # extracted data
    dt_of_issue = models.DateTimeField(
        db_column="dtIssue", blank=True, null=True
    )  # extracted data
    dt_of_expiry = models.DateTimeField(
        db_column="dtExpiry", blank=True, null=True
    )  # extracted data
    remarkes = models.CharField(
        db_column="sRemarks", max_length=40, blank=True, null=True
    )

    class Meta:
        #    managed = False
        db_table = "T15rpa_extract_data"
        verbose_name = "Upload to extract data"
