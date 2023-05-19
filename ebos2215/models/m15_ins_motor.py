from inspect import CO_ASYNC_GENERATOR

from django.db import models

from ebos2210.models.m10_fin_gl import T10Gld10, T10Pst10

# Create your models here.

# Menu :   Insurance Service  >>  Motor Insurance


class Certificate(models.Model):
    certificate_no = models.IntegerField()


class Broker(models.Model):
    pass


class Area(models.Model):
    pass


class Customer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class Endorsereason(models.Model):
    pass


class Insurancecompany(models.Model):
    name = models.CharField(max_length=200)


class Branch(models.Model):
    name = models.CharField(max_length=200)


class T15Mop10(models.Model):
    certificateid = models.ForeignKey(
        Certificate, models.DO_NOTHING, db_column="CertificateID"
    )
    customerid = models.ForeignKey(Customer, models.DO_NOTHING, db_column="CustomerID")
    policystatus = models.CharField(
        db_column="PolicyStatus", max_length=10, blank=True, null=True
    )
    policytypeid = models.IntegerField(db_column="PolicyTypeID")
    policynumber = models.CharField(
        db_column="PolicyNumber", max_length=25, blank=True, null=True
    )
    brokerid = models.ForeignKey(
        Broker, models.DO_NOTHING, db_column="BrokerID", blank=True, null=True
    )
    areaid = models.ForeignKey(
        Area, models.DO_NOTHING, db_column="AreaID", blank=True, null=True
    )
    salesmanid = models.IntegerField(db_column="SalesmanID", blank=True, null=True)
    areaexcess = models.DecimalField(
        db_column="AreaExcess", max_digits=19, decimal_places=4
    )
    dateissue = models.DateTimeField(db_column="DateIssue")
    datestart = models.DateTimeField(db_column="DateStart")
    dateend = models.DateTimeField(db_column="DateEnd")
    isagencyrepair = models.BooleanField(
        db_column="IsAgencyRepair", blank=True, null=True
    )
    isdriverinsured = models.BooleanField(db_column="IsDriverInsured")
    noofpassengers = models.IntegerField(db_column="NoOfPassengers")
    receiptnumber = models.BigIntegerField(
        db_column="ReceiptNumber", blank=True, null=True
    )
    year = models.CharField(db_column="Year", max_length=50, blank=True, null=True)
    totalfees = models.DecimalField(
        db_column="TotalFees", max_digits=19, decimal_places=4
    )
    cancelstatus = models.CharField(db_column="CancelStatus", max_length=20, null=True)
    canceldate = models.DateTimeField(db_column="CancelDate", blank=True, null=True)
    endorsereasonid = models.ForeignKey(
        Endorsereason,
        models.DO_NOTHING,
        db_column="EndorseReasonID",
        blank=True,
        null=True,
    )
    insurancecompanyid = models.ForeignKey(
        Insurancecompany, models.DO_NOTHING, db_column="InsuranceCompanyID"
    )
    branchid = models.ForeignKey(Branch, models.DO_NOTHING, db_column="BranchID")
    paymentmode = models.CharField(
        db_column="PaymentMode", max_length=10, blank=True, null=True
    )
    agentcommssion = models.DecimalField(
        db_column="AgentCommssion",
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )
    brokercommission = models.DecimalField(
        db_column="BrokerCommission",
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )
    noncommfees = models.DecimalField(
        db_column="NonCommFees", max_digits=19, decimal_places=4
    )
    vehiclevalue = models.DecimalField(
        db_column="VehicleValue", max_digits=19, decimal_places=4
    )
    grosspremium = models.DecimalField(
        db_column="GrossPremium", max_digits=18, decimal_places=0, blank=True, null=True
    )
    soldfor = models.DecimalField(db_column="SoldFor", max_digits=19, decimal_places=4)
    excess = models.DecimalField(db_column="Excess", max_digits=19, decimal_places=4)
    tfc = models.DecimalField(db_column="TFC", max_digits=19, decimal_places=4)
    net = models.DecimalField(
        db_column="NET", max_digits=18, decimal_places=0, blank=True, null=True
    )
    commission = models.DecimalField(
        db_column="Commission", max_digits=18, decimal_places=0, blank=True, null=True
    )
    smcommission = models.DecimalField(
        db_column="SMCommission", max_digits=10, decimal_places=4, blank=True, null=True
    )
    ejisfee = models.DecimalField(
        db_column="EJISFee", max_digits=10, decimal_places=4, blank=True, null=True
    )
    inscommissionfee = models.DecimalField(
        db_column="InsCommissionFee",
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )
    ccbankcharges = models.DecimalField(
        db_column="ccBankCharges",
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )
    cashreceivedamount = models.DecimalField(
        db_column="CashReceivedAmount",
        max_digits=19,
        decimal_places=4,
        blank=True,
        null=True,
    )
    ccreceivedamount = models.DecimalField(
        db_column="CCReceivedAmount",
        max_digits=19,
        decimal_places=4,
        blank=True,
        null=True,
    )
    chequereceivedamount = models.DecimalField(
        db_column="ChequeReceivedAmount",
        max_digits=19,
        decimal_places=4,
        blank=True,
        null=True,
    )
    creditreceivedamount = models.DecimalField(
        db_column="CreditReceivedAmount",
        max_digits=19,
        decimal_places=4,
        blank=True,
        null=True,
    )
    remarks = models.CharField(db_column="Remarks", max_length=400, null=True)
    dltremarks = models.CharField(db_column="DltRemarks", max_length=400, null=True)
    original_tfc = models.DecimalField(
        db_column="Original_TFC", max_digits=18, decimal_places=0, blank=True, null=True
    )
    original_soldfor = models.DecimalField(
        db_column="Original_SoldFor",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    newinvoiceamount = models.DecimalField(
        db_column="NewInvoiceAmount",
        max_digits=18,
        decimal_places=0,
        blank=True,
        null=True,
    )
    subledger = models.IntegerField(
        db_column="CreditAddressBookID", blank=True, null=True
    )
    voucherid = models.IntegerField(db_column="VoucherID", blank=True, null=True)
    isposted = models.BooleanField(
        db_column="IsPosted", default=False, blank=True, null=True
    )
    isdeleted = models.BooleanField(
        db_column="IsDeleted", default=False, blank=True, null=True
    )
    glcode = models.CharField(db_column="GLCode", max_length=20, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "T15Mop10"
        verbose_name = "Motor Policy"

    def motor_policy_post(self):
        # Post policy when IsDeleted = False,  isPosted = False
        try:
            vou_curr = T10Pst10.objects.get(gl_code_id=self.glcode).division.currency
            mapping_data = {
                field.name: self.__getattribute__(field.name)
                for field in self._meta.fields
            }

            T10Gld10.auto_gl_post(
                gl_code=self.glcode, vou_curr=vou_curr, line_obj_dict=mapping_data
            )

        except Exception as e:
            raise ValueError(e)
