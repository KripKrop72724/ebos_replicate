# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

"""
class Accliabilitymst(models.Model):
    liabilityid = models.BigIntegerField(db_column='LiabilityId', primary_key=True)  # Field name made lowercase.
    insuranceid = models.IntegerField(db_column='InsuranceId')  # Field name made lowercase.
    comprehensiveengname = models.CharField(db_column='ComprehensiveEngname', max_length=100,  null=True)  # Field name made lowercase.
    comprehensivearabname = models.CharField(db_column='ComprehensiveArabName', max_length=100,  null=True)  # Field name made lowercase.
    thirdpartyengname = models.CharField(db_column='ThirdPartyEngname', max_length=100,  null=True)  # Field name made lowercase.
    thirdpartyarbname = models.CharField(db_column='ThirdPartyArbName', max_length=100,  null=True)  # Field name made lowercase.
    exportengname = models.CharField(db_column='ExportEngName', max_length=100,  null=True)  # Field name made lowercase.
    exportarbname = models.CharField(db_column='ExportArbName', max_length=100,  null=True)  # Field name made lowercase.
    enteredby = models.IntegerField(db_column='Enteredby', blank=True, null=True)  # Field name made lowercase.
    entereddate = models.DateTimeField(db_column='EnteredDate', blank=True, null=True)  # Field name made lowercase.
    updatedby = models.IntegerField(db_column='Updatedby', blank=True, null=True)  # Field name made lowercase.
    updateddate = models.DateTimeField(db_column='UpdatedDate', blank=True, null=True)  # Field name made lowercase.
    deletedby = models.IntegerField(db_column='Deletedby', blank=True, null=True)  # Field name made lowercase.
    deleteddate = models.DateTimeField(db_column='DeletedDate', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='isDeleted')  # Field name made lowercase.
    checkboxstatus = models.BooleanField(db_column='checkboxStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'AccLiabilitymst'


class Additionalcoverrate(models.Model):
    additionalcoverrateid = models.AutoField(db_column='AdditionalCoverRateID', primary_key=True)  # Field name made lowercase.
    insurancetypeid = models.IntegerField(db_column='InsuranceTypeID', blank=True, null=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID', blank=True, null=True)  # Field name made lowercase.
    covervalue = models.DecimalField(db_column='CoverValue', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    premium = models.DecimalField(db_column='Premium', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    brokercommission = models.DecimalField(db_column='BrokerCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    salesmancommission = models.DecimalField(db_column='SalesmanCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    thirdpartycommission = models.DecimalField(db_column='ThirdPartyCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    fees = models.DecimalField(db_column='Fees', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    months = models.IntegerField(db_column='Months', blank=True, null=True)  # Field name made lowercase.
    printformat = models.CharField(db_column='PrintFormat', max_length=50,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'AdditionalCoverRate'


class Additionalpolicy(models.Model):
    additionalpolicyid = models.AutoField(db_column='AdditionalPolicyID', primary_key=True)  # Field name made lowercase.
    policynumber = models.CharField(db_column='PolicyNumber', max_length=20,  null=True)  # Field name made lowercase.
    motorpolicyid = models.IntegerField(db_column='MotorPolicyID', blank=True, null=True)  # Field name made lowercase.
    premium = models.DecimalField(db_column='Premium', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    fees = models.DecimalField(db_column='Fees', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    coveragedesc = models.CharField(db_column='CoverageDesc', max_length=300,  null=True)  # Field name made lowercase.
    insuredvalue = models.DecimalField(db_column='InsuredValue', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    datecoveragefrom = models.DateTimeField(db_column='DateCoverageFrom', blank=True, null=True)  # Field name made lowercase.
    datecoverageto = models.DateTimeField(db_column='DateCoverageTo', blank=True, null=True)  # Field name made lowercase.
    insurancetype = models.CharField(db_column='InsuranceType', max_length=50,  null=True)  # Field name made lowercase.
    insurancecompany = models.CharField(db_column='InsuranceCompany', max_length=50,  null=True)  # Field name made lowercase.
    ispolicyprinted = models.BooleanField(db_column='IsPolicyPrinted', blank=True, null=True)  # Field name made lowercase.
    policyprinteduserid = models.IntegerField(db_column='PolicyPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    datedeleted = models.DateTimeField(db_column='DateDeleted', blank=True, null=True)  # Field name made lowercase.
    deleteduserid = models.IntegerField(db_column='DeletedUserID', blank=True, null=True)  # Field name made lowercase.
    ispostedtoaccounts = models.BooleanField(db_column='IsPostedToAccounts', blank=True, null=True)  # Field name made lowercase.
    datepostedtoaccounts = models.DateTimeField(db_column='DatePostedToAccounts', blank=True, null=True)  # Field name made lowercase.
    postedtoaccountuserid = models.IntegerField(db_column='PostedToAccountUserID', blank=True, null=True)  # Field name made lowercase.
    voucherid = models.IntegerField(db_column='VoucherID', blank=True, null=True)  # Field name made lowercase.
    glcode = models.IntegerField(db_column='GLCode', blank=True, null=True)  # Field name made lowercase.
    paymentmode = models.IntegerField(db_column='PaymentMode', blank=True, null=True)  # Field name made lowercase.
    commission = models.DecimalField(db_column='Commission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    isreceiptprinted = models.IntegerField(db_column='IsReceiptPrinted', blank=True, null=True)  # Field name made lowercase.
    policyprinteddate = models.DateTimeField(db_column='PolicyPrintedDate', blank=True, null=True)  # Field name made lowercase.
    receiptprinteddate = models.DateTimeField(db_column='ReceiptPrintedDate', blank=True, null=True)  # Field name made lowercase.
    branchid = models.IntegerField(db_column='BranchID', blank=True, null=True)  # Field name made lowercase.
    salesmenid = models.IntegerField(db_column='SalesmenID', blank=True, null=True)  # Field name made lowercase.
    cashreceivedamount = models.DecimalField(db_column='CashReceivedAmount', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    ccreceivedamount = models.DecimalField(db_column='CCReceivedAmount', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    chequereceivedamount = models.DecimalField(db_column='ChequeReceivedAmount', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    creditreceivedamount = models.DecimalField(db_column='CreditReceivedAmount', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    policytype = models.IntegerField(db_column='PolicyType', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=50,  null=True)  # Field name made lowercase.
    insurancecompanyid = models.ForeignKey('Insurancecompany', models.DO_NOTHING, db_column='InsuranceCompanyID', blank=True, null=True)  # Field name made lowercase.
    referencenumber = models.CharField(db_column='ReferenceNumber', max_length=100,  null=True)  # Field name made lowercase.
    insurednamee = models.TextField(db_column='InsuredNameE',  null=True)  # Field name made lowercase.
    insurednamea = models.TextField(db_column='InsuredNameA',  null=True)  # Field name made lowercase.
    addresss = models.TextField(db_column='Addresss',  null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='ContactPerson', max_length=100,  null=True)  # Field name made lowercase.
    telephonenumber = models.CharField(db_column='Telephonenumber', max_length=20,  null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50,  null=True)  # Field name made lowercase.
    mobilenumber = models.CharField(db_column='MobileNumber', max_length=20,  null=True)  # Field name made lowercase.
    suminsured = models.DecimalField(db_column='SumInsured', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    soldamount = models.DecimalField(db_column='SoldAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    grosspremium = models.DecimalField(db_column='GrossPremium', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    netpremium = models.DecimalField(db_column='NetPremium', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    nonmotorpolicyid = models.IntegerField(db_column='NonMotorPolicyID', blank=True, null=True)  # Field name made lowercase.
    salesmanid = models.IntegerField(db_column='SalesManID', blank=True, null=True)  # Field name made lowercase.
    eremarks = models.CharField(db_column='ERemarks', max_length=100,  null=True)  # Field name made lowercase.
    receiptno = models.CharField(db_column='ReceiptNo', max_length=100,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'AdditionalPolicy'


class Application(models.Model):
    applicationid = models.AutoField(db_column='ApplicationID', primary_key=True)  # Field name made lowercase.
    applicationname = models.CharField(db_column='ApplicationName', max_length=50,  null=True)  # Field name made lowercase.
    applicationconn = models.CharField(db_column='ApplicationConn', max_length=150,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Application'


class Area(models.Model):
    areaid = models.AutoField(db_column='AreaID', primary_key=True)  # Field name made lowercase.
    areanameeng = models.CharField(db_column='AreaNameEng', max_length=25, blank=True, null=True)  # Field name made lowercase.
    areanamearab = models.CharField(db_column='AreaNameArab', max_length=50,  null=True)  # Field name made lowercase.
    areaentereddate = models.DateTimeField(db_column='AreaEnteredDate')  # Field name made lowercase.
    areaenteredby = models.IntegerField(db_column='AreaEnteredBy', blank=True, null=True)  # Field name made lowercase.
    areavehicletype = models.CharField(db_column='AreaVehicleType', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Area'


class Bank(models.Model):
    bankid = models.AutoField(db_column='BankID', primary_key=True)  # Field name made lowercase.
    banknameeng = models.CharField(db_column='BankNameEng', max_length=50,  null=True)  # Field name made lowercase.
    banknamearab = models.CharField(db_column='BankNameArab', max_length=100,  null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=15,  null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address',  null=True)  # Field name made lowercase.
    enteredby = models.IntegerField(db_column='EnteredBy', blank=True, null=True)  # Field name made lowercase.
    entereddate = models.DateTimeField(db_column='EnteredDate', blank=True, null=True)  # Field name made lowercase.
    deletedby = models.IntegerField(db_column='DeletedBy', blank=True, null=True)  # Field name made lowercase.
    deletedate = models.DateTimeField(db_column='DeleteDate', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment',  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Bank'


class Bodytype(models.Model):
    bodytypeid = models.AutoField(db_column='BodyTypeID', primary_key=True)  # Field name made lowercase.
    bodytypenameeng = models.CharField(db_column='BodyTypeNameEng', max_length=30, blank=True, null=True)  # Field name made lowercase.
    bodytypenamearab = models.CharField(db_column='BodyTypeNameArab', max_length=50,  null=True)  # Field name made lowercase.
    driverrate = models.DecimalField(db_column='DriverRate', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    passengerrate = models.DecimalField(db_column='PassengerRate', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    bodytypeenteredby = models.IntegerField(db_column='BodyTypeEnteredBy', blank=True, null=True)  # Field name made lowercase.
    bodytypeentereddate = models.DateTimeField(db_column='BodyTypeEnteredDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'BodyType'


class Branch(models.Model):
    branchid = models.AutoField(db_column='BranchID', primary_key=True)  # Field name made lowercase.
    branchcode = models.CharField(db_column='BranchCode', max_length=10,  null=True)  # Field name made lowercase.
    branchnameeng = models.CharField(db_column='BranchNameEng', max_length=25, blank=True, null=True)  # Field name made lowercase.
    branchnamearab = models.CharField(db_column='BranchNameArab', max_length=50,  null=True)  # Field name made lowercase.
    branchphone = models.CharField(db_column='BranchPhone', max_length=15,  null=True)  # Field name made lowercase.
    pvcode = models.CharField(db_column='PVCode', max_length=50,  null=True)  # Field name made lowercase.
    branchabid = models.IntegerField(db_column='BranchABID', blank=True, null=True)  # Field name made lowercase.
    branchenteredby = models.IntegerField(db_column='BranchEnteredBy')  # Field name made lowercase.
    branchentereddate = models.DateTimeField(db_column='BranchEnteredDate')  # Field name made lowercase.
    branchaddressengline1 = models.CharField(db_column='BranchAddressEngLine1', max_length=30,  null=True)  # Field name made lowercase.
    branchaddressengline2 = models.CharField(db_column='BranchAddressEngLine2', max_length=30,  null=True)  # Field name made lowercase.
    branchaddressengline3 = models.CharField(db_column='BranchAddressEngLine3', max_length=30,  null=True)  # Field name made lowercase.
    branchaddressarabline1 = models.CharField(db_column='BranchAddressArabLine1', max_length=30,  null=True)  # Field name made lowercase.
    branchaddressarabline2 = models.CharField(db_column='BranchAddressArabLine2', max_length=30,  null=True)  # Field name made lowercase.
    branchaddressarabline3 = models.CharField(db_column='BranchAddressArabLine3', max_length=30,  null=True)  # Field name made lowercase.
    branchcommenteng = models.CharField(db_column='BranchCommentEng', max_length=200,  null=True)  # Field name made lowercase.
    branchcomentarab = models.CharField(db_column='BranchComentArab', max_length=200,  null=True)  # Field name made lowercase.
    brokercomment = models.CharField(db_column='BrokerComment', max_length=200,  null=True)  # Field name made lowercase.
    brokercommenta = models.CharField(db_column='BrokerCommentA', max_length=200,  null=True)  # Field name made lowercase.
    provider = models.CharField(db_column='Provider', max_length=50,  null=True)  # Field name made lowercase.
    bcidaddressbook = models.IntegerField(db_column='BcIdAddressBook', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Branch'


class Broker(models.Model):
    brokerid = models.AutoField(db_column='BrokerID', primary_key=True)  # Field name made lowercase.
    brokercode = models.CharField(db_column='BrokerCode', max_length=20,  null=True)  # Field name made lowercase.
    brokernameeng = models.CharField(db_column='BrokerNameEng', max_length=30, blank=True, null=True)  # Field name made lowercase.
    brokernamearab = models.CharField(db_column='BrokerNameArab', max_length=40,  null=True)  # Field name made lowercase.
    brokeraddressengline1 = models.CharField(db_column='BrokerAddressEngLine1', max_length=20,  null=True)  # Field name made lowercase.
    brokeraddressengline2 = models.CharField(db_column='BrokerAddressEngLine2', max_length=20,  null=True)  # Field name made lowercase.
    brokeraddressengline3 = models.CharField(db_column='BrokerAddressEngLine3', max_length=20,  null=True)  # Field name made lowercase.
    brokeraddressarabline1 = models.CharField(db_column='BrokerAddressArabLine1', max_length=20,  null=True)  # Field name made lowercase.
    brokeraddressarabline2 = models.CharField(db_column='BrokerAddressArabLine2', max_length=20,  null=True)  # Field name made lowercase.
    brokeraddressarabline3 = models.CharField(db_column='BrokerAddressArabLine3', max_length=20,  null=True)  # Field name made lowercase.
    brokerphone1 = models.CharField(db_column='BrokerPhone1', max_length=20,  null=True)  # Field name made lowercase.
    brokerphone2 = models.CharField(db_column='BrokerPhone2', max_length=20,  null=True)  # Field name made lowercase.
    brokeremailid = models.CharField(db_column='BrokerEmailID', max_length=30,  null=True)  # Field name made lowercase.
    brokerwebsite = models.CharField(db_column='BrokerWebSite', max_length=30,  null=True)  # Field name made lowercase.
    brokerenteredby = models.IntegerField(db_column='BrokerEnteredBy')  # Field name made lowercase.
    brokerentereddate = models.DateTimeField(db_column='BrokerEnteredDate')  # Field name made lowercase.
    brokercomment = models.CharField(db_column='BrokerComment', max_length=200,  null=True)  # Field name made lowercase.
    brokercommenta = models.CharField(db_column='BrokerCommentA', max_length=200,  null=True)  # Field name made lowercase.
    brsubledgerid = models.IntegerField(db_column='BrSubLedgerID', blank=True, null=True)  # Field name made lowercase.
    bridaddressbook = models.IntegerField(db_column='BrIdAddressBook', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Broker'


class Cancelrefund(models.Model):
    cancelrefundid = models.BigAutoField(db_column='CancelRefundID', primary_key=True)  # Field name made lowercase.
    motorpolicyid = models.ForeignKey('Motorpolicy', models.DO_NOTHING, db_column='MotorPolicyID')  # Field name made lowercase.
    cancelnumber = models.IntegerField(db_column='CancelNumber')  # Field name made lowercase.
    isnewpolicy = models.BooleanField(db_column='IsNewPolicy')  # Field name made lowercase.
    newpolicyid = models.IntegerField(db_column='NewPolicyID', blank=True, null=True)  # Field name made lowercase.
    chequesalutation = models.CharField(db_column='ChequeSalutation', max_length=10, blank=True, null=True)  # Field name made lowercase.
    chequename = models.CharField(db_column='ChequeName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    contactnumber = models.CharField(db_column='ContactNumber', max_length=10, blank=True, null=True)  # Field name made lowercase.
    salesbranchid = models.IntegerField(db_column='SalesBranchID')  # Field name made lowercase.
    salesuserid = models.IntegerField(db_column='SalesUserID')  # Field name made lowercase.
    salesdateentered = models.DateTimeField(db_column='SalesDateEntered')  # Field name made lowercase.
    canceleddate = models.DateTimeField(db_column='CanceledDate')  # Field name made lowercase.
    cancelremark = models.CharField(db_column='CancelRemark', max_length=255,  null=True)  # Field name made lowercase.
    isdebitnotecreated = models.BooleanField(db_column='IsDebitNoteCreated')  # Field name made lowercase.
    dnamount = models.DecimalField(db_column='DNAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    dnentereddatetime = models.DateTimeField(db_column='DNEnteredDateTime', blank=True, null=True)  # Field name made lowercase.
    dnentereduserid = models.IntegerField(db_column='DNEnteredUserID', blank=True, null=True)  # Field name made lowercase.
    ispaymentdone = models.BooleanField(db_column='IsPaymentDone', blank=True, null=True)  # Field name made lowercase.
    inscompanycnnumber = models.CharField(db_column='InsCompanyCNNumber', max_length=50,  null=True)  # Field name made lowercase.
    refundmode = models.BooleanField(db_column='RefundMode', blank=True, null=True)  # Field name made lowercase.
    refundamount = models.CharField(db_column='RefundAmount', max_length=8,  null=True)  # Field name made lowercase.
    refunddatetime = models.DateTimeField(db_column='RefundDateTime', blank=True, null=True)  # Field name made lowercase.
    refundmodebankdetails = models.CharField(db_column='RefundModeBankDetails', max_length=100,  null=True)  # Field name made lowercase.
    refundmodechequenumber = models.CharField(db_column='RefundModeChequeNumber', max_length=25,  null=True)  # Field name made lowercase.
    refundmodechequedate = models.DateTimeField(db_column='RefundModeChequeDate', blank=True, null=True)  # Field name made lowercase.
    refundmoderemarks = models.CharField(db_column='RefundModeRemarks', max_length=255,  null=True)  # Field name made lowercase.
    refunduserid = models.IntegerField(db_column='RefundUserID', blank=True, null=True)  # Field name made lowercase.
    accountnumber = models.CharField(db_column='AccountNumber', max_length=200,  null=True)  # Field name made lowercase.
    abnumber = models.CharField(db_column='ABNumber', max_length=20,  null=True)  # Field name made lowercase.
    ispaymentapproved = models.BooleanField(db_column='IsPaymentApproved', blank=True, null=True)  # Field name made lowercase.
    dnglcode = models.IntegerField(db_column='DNGLCode', blank=True, null=True)  # Field name made lowercase.
    dnvoucherid = models.BigIntegerField(db_column='DNVoucherID', blank=True, null=True)  # Field name made lowercase.
    dnpostuserid = models.IntegerField(db_column='DNPostUserID', blank=True, null=True)  # Field name made lowercase.
    dnpostdatetime = models.DateTimeField(db_column='DNPostDateTime', blank=True, null=True)  # Field name made lowercase.
    refundglcode = models.IntegerField(db_column='RefundGLCode', blank=True, null=True)  # Field name made lowercase.
    refundvoucherid = models.BigIntegerField(db_column='RefundVoucherID', blank=True, null=True)  # Field name made lowercase.
    refundpostuserid = models.IntegerField(db_column='RefundPostUserID', blank=True, null=True)  # Field name made lowercase.
    refundpostdatetime = models.DateTimeField(db_column='RefundPostDateTime', blank=True, null=True)  # Field name made lowercase.
    idcoa = models.IntegerField(db_column='IDCOA', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'CancelRefund'


class Certificate(models.Model):
    certificateid = models.AutoField(db_column='CertificateID', primary_key=True)  # Field name made lowercase.
    certificatecodeprefix = models.CharField(db_column='CertificateCodePrefix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    certificatecode = models.IntegerField(db_column='CertificateCode')  # Field name made lowercase.
    certificatecodesuffix = models.CharField(db_column='CertificateCodeSuffix', max_length=20, blank=True, null=True)  # Field name made lowercase.
    registereddate = models.DateTimeField(db_column='RegisteredDate')  # Field name made lowercase.
    isissued = models.IntegerField(db_column='IsIssued')  # Field name made lowercase.
    issuedyear = models.IntegerField(db_column='IssuedYear')  # Field name made lowercase.
    certificateenteredby = models.IntegerField(db_column='CertificateEnteredBy')  # Field name made lowercase.
    certificateentereddate = models.DateTimeField(db_column='CertificateEnteredDate')  # Field name made lowercase.
    certinsurancecompanyid = models.IntegerField(db_column='CertInsuranceCompanyID')  # Field name made lowercase.
    certbranchid = models.IntegerField(db_column='CertBranchID')  # Field name made lowercase.
    certissuedby = models.IntegerField(db_column='CertIssuedBy', blank=True, null=True)  # Field name made lowercase.
    certissueddate = models.DateTimeField(db_column='CertIssuedDate', blank=True, null=True)  # Field name made lowercase.
    certupdatedby = models.IntegerField(db_column='CertUpdatedBy', blank=True, null=True)  # Field name made lowercase.
    certupdateddate = models.DateTimeField(db_column='CertUpdatedDate', blank=True, null=True)  # Field name made lowercase.
    certupdatedscreenname = models.CharField(db_column='CertUpdatedScreenName', max_length=50,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Certificate'


class Client(models.Model):
    clientid = models.AutoField(db_column='ClientID', primary_key=True)  # Field name made lowercase.
    clientname = models.CharField(db_column='ClientName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    clientmobile = models.CharField(db_column='ClientMobile', max_length=50,  null=True)  # Field name made lowercase.
    clientstatus = models.IntegerField(db_column='ClientStatus', blank=True, null=True)  # Field name made lowercase.
    cliententeredby = models.IntegerField(db_column='ClientEnteredBy')  # Field name made lowercase.
    cliententereddate = models.DateTimeField(db_column='ClientEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Client'


class Color(models.Model):
    colorid = models.AutoField(db_column='ColorID', primary_key=True)  # Field name made lowercase.
    coloreng = models.CharField(db_column='ColorEng', max_length=50, blank=True, null=True)  # Field name made lowercase.
    colorarab = models.CharField(db_column='ColorArab', max_length=50,  null=True)  # Field name made lowercase.
    colorenteredby = models.IntegerField(db_column='ColorEnteredBy')  # Field name made lowercase.
    colorentereddate = models.DateTimeField(db_column='ColorEnteredDate')  # Field name made lowercase.
    colorvehtype = models.CharField(db_column='ColorVehType', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Color'


class Commisionrate(models.Model):
    commissionrateid = models.AutoField(db_column='CommissionRateID', primary_key=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    compratepercent = models.DecimalField(db_column='CompRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    tpratepercent = models.DecimalField(db_column='TPRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    exportpercent = models.DecimalField(db_column='ExportPercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    agentcompratepercent = models.DecimalField(db_column='AgentCompRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    agenttpratepercent = models.DecimalField(db_column='AgentTPRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    agentexportratepercent = models.DecimalField(db_column='AgentExportRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    smcompratepercent = models.DecimalField(db_column='SMCompRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    smtpratepercent = models.DecimalField(db_column='SMTPRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    smexportratepercent = models.DecimalField(db_column='SMExportRatePercent', max_digits=10, decimal_places=4)  # Field name made lowercase.
    commissionrateenteredby = models.IntegerField(db_column='CommissionRateEnteredBy')  # Field name made lowercase.
    commissionrateentereddate = models.DateTimeField(db_column='CommissionRateEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'CommisionRate'


class Company(models.Model):
    companyid = models.AutoField(db_column='CompanyID', primary_key=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    companyaddress = models.CharField(db_column='CompanyAddress', max_length=200,  null=True)  # Field name made lowercase.
    companyactivity = models.CharField(db_column='CompanyActivity', max_length=50,  null=True)  # Field name made lowercase.
    companylicenceno = models.CharField(db_column='CompanyLicenceno', max_length=100,  null=True)  # Field name made lowercase.
    companylocation = models.CharField(db_column='CompanyLocation', max_length=50,  null=True)  # Field name made lowercase.
    companylogo = models.CharField(db_column='CompanyLogo', max_length=100,  null=True)  # Field name made lowercase.
    companycopyright = models.CharField(db_column='CompanyCopyright', max_length=100,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Company'


class Comprehensiverate(models.Model):
    comprehensiverateid = models.AutoField(db_column='ComprehensiveRateID', primary_key=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    ageownerfrom = models.IntegerField(db_column='AgeOwnerFrom')  # Field name made lowercase.
    ageownerto = models.IntegerField(db_column='AgeOwnerTo')  # Field name made lowercase.
    agelicensefrom = models.IntegerField(db_column='AgeLicenseFrom')  # Field name made lowercase.
    agelicenseto = models.IntegerField(db_column='AgeLicenseTo')  # Field name made lowercase.
    ratestatus = models.CharField(db_column='RateStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.
    modelid = models.IntegerField(db_column='ModelID')  # Field name made lowercase.
    useofvehicleid = models.IntegerField(db_column='UseOfVehicleID')  # Field name made lowercase.
    bodytypeid = models.IntegerField(db_column='BodyTypeID')  # Field name made lowercase.
    ratepolicytype = models.CharField(db_column='RatePolicyType', max_length=20, blank=True, null=True)  # Field name made lowercase.
    israteagencyrepair = models.BooleanField(db_column='IsRateAgencyRepair')  # Field name made lowercase.
    agencyyear1 = models.DecimalField(db_column='AgencyYear1', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    agencyyear2 = models.DecimalField(db_column='AgencyYear2', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    agencyyear3 = models.DecimalField(db_column='AgencyYear3', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    agencyyear4 = models.DecimalField(db_column='AgencyYear4', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    agencyyear5 = models.DecimalField(db_column='AgencyYear5', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    agencyminimum = models.DecimalField(db_column='AgencyMinimum', max_digits=19, decimal_places=4)  # Field name made lowercase.
    agencyexcess = models.DecimalField(db_column='AgencyExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    nonagencyminpremium = models.DecimalField(db_column='NonAgencyMinPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    nonagencypremium = models.DecimalField(db_column='NonAgencyPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    nonagencyexcess = models.DecimalField(db_column='NonAgencyExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    areaid = models.IntegerField(db_column='AreaID', blank=True, null=True)  # Field name made lowercase.
    surplusareacomppremium = models.DecimalField(db_column='SurplusAreaCompPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusareacompexcess = models.DecimalField(db_column='SurplusAreaCompExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusareacompminimum = models.DecimalField(db_column='SurplusAreaCompMinimum', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusnatcomppremium = models.DecimalField(db_column='SurplusNatCompPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusnatcompexcess = models.DecimalField(db_column='SurplusNatCompExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusnatcompminimum = models.DecimalField(db_column='SurplusNatCompMinimum', max_digits=19, decimal_places=4)  # Field name made lowercase.
    ratedriver = models.DecimalField(db_column='RateDriver', max_digits=19, decimal_places=4)  # Field name made lowercase.
    ratepassenger = models.DecimalField(db_column='RatePassenger', max_digits=19, decimal_places=4)  # Field name made lowercase.
    israteapporved = models.BooleanField(db_column='IsRateApporved')  # Field name made lowercase.
    rateapprovedby = models.IntegerField(db_column='RateApprovedBy')  # Field name made lowercase.
    rateenteredby = models.IntegerField(db_column='RateEnteredBy')  # Field name made lowercase.
    rateentereddate = models.DateTimeField(db_column='RateEnteredDate')  # Field name made lowercase.
    comprcommission = models.DecimalField(db_column='ComprCommission', max_digits=10, decimal_places=4)  # Field name made lowercase.
    compragentcomm = models.DecimalField(db_column='ComprAgentComm', max_digits=10, decimal_places=4)  # Field name made lowercase.
    comprrate = models.DecimalField(db_column='ComprRate', max_digits=10, decimal_places=4)  # Field name made lowercase.
    compratemakeid = models.IntegerField(db_column='CompRateMakeID')  # Field name made lowercase.
    nationalityid = models.IntegerField(db_column='NationalityID', blank=True, null=True)  # Field name made lowercase.
    iscopied = models.IntegerField(db_column='IsCopied', blank=True, null=True)  # Field name made lowercase.
    agdr = models.DecimalField(db_column='AgDR', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    agpassenger = models.DecimalField(db_column='AgPassenger', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    vminvalue = models.IntegerField(db_column='VminValue', blank=True, null=True)  # Field name made lowercase.
    vmaxvalue = models.IntegerField(db_column='VmaxValue', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ComprehensiveRate'


class Copymail(models.Model):
    mailid = models.BigAutoField(db_column='MailID', primary_key=True)  # Field name made lowercase.
    subject = models.CharField(db_column='Subject', max_length=200,  null=True)  # Field name made lowercase.
    messagebody = models.TextField(db_column='MessageBody',  null=True)  # Field name made lowercase.
    fromuserid = models.BigIntegerField(db_column='FromUserID', blank=True, null=True)  # Field name made lowercase.
    touserid = models.BigIntegerField(db_column='ToUserID', blank=True, null=True)  # Field name made lowercase.
    ccuserid = models.BigIntegerField(db_column='CCUserID', blank=True, null=True)  # Field name made lowercase.
    senddate = models.DateTimeField(db_column='SendDate', blank=True, null=True)  # Field name made lowercase.
    isattachment = models.BooleanField(db_column='IsAttachment', blank=True, null=True)  # Field name made lowercase.
    attachmentid = models.CharField(db_column='AttachmentID', max_length=10,  null=True)  # Field name made lowercase.
    isread = models.BooleanField(db_column='IsRead', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    deletedate = models.DateTimeField(db_column='DeleteDate', blank=True, null=True)  # Field name made lowercase.
    isdeleteoutbox = models.BooleanField(db_column='IsDeleteOutBox', blank=True, null=True)  # Field name made lowercase.
    tousername = models.CharField(db_column='ToUserName', max_length=500,  null=True)  # Field name made lowercase.
    common = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'CopyMail'


class Creditcardmaster(models.Model):
    creditcardid = models.BigIntegerField(db_column='CreditCardID', blank=True, null=True)  # Field name made lowercase.
    cardtype = models.CharField(db_column='CardType', max_length=50,  null=True)  # Field name made lowercase.
    bankchargepercentage = models.DecimalField(db_column='BankChargePercentage', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    accountcode = models.CharField(db_column='AccountCode', max_length=50,  null=True)  # Field name made lowercase.
    bankrecratio = models.DecimalField(db_column='BankRecRatio', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'CreditCardMaster'


class Creditinfo(models.Model):
    policyid = models.BigIntegerField(db_column='PolicyID', blank=True, null=True)  # Field name made lowercase.
    policyno = models.CharField(db_column='PolicyNo', max_length=25,  null=True)  # Field name made lowercase.
    creditdays = models.IntegerField(db_column='CreditDays', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=300,  null=True)  # Field name made lowercase.
    abnumber = models.BigIntegerField(db_column='ABNumber', blank=True, null=True)  # Field name made lowercase.
    abname = models.CharField(db_column='ABName', max_length=100,  null=True)  # Field name made lowercase.
    nonmotorpolicyid = models.IntegerField(db_column='NonMotorPolicyID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'CreditInfo'


class Customer(models.Model):
    customerid = models.AutoField(db_column='CustomerID', primary_key=True)  # Field name made lowercase.
    customernameeng = models.TextField(db_column='CustomerNameEng',  null=True)  # Field name made lowercase.
    customernamearab = models.TextField(db_column='CustomerNameArab',  null=True)  # Field name made lowercase.
    custraddengline1 = models.CharField(db_column='CustrAddEngLine1', max_length=300,  null=True)  # Field name made lowercase.
    customeraddengline2 = models.CharField(db_column='CustomerAddEngLine2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    customerphone = models.CharField(db_column='CustomerPhone', max_length=20, blank=True, null=True)  # Field name made lowercase.
    customermobile = models.CharField(db_column='CustomerMobile', max_length=30,  null=True)  # Field name made lowercase.
    nationalityid = models.IntegerField(db_column='NationalityID')  # Field name made lowercase.
    customercity = models.CharField(db_column='CustomerCity', max_length=20, blank=True, null=True)  # Field name made lowercase.
    customeremail = models.CharField(db_column='CustomerEmail', max_length=50,  null=True)  # Field name made lowercase.
    customerdob = models.DateTimeField(db_column='CustomerDOB')  # Field name made lowercase.
    custlicenseissuedate = models.DateTimeField(db_column='CustLicenseIssueDate')  # Field name made lowercase.
    custlicenseno = models.CharField(db_column='CustLicenseNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custenteredby = models.IntegerField(db_column='CustEnteredBy')  # Field name made lowercase.
    custentereddate = models.DateTimeField(db_column='CustEnteredDate')  # Field name made lowercase.
    custpassportno = models.CharField(db_column='CustPassportNo', max_length=100,  null=True)  # Field name made lowercase.
    custpassportissuedate = models.DateTimeField(db_column='CustPassportIssueDate', blank=True, null=True)  # Field name made lowercase.
    customersex = models.CharField(db_column='CustomerSex', max_length=10, blank=True, null=True)  # Field name made lowercase.
    custpassportexpirydate = models.DateTimeField(db_column='CustPassportExpiryDate', blank=True, null=True)  # Field name made lowercase.
    custaddengline3 = models.CharField(db_column='CustAddEngLine3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custaddarabline1 = models.CharField(db_column='CustAddArabLine1', max_length=300,  null=True)  # Field name made lowercase.
    custaddarabline2 = models.CharField(db_column='CustAddArabLine2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custaddarabline3 = models.CharField(db_column='CustAddArabLine3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custmotorpolicyid = models.IntegerField(db_column='CustMotorPolicyID', blank=True, null=True)  # Field name made lowercase.
    cusubledgerid = models.IntegerField(db_column='CuSubLedgerID', blank=True, null=True)  # Field name made lowercase.
    isblocked = models.BooleanField(db_column='IsBlocked', blank=True, null=True)  # Field name made lowercase.
    motorpolicydate = models.DateTimeField(db_column='MotorPolicyDate', blank=True, null=True)  # Field name made lowercase.
    branchid = models.IntegerField(db_column='BranchID', blank=True, null=True)  # Field name made lowercase.
    cuidaddressbook = models.IntegerField(db_column='CuIdAddressBook', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Customer'


class Customeraudit(models.Model):
    customerauditid = models.AutoField(db_column='CustomerAuditID', primary_key=True)  # Field name made lowercase.
    customerid = models.IntegerField(db_column='CustomerID')  # Field name made lowercase.
    customernameeng = models.TextField(db_column='CustomerNameEng',  null=True)  # Field name made lowercase.
    customernamearab = models.TextField(db_column='CustomerNameArab',  null=True)  # Field name made lowercase.
    custraddengline1 = models.CharField(db_column='CustrAddEngLine1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    customeraddengline2 = models.CharField(db_column='CustomerAddEngLine2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    customerphone = models.CharField(db_column='CustomerPhone', max_length=20, blank=True, null=True)  # Field name made lowercase.
    customermobile = models.CharField(db_column='CustomerMobile', max_length=20, blank=True, null=True)  # Field name made lowercase.
    nationalityid = models.IntegerField(db_column='NationalityID')  # Field name made lowercase.
    customercity = models.CharField(db_column='CustomerCity', max_length=20, blank=True, null=True)  # Field name made lowercase.
    customeremail = models.CharField(db_column='CustomerEmail', max_length=25, blank=True, null=True)  # Field name made lowercase.
    customerdob = models.DateTimeField(db_column='CustomerDOB')  # Field name made lowercase.
    custlicenseissuedate = models.DateTimeField(db_column='CustLicenseIssueDate')  # Field name made lowercase.
    custlicenseno = models.CharField(db_column='CustLicenseNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custenteredby = models.IntegerField(db_column='CustEnteredBy')  # Field name made lowercase.
    custentereddate = models.DateTimeField(db_column='CustEnteredDate')  # Field name made lowercase.
    custpassportno = models.CharField(db_column='CustPassportNo', max_length=100,  null=True)  # Field name made lowercase.
    custpassportissuedate = models.DateTimeField(db_column='CustPassportIssueDate', blank=True, null=True)  # Field name made lowercase.
    customersex = models.CharField(db_column='CustomerSex', max_length=10, blank=True, null=True)  # Field name made lowercase.
    custpassportexpirydate = models.DateTimeField(db_column='CustPassportExpiryDate', blank=True, null=True)  # Field name made lowercase.
    custaddengline3 = models.CharField(db_column='CustAddEngLine3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custaddarabline1 = models.CharField(db_column='CustAddArabLine1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custaddarabline2 = models.CharField(db_column='CustAddArabLine2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custaddarabline3 = models.CharField(db_column='CustAddArabLine3', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'CustomerAudit'


class Customerhistory(models.Model):
    customerhistoryid = models.AutoField(db_column='CustomerHistoryID', primary_key=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'CustomerHistory'


class Department(models.Model):
    departmentid = models.IntegerField(db_column='DepartmentID', primary_key=True)  # Field name made lowercase.
    departmenteng = models.CharField(db_column='DepartmentEng', max_length=50,  null=True)  # Field name made lowercase.
    departmentarab = models.CharField(db_column='DepartmentArab', max_length=50,  null=True)  # Field name made lowercase.
    departmententeredby = models.IntegerField(db_column='DepartmentEnteredBy')  # Field name made lowercase.
    departmententereddate = models.DateTimeField(db_column='DepartmentEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Department'


class Designation(models.Model):
    designationid = models.IntegerField(db_column='DesignationID', primary_key=True)  # Field name made lowercase.
    designationeng = models.CharField(db_column='DesignationEng', max_length=50,  null=True)  # Field name made lowercase.
    designationarab = models.CharField(db_column='DesignationArab', max_length=50,  null=True)  # Field name made lowercase.
    designationenteredby = models.IntegerField(db_column='DesignationEnteredBy')  # Field name made lowercase.
    designationentereddate = models.DateTimeField(db_column='DesignationEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Designation'


class Email(models.Model):
    mailid = models.BigAutoField(db_column='MailID', primary_key=True)  # Field name made lowercase.
    subject = models.CharField(db_column='Subject', max_length=200,  null=True)  # Field name made lowercase.
    messagebody = models.TextField(db_column='MessageBody',  null=True)  # Field name made lowercase.
    fromuserid = models.BigIntegerField(db_column='FromUserID', blank=True, null=True)  # Field name made lowercase.
    touserid = models.BigIntegerField(db_column='ToUserID', blank=True, null=True)  # Field name made lowercase.
    ccuserid = models.BigIntegerField(db_column='CCUserID', blank=True, null=True)  # Field name made lowercase.
    senddate = models.DateTimeField(db_column='SendDate', blank=True, null=True)  # Field name made lowercase.
    isattachment = models.BooleanField(db_column='IsAttachment', blank=True, null=True)  # Field name made lowercase.
    attachmentid = models.CharField(db_column='AttachmentID', max_length=10,  null=True)  # Field name made lowercase.
    isread = models.BooleanField(db_column='IsRead', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    deletedate = models.DateTimeField(db_column='DeleteDate', blank=True, null=True)  # Field name made lowercase.
    isdeleteoutbox = models.BooleanField(db_column='IsDeleteOutBox', blank=True, null=True)  # Field name made lowercase.
    common1 = models.DateTimeField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Email'


class Endorsereason(models.Model):
    endorsereasonid = models.AutoField(db_column='EndorseReasonID', primary_key=True)  # Field name made lowercase.
    reasonenteredby = models.IntegerField(db_column='ReasonEnteredBy')  # Field name made lowercase.
    reasonentereddate = models.DateTimeField(db_column='ReasonEnteredDate')  # Field name made lowercase.
    endorsementarab = models.CharField(db_column='EndorsementArab', max_length=50, blank=True, null=True)  # Field name made lowercase.
    endorsementeng = models.CharField(db_column='EndorsementEng', max_length=50, blank=True, null=True)  # Field name made lowercase.
    endorsementvehtype = models.CharField(db_column='EndorsementVehType', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'EndorseReason'


class Exceptionalvehicles(models.Model):
    exceptionalvehiclesid = models.AutoField(db_column='ExceptionalVehiclesID', primary_key=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    excepmakeid = models.IntegerField(db_column='ExcepMakeID')  # Field name made lowercase.
    modelid = models.IntegerField(db_column='ModelID')  # Field name made lowercase.
    bodytypeid = models.IntegerField(db_column='BodyTypeID')  # Field name made lowercase.
    exceptionalpremium = models.DecimalField(db_column='ExceptionalPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    exceptionalcommission = models.DecimalField(db_column='ExceptionalCommission', max_digits=19, decimal_places=4)  # Field name made lowercase.
    excepenteredby = models.IntegerField(db_column='ExcepEnteredBy')  # Field name made lowercase.
    excepentereddate = models.DateTimeField(db_column='ExcepEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ExceptionalVehicles'


class Exportrate(models.Model):
    exportrateid = models.AutoField(db_column='ExportRateID', primary_key=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    expageownerfrom = models.IntegerField(db_column='ExpAgeOwnerFrom')  # Field name made lowercase.
    expageownerto = models.IntegerField(db_column='ExpAgeOwnerTo')  # Field name made lowercase.
    expagelicensefrom = models.IntegerField(db_column='ExpAgeLicenseFrom')  # Field name made lowercase.
    expagelicenseto = models.IntegerField(db_column='ExpAgeLicenseTo')  # Field name made lowercase.
    expstatus = models.CharField(db_column='ExpStatus', max_length=20, blank=True, null=True)  # Field name made lowercase.
    bodytypeid = models.IntegerField(db_column='BodyTypeID')  # Field name made lowercase.
    exppremium = models.DecimalField(db_column='ExpPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    expdays = models.IntegerField(db_column='ExpDays')  # Field name made lowercase.
    expapprovedby = models.IntegerField(db_column='ExpApprovedBy')  # Field name made lowercase.
    expennteredby = models.IntegerField(db_column='ExpEnnteredBy')  # Field name made lowercase.
    expentereddate = models.DateTimeField(db_column='ExpEnteredDate')  # Field name made lowercase.
    expcommision = models.DecimalField(db_column='ExpCommision', max_digits=19, decimal_places=4)  # Field name made lowercase.
    expareaminium = models.DecimalField(db_column='ExpAreaMinium', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    expareaexcess = models.DecimalField(db_column='ExpAreaExcess', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    expareapremium = models.DecimalField(db_column='ExpAreaPremium', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    expnatminimum = models.DecimalField(db_column='ExpNatMinimum', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    expnatexcess = models.DecimalField(db_column='ExpNatExcess', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    expnatpremium = models.DecimalField(db_column='ExpNatPremium', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    nationalityid = models.ForeignKey('Nationality', models.DO_NOTHING, db_column='NationalityID', blank=True, null=True)  # Field name made lowercase.
    areaid = models.ForeignKey(Area, models.DO_NOTHING, db_column='AreaID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ExportRate'


class Fees(models.Model):
    feesid = models.AutoField(db_column='FeesID', primary_key=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    insfeestype = models.CharField(db_column='InsFeesType', max_length=20, blank=True, null=True)  # Field name made lowercase.
    insfeesamount = models.DecimalField(db_column='InsFeesAmount', max_digits=19, decimal_places=4)  # Field name made lowercase.
    insnoncommfees = models.DecimalField(db_column='InsNonCommFees', max_digits=19, decimal_places=4)  # Field name made lowercase.
    servicefees = models.DecimalField(db_column='ServiceFees', max_digits=19, decimal_places=4)  # Field name made lowercase.
    feesenteredby = models.IntegerField(db_column='FeesEnteredBy')  # Field name made lowercase.
    feesentereddate = models.DateTimeField(db_column='FeesEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Fees'


class Insurancecompany(models.Model):
    insurancecompanyid = models.AutoField(db_column='InsuranceCompanyID', primary_key=True)  # Field name made lowercase.
    addressbookid = models.IntegerField(db_column='AddressBookID')  # Field name made lowercase.
    subledgercode = models.CharField(db_column='SubLedgerCode', max_length=10,  null=True)  # Field name made lowercase.
    insurancecompanyarab = models.CharField(db_column='InsuranceCompanyArab', max_length=50,  null=True)  # Field name made lowercase.
    inscompaddressengline1 = models.CharField(db_column='InsCompAddressEngLine1', max_length=40,  null=True)  # Field name made lowercase.
    inscompaddressengline2 = models.CharField(db_column='InsCompAddressEngLine2', max_length=40,  null=True)  # Field name made lowercase.
    inscompaddressengline3 = models.CharField(db_column='InsCompAddressEngLine3', max_length=40,  null=True)  # Field name made lowercase.
    inscompaddressarabline1 = models.CharField(db_column='InsCompAddressArabLine1', max_length=40,  null=True)  # Field name made lowercase.
    inscompaddressarabline2 = models.CharField(db_column='InsCompAddressArabLine2', max_length=40,  null=True)  # Field name made lowercase.
    inscompaddressarabline3 = models.CharField(db_column='InsCompAddressArabLine3', max_length=40,  null=True)  # Field name made lowercase.
    insurancecompanyeng = models.CharField(db_column='InsuranceCompanyEng', max_length=50, blank=True, null=True)  # Field name made lowercase.
    inscomphone1 = models.CharField(db_column='InsComPhone1', max_length=20,  null=True)  # Field name made lowercase.
    inscompemail = models.CharField(db_column='InsCompEmail', max_length=30,  null=True)  # Field name made lowercase.
    inscompenteredby = models.IntegerField(db_column='InsCompEnteredBy')  # Field name made lowercase.
    inscompentereddate = models.DateTimeField(db_column='InsCompEnteredDate')  # Field name made lowercase.
    inscompwebsite = models.CharField(db_column='InsCompWebSite', max_length=25, blank=True, null=True)  # Field name made lowercase.
    inscompcommenteng = models.CharField(db_column='InsCompCommentEng', max_length=100, blank=True, null=True)  # Field name made lowercase.
    inscompcommentarab = models.CharField(db_column='InsCompCommentArab', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isadminhold = models.BooleanField(db_column='IsAdminHold')  # Field name made lowercase.
    isduplicatecertificate = models.BooleanField(db_column='IsDuplicateCertificate')  # Field name made lowercase.
    isduplicatepolicyno = models.BooleanField(db_column='IsDuplicatePolicyNo')  # Field name made lowercase.
    rptlayoutthirdparty = models.CharField(db_column='RptLayoutThirdParty', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rptlayoutcomprehensive = models.CharField(db_column='RptLayoutComprehensive', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rptlayoutexport = models.CharField(db_column='RptLayoutExport', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rtainsurancecompcode = models.IntegerField(db_column='RTAInsuranceCompCode', blank=True, null=True)  # Field name made lowercase.
    policyno = models.CharField(db_column='PolicyNo', max_length=50,  null=True)  # Field name made lowercase.
    tpartypolicyno = models.CharField(db_column='TPartyPolicyNo', max_length=50,  null=True)  # Field name made lowercase.
    comprjisfee = models.DecimalField(db_column='ComprJISFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    comprinscofee = models.DecimalField(db_column='ComprInsCoFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    iscomprfeecommission = models.BooleanField(db_column='IsComprFeeCommission', blank=True, null=True)  # Field name made lowercase.
    thirdpartyjisfee = models.DecimalField(db_column='ThirdPartyJISFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    thirdpartyinscofee = models.DecimalField(db_column='ThirdPartyInsCoFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    isthirdpartyfeecommission = models.BooleanField(db_column='IsThirdPartyFeeCommission', blank=True, null=True)  # Field name made lowercase.
    exportjisfee = models.DecimalField(db_column='ExportJISFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    exporinscofee = models.DecimalField(db_column='ExporInsCoFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    isexporfeecommission = models.BooleanField(db_column='IsExporFeeCommission', blank=True, null=True)  # Field name made lowercase.
    compyear = models.IntegerField(db_column='CompYear', blank=True, null=True)  # Field name made lowercase.
    tpyear = models.IntegerField(db_column='TPYear', blank=True, null=True)  # Field name made lowercase.
    icidaddressbook = models.IntegerField(db_column='IcIdAddressBook', blank=True, null=True)  # Field name made lowercase.
    comprjisfee_endorse = models.DecimalField(db_column='ComprJISFee_Endorse', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    comprinscofee_endorse = models.DecimalField(db_column='ComprInsCoFee_Endorse', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    thirdpartyjisfee_endorse = models.DecimalField(db_column='ThirdPartyJISFee_Endorse', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    thirdpartyinscofee_endorse = models.DecimalField(db_column='ThirdPartyInsCoFee_Endorse', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    exportjisfee_endorse = models.DecimalField(db_column='ExportJISFee_Endorse', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    exporinscofee_endorse = models.DecimalField(db_column='ExporInsCoFee_Endorse', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    dtnosaleson = models.DateTimeField(db_column='dtNoSalesOn', blank=True, null=True)  # Field name made lowercase.
    dtnosalesonflag = models.BooleanField(db_column='dtNoSalesOnFlag', blank=True, null=True)  # Field name made lowercase.
    autonumberingornot = models.BooleanField(db_column='AutoNumberingOrNot', blank=True, null=True)  # Field name made lowercase.
    thirdpartyformat = models.CharField(db_column='ThirdPartyFormat', max_length=50,  null=True)  # Field name made lowercase.
    format = models.CharField(db_column='Format', max_length=50,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'InsuranceCompany'


class Insurancetype(models.Model):
    insurancetypeid = models.AutoField(db_column='InsuranceTypeID', primary_key=True)  # Field name made lowercase.
    insurancetype = models.CharField(db_column='InsuranceType', max_length=50,  null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=150,  null=True)  # Field name made lowercase.
    glcash = models.IntegerField(db_column='GLCash', blank=True, null=True)  # Field name made lowercase.
    glcc = models.IntegerField(db_column='GLCC', blank=True, null=True)  # Field name made lowercase.
    glcheque = models.IntegerField(db_column='GLCheque', blank=True, null=True)  # Field name made lowercase.
    glcredit = models.IntegerField(db_column='GLCredit', blank=True, null=True)  # Field name made lowercase.
    sysnumber = models.IntegerField(db_column='SysNumber', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'InsuranceType'


class Make(models.Model):
    makeid = models.AutoField(db_column='MakeID', primary_key=True)  # Field name made lowercase.
    makeeng = models.CharField(db_column='MakeEng', max_length=30, blank=True, null=True)  # Field name made lowercase.
    makearab = models.CharField(db_column='MakeArab', max_length=50,  null=True)  # Field name made lowercase.
    makeenteredby = models.IntegerField(db_column='MakeEnteredBy')  # Field name made lowercase.
    makeentereddate = models.DateTimeField(db_column='MakeEnteredDate')  # Field name made lowercase.
    makevehtype = models.CharField(db_column='MakeVehType', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Make'


class Model(models.Model):
    modelid = models.AutoField(db_column='ModelID', primary_key=True)  # Field name made lowercase.
    modeleng = models.CharField(db_column='ModelEng', max_length=40, blank=True, null=True)  # Field name made lowercase.
    modelarab = models.CharField(db_column='ModelArab', max_length=50,  null=True)  # Field name made lowercase.
    makeid = models.ForeignKey(Make, models.DO_NOTHING, db_column='MakeID')  # Field name made lowercase.
    modeenteredby = models.IntegerField(db_column='ModeEnteredBy')  # Field name made lowercase.
    modelentereddate = models.DateTimeField(db_column='ModelEnteredDate')  # Field name made lowercase.
    modelvehtype = models.CharField(db_column='ModelVehType', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Model'


class Motorpolicy(models.Model):
    motorpolicyid = models.AutoField(db_column='MotorPolicyID', primary_key=True)  # Field name made lowercase.
    certificateid = models.ForeignKey(Certificate, models.DO_NOTHING, db_column='CertificateID')  # Field name made lowercase.
    tfc = models.DecimalField(db_column='TFC', max_digits=19, decimal_places=4)  # Field name made lowercase.
    net = models.DecimalField(db_column='NET', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    policystatus = models.CharField(db_column='PolicyStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.
    policynumber = models.CharField(db_column='PolicyNumber', max_length=25, blank=True, null=True)  # Field name made lowercase.
    brokerid = models.ForeignKey(Broker, models.DO_NOTHING, db_column='BrokerID', blank=True, null=True)  # Field name made lowercase.
    areaid = models.ForeignKey(Area, models.DO_NOTHING, db_column='AreaID', blank=True, null=True)  # Field name made lowercase.
    salesmanid = models.IntegerField(db_column='SalesmanID', blank=True, null=True)  # Field name made lowercase.
    areaexcess = models.DecimalField(db_column='AreaExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    dateissue = models.DateTimeField(db_column='DateIssue')  # Field name made lowercase.
    datestart = models.DateTimeField(db_column='DateStart')  # Field name made lowercase.
    dateend = models.DateTimeField(db_column='DateEnd')  # Field name made lowercase.
    isagencyrepair = models.BooleanField(db_column='IsAgencyRepair', blank=True, null=True)  # Field name made lowercase.
    vehiclevalue = models.DecimalField(db_column='VehicleValue', max_digits=19, decimal_places=4)  # Field name made lowercase.
    grosspremium = models.DecimalField(db_column='GrossPremium', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    soldfor = models.DecimalField(db_column='SoldFor', max_digits=19, decimal_places=4)  # Field name made lowercase.
    excess = models.DecimalField(db_column='Excess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    commission = models.IntegerField(db_column='Commission')  # Field name made lowercase.
    isdriverinsured = models.BooleanField(db_column='IsDriverInsured')  # Field name made lowercase.
    noofpassengers = models.IntegerField(db_column='NoOfPassengers')  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    voucherid = models.IntegerField(db_column='VoucherID', blank=True, null=True)  # Field name made lowercase.
    isposted = models.BooleanField(db_column='IsPosted', blank=True, null=True)  # Field name made lowercase.
    isreceiptprinted = models.BooleanField(db_column='IsReceiptPrinted', blank=True, null=True)  # Field name made lowercase.
    ispolicyprinted = models.BooleanField(db_column='IsPolicyPrinted', blank=True, null=True)  # Field name made lowercase.
    dateposted = models.DateTimeField(db_column='DatePosted', blank=True, null=True)  # Field name made lowercase.
    userpostedid = models.IntegerField(db_column='UserPostedID', blank=True, null=True)  # Field name made lowercase.
    receiptprinteduserid = models.IntegerField(db_column='ReceiptPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    policyprinteduserid = models.IntegerField(db_column='PolicyPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    receiptnumber = models.BigIntegerField(db_column='ReceiptNumber', blank=True, null=True)  # Field name made lowercase.
    glcode = models.CharField(db_column='GLCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    creditaddressbookid = models.IntegerField(db_column='CreditAddressBookID')  # Field name made lowercase.
    policyentered = models.DateTimeField(db_column='PolicyEntered')  # Field name made lowercase.
    policyenteredby = models.IntegerField(db_column='PolicyEnteredBy')  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    year = models.CharField(db_column='Year', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paymodeid = models.IntegerField(db_column='PayModeID', blank=True, null=True)  # Field name made lowercase.
    policyapprovedby = models.IntegerField(db_column='PolicyApprovedBy', blank=True, null=True)  # Field name made lowercase.
    totalfees = models.DecimalField(db_column='TotalFees', max_digits=19, decimal_places=4)  # Field name made lowercase.
    cancelstatus = models.CharField(db_column='CancelStatus', max_length=20,  null=True)  # Field name made lowercase.
    canceldate = models.DateTimeField(db_column='CancelDate', blank=True, null=True)  # Field name made lowercase.
    isexportedtorta = models.BooleanField(db_column='IsExportedToRTA', blank=True, null=True)  # Field name made lowercase.
    isexportedtoinsco = models.BooleanField(db_column='IsExportedToInsCo', blank=True, null=True)  # Field name made lowercase.
    vehicledetailid = models.IntegerField(db_column='VehicleDetailID')  # Field name made lowercase.
    agentcommssion = models.DecimalField(db_column='AgentCommssion', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    brokercommission = models.DecimalField(db_column='BrokerCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    policytypeid = models.IntegerField(db_column='PolicyTypeID')  # Field name made lowercase.
    customerid = models.ForeignKey(Customer, models.DO_NOTHING, db_column='CustomerID')  # Field name made lowercase.
    endorsereasonid = models.ForeignKey(Endorsereason, models.DO_NOTHING, db_column='EndorseReasonID', blank=True, null=True)  # Field name made lowercase.
    noncommfees = models.DecimalField(db_column='NonCommFees', max_digits=19, decimal_places=4)  # Field name made lowercase.
    isendorsement = models.BooleanField(db_column='IsEndorsement', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='IsApproved', blank=True, null=True)  # Field name made lowercase.
    receiptprinteddate = models.DateTimeField(db_column='ReceiptPrintedDate', blank=True, null=True)  # Field name made lowercase.
    policyprinteddate = models.DateTimeField(db_column='PolicyPrintedDate', blank=True, null=True)  # Field name made lowercase.
    approveddatetime = models.DateTimeField(db_column='ApprovedDateTime', blank=True, null=True)  # Field name made lowercase.
    insurancecompanyid = models.ForeignKey(Insurancecompany, models.DO_NOTHING, db_column='InsuranceCompanyID')  # Field name made lowercase.
    branchid = models.ForeignKey(Branch, models.DO_NOTHING, db_column='BranchID')  # Field name made lowercase.
    userapprovedid = models.IntegerField(db_column='UserApprovedID', blank=True, null=True)  # Field name made lowercase.
    commssion = models.DecimalField(db_column='Commssion', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    smcommission = models.DecimalField(db_column='SMCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    endtemp = models.CharField(db_column='EndTemp', max_length=100,  null=True)  # Field name made lowercase.
    isexportedtoolddb = models.BooleanField(db_column='IsExportedToOldDB', blank=True, null=True)  # Field name made lowercase.
    ejisfee = models.DecimalField(db_column='EJISFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    inscommissionfee = models.DecimalField(db_column='InsCommissionFee', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    ccbankcharges = models.DecimalField(db_column='ccBankCharges', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    cashreceivedamount = models.DecimalField(db_column='CashReceivedAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    ccreceivedamount = models.DecimalField(db_column='CCReceivedAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    chequereceivedamount = models.DecimalField(db_column='ChequeReceivedAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    creditreceivedamount = models.DecimalField(db_column='CreditReceivedAmount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=400,  null=True)  # Field name made lowercase.
    dltremarks = models.CharField(db_column='DltRemarks', max_length=400,  null=True)  # Field name made lowercase.
    original_tfc = models.DecimalField(db_column='Original_TFC', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    original_soldfor = models.DecimalField(db_column='Original_SoldFor', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    newinvoiceamount = models.DecimalField(db_column='NewInvoiceAmount', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    aacode = models.CharField(db_column='AACode', max_length=20,  null=True)  # Field name made lowercase.
    class Meta:
        # managed = False
        db_table = 'MotorPolicy'


class Motorpolicyaudit(models.Model):
    motorpolicyauditid = models.AutoField(db_column='MotorPolicyAuditID', primary_key=True)  # Field name made lowercase.
    motorpolicyid = models.IntegerField(db_column='MotorPolicyID')  # Field name made lowercase.
    certificateid = models.IntegerField(db_column='CertificateID')  # Field name made lowercase.
    tfc = models.DecimalField(db_column='TFC', max_digits=19, decimal_places=4)  # Field name made lowercase.
    net = models.DecimalField(db_column='NET', max_digits=19, decimal_places=4)  # Field name made lowercase.
    policystatus = models.CharField(db_column='PolicyStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.
    policynumber = models.CharField(db_column='PolicyNumber', max_length=25, blank=True, null=True)  # Field name made lowercase.
    brokerid = models.IntegerField(db_column='BrokerID', blank=True, null=True)  # Field name made lowercase.
    areaid = models.IntegerField(db_column='AreaID', blank=True, null=True)  # Field name made lowercase.
    salesmanid = models.IntegerField(db_column='SalesmanID', blank=True, null=True)  # Field name made lowercase.
    areaexcess = models.DecimalField(db_column='AreaExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    dateissue = models.DateTimeField(db_column='DateIssue')  # Field name made lowercase.
    datestart = models.DateTimeField(db_column='DateStart')  # Field name made lowercase.
    dateend = models.DateTimeField(db_column='DateEnd')  # Field name made lowercase.
    isagencyrepair = models.BooleanField(db_column='IsAgencyRepair', blank=True, null=True)  # Field name made lowercase.
    vehiclevalue = models.DecimalField(db_column='VehicleValue', max_digits=19, decimal_places=4)  # Field name made lowercase.
    grosspremium = models.DecimalField(db_column='GrossPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    soldfor = models.DecimalField(db_column='SoldFor', max_digits=19, decimal_places=4)  # Field name made lowercase.
    excess = models.DecimalField(db_column='Excess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    commission = models.IntegerField(db_column='Commission')  # Field name made lowercase.
    aacode = models.CharField(db_column='AACode', max_length=20,  null=True)  # Field name made lowercase.
    isdriverinsured = models.BooleanField(db_column='IsDriverInsured')  # Field name made lowercase.
    noofpassengers = models.IntegerField(db_column='NoOfPassengers')  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    voucherid = models.IntegerField(db_column='VoucherID', blank=True, null=True)  # Field name made lowercase.
    isposted = models.BooleanField(db_column='IsPosted', blank=True, null=True)  # Field name made lowercase.
    isreceiptprinted = models.BooleanField(db_column='IsReceiptPrinted', blank=True, null=True)  # Field name made lowercase.
    ispolicyprinted = models.BooleanField(db_column='IsPolicyPrinted', blank=True, null=True)  # Field name made lowercase.
    dateposted = models.DateTimeField(db_column='DatePosted', blank=True, null=True)  # Field name made lowercase.
    userpostedid = models.IntegerField(db_column='UserPostedID', blank=True, null=True)  # Field name made lowercase.
    receiptprinteduserid = models.IntegerField(db_column='ReceiptPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    policyprinteduserid = models.IntegerField(db_column='PolicyPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    receiptnumber = models.CharField(db_column='ReceiptNumber', max_length=50,  null=True)  # Field name made lowercase.
    glcode = models.CharField(db_column='GLCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    creditaddressbookid = models.IntegerField(db_column='CreditAddressBookID')  # Field name made lowercase.
    policyentered = models.DateTimeField(db_column='PolicyEntered')  # Field name made lowercase.
    policyenteredby = models.IntegerField(db_column='PolicyEnteredBy')  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    year = models.CharField(db_column='Year', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paymodeid = models.IntegerField(db_column='PayModeID', blank=True, null=True)  # Field name made lowercase.
    policyapprovedby = models.IntegerField(db_column='PolicyApprovedBy', blank=True, null=True)  # Field name made lowercase.
    totalfees = models.DecimalField(db_column='TotalFees', max_digits=19, decimal_places=4)  # Field name made lowercase.
    cancelstatus = models.CharField(db_column='CancelStatus', max_length=20,  null=True)  # Field name made lowercase.
    canceldate = models.DateTimeField(db_column='CancelDate', blank=True, null=True)  # Field name made lowercase.
    isexportedtorta = models.BooleanField(db_column='IsExportedToRTA', blank=True, null=True)  # Field name made lowercase.
    isexportedtoinsco = models.BooleanField(db_column='IsExportedToInsCo', blank=True, null=True)  # Field name made lowercase.
    vehicledetailid = models.IntegerField(db_column='VehicleDetailID')  # Field name made lowercase.
    agentcommssion = models.DecimalField(db_column='AgentCommssion', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    brokercommission = models.DecimalField(db_column='BrokerCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    policytypeid = models.IntegerField(db_column='PolicyTypeID')  # Field name made lowercase.
    customerid = models.IntegerField(db_column='CustomerID')  # Field name made lowercase.
    endorsereasonid = models.IntegerField(db_column='EndorseReasonID', blank=True, null=True)  # Field name made lowercase.
    noncommfees = models.DecimalField(db_column='NonCommFees', max_digits=19, decimal_places=4)  # Field name made lowercase.
    isendorsement = models.BooleanField(db_column='IsEndorsement', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='IsApproved', blank=True, null=True)  # Field name made lowercase.
    receiptprinteddate = models.DateTimeField(db_column='ReceiptPrintedDate', blank=True, null=True)  # Field name made lowercase.
    policyprinteddate = models.DateTimeField(db_column='PolicyPrintedDate', blank=True, null=True)  # Field name made lowercase.
    approveddatetime = models.DateTimeField(db_column='ApprovedDateTime', blank=True, null=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    branchid = models.IntegerField(db_column='BranchID')  # Field name made lowercase.
    smcommission = models.DecimalField(db_column='SMCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    commssion = models.DecimalField(db_column='Commssion', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    userapprovedid = models.IntegerField(db_column='UserApprovedID', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=400,  null=True)  # Field name made lowercase.
    updateby = models.IntegerField(db_column='updateBy', blank=True, null=True)  # Field name made lowercase.
    updatedate = models.DateTimeField(db_column='updateDate', blank=True, null=True)  # Field name made lowercase.
    dltremarks = models.CharField(db_column='DltRemarks', max_length=400,  null=True)  # Field name made lowercase.
    deleteddate = models.DateTimeField(db_column='deletedDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'MotorPolicyAudit'


class Motorpolicyhistory(models.Model):
    motorpolicyhistoryid = models.AutoField(db_column='MotorPolicyHistoryID', primary_key=True)  # Field name made lowercase.
    motorpolicyid = models.IntegerField(db_column='MotorPolicyID')  # Field name made lowercase.
    certificateid = models.IntegerField(db_column='CertificateID')  # Field name made lowercase.
    tfc = models.DecimalField(db_column='TFC', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    net = models.DecimalField(db_column='NET', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    policystatus = models.CharField(db_column='PolicyStatus', max_length=10,  null=True)  # Field name made lowercase.
    policynumber = models.CharField(db_column='PolicyNumber', max_length=25,  null=True)  # Field name made lowercase.
    brokerid = models.IntegerField(db_column='BrokerID', blank=True, null=True)  # Field name made lowercase.
    areaid = models.IntegerField(db_column='AreaID', blank=True, null=True)  # Field name made lowercase.
    salesmanid = models.IntegerField(db_column='SalesmanID', blank=True, null=True)  # Field name made lowercase.
    areaexcess = models.DecimalField(db_column='AreaExcess', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    dateissue = models.DateTimeField(db_column='DateIssue', blank=True, null=True)  # Field name made lowercase.
    datestart = models.DateTimeField(db_column='DateStart', blank=True, null=True)  # Field name made lowercase.
    dateend = models.DateTimeField(db_column='DateEnd', blank=True, null=True)  # Field name made lowercase.
    isagencyrepair = models.BooleanField(db_column='IsAgencyRepair', blank=True, null=True)  # Field name made lowercase.
    vehiclevalue = models.DecimalField(db_column='VehicleValue', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    grosspremium = models.DecimalField(db_column='GrossPremium', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    soldfor = models.DecimalField(db_column='SoldFor', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    excess = models.DecimalField(db_column='Excess', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    commission = models.IntegerField(db_column='Commission', blank=True, null=True)  # Field name made lowercase.
    aacode = models.CharField(db_column='AACode', max_length=20,  null=True)  # Field name made lowercase.
    isdriverinsured = models.BooleanField(db_column='IsDriverInsured', blank=True, null=True)  # Field name made lowercase.
    noofpassengers = models.IntegerField(db_column='NoOfPassengers', blank=True, null=True)  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=10,  null=True)  # Field name made lowercase.
    voucherid = models.IntegerField(db_column='VoucherID', blank=True, null=True)  # Field name made lowercase.
    isposted = models.BooleanField(db_column='IsPosted', blank=True, null=True)  # Field name made lowercase.
    isreceiptprinted = models.BooleanField(db_column='IsReceiptPrinted', blank=True, null=True)  # Field name made lowercase.
    ispolicyprinted = models.BooleanField(db_column='IsPolicyPrinted', blank=True, null=True)  # Field name made lowercase.
    dateposted = models.DateTimeField(db_column='DatePosted', blank=True, null=True)  # Field name made lowercase.
    userpostedid = models.IntegerField(db_column='UserPostedID', blank=True, null=True)  # Field name made lowercase.
    receiptprinteduserid = models.IntegerField(db_column='ReceiptPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    policyprinteduserid = models.IntegerField(db_column='PolicyPrintedUserID', blank=True, null=True)  # Field name made lowercase.
    receiptnumber = models.CharField(db_column='ReceiptNumber', max_length=50,  null=True)  # Field name made lowercase.
    glcode = models.CharField(db_column='GLCode', max_length=20,  null=True)  # Field name made lowercase.
    creditaddressbookid = models.IntegerField(db_column='CreditAddressBookID', blank=True, null=True)  # Field name made lowercase.
    policyentered = models.DateTimeField(db_column='PolicyEntered', blank=True, null=True)  # Field name made lowercase.
    policyenteredby = models.IntegerField(db_column='PolicyEnteredBy', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.
    year = models.CharField(db_column='Year', max_length=50,  null=True)  # Field name made lowercase.
    paymodeid = models.IntegerField(db_column='PayModeID', blank=True, null=True)  # Field name made lowercase.
    policyapprovedby = models.IntegerField(db_column='PolicyApprovedBy', blank=True, null=True)  # Field name made lowercase.
    totalfees = models.DecimalField(db_column='TotalFees', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    cancelstatus = models.CharField(db_column='CancelStatus', max_length=20,  null=True)  # Field name made lowercase.
    canceldate = models.DateTimeField(db_column='CancelDate', blank=True, null=True)  # Field name made lowercase.
    isexportedtorta = models.BooleanField(db_column='IsExportedToRTA', blank=True, null=True)  # Field name made lowercase.
    isexportedtoinsco = models.BooleanField(db_column='IsExportedToInsCo', blank=True, null=True)  # Field name made lowercase.
    vehicledetailid = models.IntegerField(db_column='VehicleDetailID', blank=True, null=True)  # Field name made lowercase.
    agentcommssion = models.DecimalField(db_column='AgentCommssion', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    brokercommission = models.DecimalField(db_column='BrokerCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    policytypeid = models.IntegerField(db_column='PolicyTypeID', blank=True, null=True)  # Field name made lowercase.
    customerid = models.IntegerField(db_column='CustomerID', blank=True, null=True)  # Field name made lowercase.
    endorsereasonid = models.IntegerField(db_column='EndorseReasonID', blank=True, null=True)  # Field name made lowercase.
    noncommfees = models.DecimalField(db_column='NonCommFees', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    isendorsement = models.BooleanField(db_column='IsEndorsement', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='IsApproved', blank=True, null=True)  # Field name made lowercase.
    receiptprinteddate = models.DateTimeField(db_column='ReceiptPrintedDate', blank=True, null=True)  # Field name made lowercase.
    policyprinteddate = models.DateTimeField(db_column='PolicyPrintedDate', blank=True, null=True)  # Field name made lowercase.
    approveddatetime = models.DateTimeField(db_column='ApprovedDateTime', blank=True, null=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID', blank=True, null=True)  # Field name made lowercase.
    branchid = models.IntegerField(db_column='BranchID', blank=True, null=True)  # Field name made lowercase.
    smcommission = models.DecimalField(db_column='SMCommission', max_digits=10, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    commssion = models.DecimalField(db_column='Commssion', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    userapprovedid = models.IntegerField(db_column='UserApprovedID', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=400,  null=True)  # Field name made lowercase.
    customerauditid = models.ForeignKey(Customeraudit, models.DO_NOTHING, db_column='CustomerAuditID', blank=True, null=True)  # Field name made lowercase.
    vehiclemasterauditid = models.ForeignKey('Vehiclemasteraudit', models.DO_NOTHING, db_column='VehicleMasterAuditID', blank=True, null=True)  # Field name made lowercase.
    updatedby = models.IntegerField(db_column='updatedBy', blank=True, null=True)  # Field name made lowercase.
    updatedate = models.DateTimeField(db_column='updateDate', blank=True, null=True)  # Field name made lowercase.
    deletedby = models.IntegerField(db_column='deletedBy', blank=True, null=True)  # Field name made lowercase.
    deleteddate = models.DateTimeField(db_column='deletedDate', blank=True, null=True)  # Field name made lowercase.
    dltremarks = models.CharField(db_column='DltRemarks', max_length=400,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'MotorPolicyHistory'


class Nationality(models.Model):
    nationalityid = models.AutoField(db_column='NationalityID', primary_key=True)  # Field name made lowercase.
    nationalityeng = models.CharField(db_column='NationalityEng', max_length=25, blank=True, null=True)  # Field name made lowercase.
    nationalityarab = models.CharField(db_column='NationalityArab', max_length=30,  null=True)  # Field name made lowercase.
    nationalityenteredby = models.IntegerField(db_column='NationalityEnteredBy')  # Field name made lowercase.
    nationalityentereddate = models.DateTimeField(db_column='NationalityEnteredDate')  # Field name made lowercase.
    nationalityvehtype = models.CharField(db_column='NationalityVehType', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Nationality'


class Paymode(models.Model):
    payid = models.AutoField(db_column='PayID', primary_key=True)  # Field name made lowercase.
    motorpolicyid = models.IntegerField(db_column='MotorPolicyID',  blank=True, null=True)  # Field name made lowercase.
    ccauthcode = models.CharField(db_column='CCAuthCode', max_length=15,  null=True)  # Field name made lowercase.
    ccname = models.CharField(db_column='CCName', max_length=50,  null=True)  # Field name made lowercase.
    ccno = models.CharField(db_column='CCNo', max_length=25,  null=True)  # Field name made lowercase.
    ccexpirydate = models.DateTimeField(db_column='CCExpiryDate', blank=True, null=True)  # Field name made lowercase.
    cctype = models.CharField(db_column='CCType', max_length=50,  null=True)  # Field name made lowercase.
    cqdate = models.DateTimeField(db_column='CQDate', blank=True, null=True)  # Field name made lowercase.
    cqno = models.CharField(db_column='CQNo', max_length=25,  null=True)  # Field name made lowercase.
    cqbank = models.CharField(db_column='CQBank', max_length=50,  null=True)  # Field name made lowercase.
    paymentmodeid = models.IntegerField(db_column='PaymentModeID')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'PayMode'


class Platecity(models.Model):
    platecityid = models.AutoField(db_column='PlateCityID', primary_key=True)  # Field name made lowercase.
    platecitynameeng = models.CharField(db_column='PlateCityNameEng', max_length=50,  null=True)  # Field name made lowercase.
    platecitynamearab = models.CharField(db_column='PlateCityNameArab', max_length=50,  null=True)  # Field name made lowercase.
    enteredby = models.IntegerField(db_column='EnteredBy', blank=True, null=True)  # Field name made lowercase.
    entereddate = models.DateTimeField(db_column='EnteredDate', blank=True, null=True)  # Field name made lowercase.
    deletedate = models.DateTimeField(db_column='DeleteDate', blank=True, null=True)  # Field name made lowercase.
    deletedby = models.IntegerField(db_column='DeletedBy', blank=True, null=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment',  null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='IsDeleted', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'PlateCity'

class Renewfollow(models.Model):
    renewfollowid = models.AutoField(db_column='RenewFollowID', primary_key=True)  # Field name made lowercase.
    motorpolicyid = models.ForeignKey('Motorpolicy', models.DO_NOTHING, db_column='MotorPolicyID')  # Field name made lowercase.
    managercomments = models.CharField(db_column='ManagerComments', max_length=150,  null=True)  # Field name made lowercase.
    laststatus = models.CharField(db_column='LastStatus', max_length=50,  null=True)  # Field name made lowercase.
    datelastupdated = models.DateTimeField(db_column='DateLastUpdated', blank=True, null=True)  # Field name made lowercase.
    renewalenteredby = models.IntegerField(db_column='RenewalEnteredBy', blank=True, null=True)  # Field name made lowercase.
    dateentered = models.DateTimeField(db_column='DateEntered', blank=True, null=True)  # Field name made lowercase.
    renewalsalesmanid = models.IntegerField(db_column='RenewalSalesmanID')  # Field name made lowercase.
    renewalmotorpolicyid = models.IntegerField(db_column='RenewalMotorPolicyID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'RenewFollow'


class Renewfollowdetails(models.Model):
    renewfollowdetailsid = models.AutoField(db_column='RenewFollowDetailsID', primary_key=True)  # Field name made lowercase.
    renewfollowid = models.ForeignKey(Renewfollow, models.DO_NOTHING, db_column='RenewFollowID')  # Field name made lowercase.
    datetimestamp = models.DateTimeField(db_column='DateTimeStamp')  # Field name made lowercase.
    comments = models.CharField(db_column='Comments', max_length=100, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    nextfollowupdate = models.DateTimeField(db_column='NextFollowupDate')  # Field name made lowercase.
    smstext = models.CharField(db_column='SMSText', max_length=150, blank=True, null=True)  # Field name made lowercase.
    mobilenumber = models.CharField(db_column='MobileNumber', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isfollowedup = models.CharField(db_column='IsFollowedUp', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'RenewFollowDetails'


class Smssent(models.Model):
    smssentid = models.AutoField(db_column='SMSSentID', primary_key=True)  # Field name made lowercase.
    smssetupid = models.ForeignKey('Smssetup', models.DO_NOTHING, db_column='SMSSetupID')  # Field name made lowercase.
    contactid = models.IntegerField(db_column='ContactID', blank=True, null=True)  # Field name made lowercase.
    telephoneno = models.CharField(db_column='TelephoneNo', max_length=25,  null=True)  # Field name made lowercase.
    smssentsender = models.CharField(db_column='SMSSentSender', max_length=20, blank=True, null=True)  # Field name made lowercase.
    smssentresponse = models.CharField(db_column='SMSSentResponse', max_length=300, blank=True, null=True)  # Field name made lowercase.
    smssentdate = models.DateTimeField(db_column='SMSSentDate', blank=True, null=True)  # Field name made lowercase.
    smssententeredby = models.IntegerField(db_column='SMSSentEnteredBy')  # Field name made lowercase.
    smssententereddate = models.DateTimeField(db_column='SMSSentEnteredDate')  # Field name made lowercase.
    smssentstatus = models.CharField(db_column='SMSSentStatus', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'SMSSent'


class Smssetup(models.Model):
    smssetupid = models.AutoField(db_column='SMSSetupID', primary_key=True)  # Field name made lowercase.
    message = models.TextField(db_column='Message',  null=True)  # Field name made lowercase.
    daysbeforeexpiry = models.IntegerField(db_column='DaysBeforeExpiry', blank=True, null=True)  # Field name made lowercase.
    smsstatus = models.CharField(db_column='SMSStatus', max_length=20, blank=True, null=True)  # Field name made lowercase.
    smssender = models.CharField(db_column='SMSSender', max_length=20,  null=True)  # Field name made lowercase.
    smssetupenteredby = models.IntegerField(db_column='SMSSetupEnteredBy')  # Field name made lowercase.
    smssetupentereddate = models.DateTimeField(db_column='SMSSetupEnteredDate')  # Field name made lowercase.
    smstypeid = models.IntegerField(db_column='SMSTypeID')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'SMSSetup'


class Smsvariables(models.Model):
    smsvariablesid = models.AutoField(db_column='SMSVariablesID', primary_key=True)  # Field name made lowercase.
    escapechar = models.CharField(db_column='EscapeChar', max_length=10,  null=True)  # Field name made lowercase.
    escapefield = models.CharField(db_column='EscapeField', max_length=50,  null=True)  # Field name made lowercase.
    escapetable = models.CharField(db_column='EscapeTable', max_length=50,  null=True)  # Field name made lowercase.
    escapepk = models.CharField(db_column='EscapePK', max_length=50,  null=True)  # Field name made lowercase.
    escapedesc = models.CharField(db_column='EscapeDesc', max_length=50,  null=True)  # Field name made lowercase.
    smsvarenteredby = models.IntegerField(db_column='SMSVarEnteredBy')  # Field name made lowercase.
    smsvarentereddate = models.DateTimeField(db_column='SMSVarEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'SMSVariables'


class Salescommision(models.Model):
    salescommisionid = models.AutoField(db_column='SalesCommisionID', primary_key=True)  # Field name made lowercase.
    branchid = models.IntegerField(db_column='BranchID')  # Field name made lowercase.
    firstpolicycomm = models.IntegerField(db_column='FirstPolicyComm')  # Field name made lowercase.
    secondpolicycomm = models.IntegerField(db_column='SecondPolicyComm')  # Field name made lowercase.
    thirdpolicycomm = models.IntegerField(db_column='ThirdPolicyComm')  # Field name made lowercase.
    fourthpolicycomm = models.IntegerField(db_column='FourthPolicyComm')  # Field name made lowercase.
    fifthpolicycomm = models.IntegerField(db_column='FifthPolicyComm')  # Field name made lowercase.
    sixthpolicycomm = models.IntegerField(db_column='SixthPolicyComm')  # Field name made lowercase.
    ninthpolicycomm = models.IntegerField(db_column='NinthPolicyComm')  # Field name made lowercase.
    tenthpolicycomm = models.IntegerField(db_column='TenthPolicyComm')  # Field name made lowercase.
    elevenandmorepolcomm = models.IntegerField(db_column='ElevenAndMorePolComm')  # Field name made lowercase.
    seventhpolicycomm = models.IntegerField(db_column='SeventhPolicyComm')  # Field name made lowercase.
    eighthpolicycomm = models.IntegerField(db_column='EighthPolicyComm')  # Field name made lowercase.
    salespolicytypeid = models.IntegerField(db_column='SalesPolicyTypeID')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'SalesCommision'


class Salesman(models.Model):
    salesmanid = models.AutoField(db_column='SalesmanID', primary_key=True)  # Field name made lowercase.
    salesmaneng = models.CharField(db_column='SalesManEng', max_length=100, blank=True, null=True)  # Field name made lowercase.
    salesmanarab = models.CharField(db_column='SalesManArab', max_length=100, blank=True, null=True)  # Field name made lowercase.
    salesmanmobile = models.CharField(db_column='SalesManMobile', max_length=20, blank=True, null=True)  # Field name made lowercase.
    salesmantel = models.CharField(db_column='SalesManTel', max_length=20, blank=True, null=True)  # Field name made lowercase.
    salesmancity = models.CharField(db_column='SalesManCity', max_length=20, blank=True, null=True)  # Field name made lowercase.
    nationalityid = models.ForeignKey(Nationality, models.DO_NOTHING, db_column='NationalityID')  # Field name made lowercase.
    salesmanemail = models.CharField(db_column='SalesManEMail', max_length=50, blank=True, null=True)  # Field name made lowercase.
    salesmandob = models.DateTimeField(db_column='SalesManDOB', blank=True, null=True)  # Field name made lowercase.
    salesmansex = models.CharField(db_column='SalesManSex', max_length=10, blank=True, null=True)  # Field name made lowercase.
    salesmanpostal = models.CharField(db_column='SalesManPostal', max_length=15, blank=True, null=True)  # Field name made lowercase.
    salesmanpassportno = models.CharField(db_column='SalesManPassportNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    salesmanpassportissue = models.DateTimeField(db_column='SalesManPassportIssue', blank=True, null=True)  # Field name made lowercase.
    salesmanpassportexpiry = models.DateTimeField(db_column='SalesManPassportExpiry', blank=True, null=True)  # Field name made lowercase.
    salesmanenteredby = models.IntegerField(db_column='SalesManEnteredBy')  # Field name made lowercase.
    salesmanentereddate = models.DateTimeField(db_column='SalesManEnteredDate')  # Field name made lowercase.
    salesmanvisano = models.CharField(db_column='SalesManVisaNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    salesmanvisaexpiry = models.DateTimeField(db_column='SalesManVisaExpiry', blank=True, null=True)  # Field name made lowercase.
    salemanaddarab3 = models.CharField(db_column='SaleManAddArab3', max_length=100,  null=True)  # Field name made lowercase.
    salemanaddarab2 = models.CharField(db_column='SaleManAddArab2', max_length=100,  null=True)  # Field name made lowercase.
    salemanaddarab1 = models.CharField(db_column='SaleManAddArab1', max_length=100,  null=True)  # Field name made lowercase.
    salemanaddeng3 = models.CharField(db_column='SaleManAddEng3', max_length=100,  null=True)  # Field name made lowercase.
    salemanaddeng2 = models.CharField(db_column='SaleManAddEng2', max_length=100,  null=True)  # Field name made lowercase.
    salemanaddeng1 = models.CharField(db_column='SaleManAddEng1', max_length=100,  null=True)  # Field name made lowercase.
    isallowrenew = models.BooleanField(db_column='ISAllowRenew')  # Field name made lowercase.
    accountaddressbookid = models.IntegerField(db_column='AccountAddressBookID', blank=True, null=True)  # Field name made lowercase.
    departmentid = models.IntegerField(db_column='DepartmentID', blank=True, null=True)  # Field name made lowercase.
    designationid = models.IntegerField(db_column='DesignationID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'SalesMan'




class Subscription(models.Model):
    subscriptionid = models.AutoField(db_column='SubscriptionID', primary_key=True)  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    brokerid = models.IntegerField(db_column='BrokerID')  # Field name made lowercase.
    branchid = models.IntegerField(db_column='BranchID')  # Field name made lowercase.
    subenteredby = models.IntegerField(db_column='SubEnteredBy')  # Field name made lowercase.
    subentereddate = models.DateTimeField(db_column='SubEnteredDate')  # Field name made lowercase.
    brokercommpercent = models.DecimalField(db_column='BrokerCommPercent', max_digits=10, decimal_places=4)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Subscription'

class Trtasendinfo(models.Model):
    idsendinfo = models.AutoField(db_column='IDSendInfo', primary_key=True)  # Field name made lowercase.
    spolicynumber = models.CharField(db_column='sPolicyNumber', max_length=50,  null=True)  # Field name made lowercase.
    spolicydate = models.CharField(db_column='sPolicyDate', max_length=50,  null=True)  # Field name made lowercase.
    spolicyexpirydate = models.CharField(db_column='sPolicyExpiryDate', max_length=50,  null=True)  # Field name made lowercase.
    sinsurancecompno = models.CharField(db_column='sInsuranceCompNo', max_length=20,  null=True)  # Field name made lowercase.
    schasisnumber = models.CharField(db_column='sChasisNumber', max_length=50,  null=True)  # Field name made lowercase.
    smodelyear = models.CharField(db_column='sModelYear', max_length=10,  null=True)  # Field name made lowercase.
    senginenumber = models.CharField(db_column='sEngineNumber', max_length=50,  null=True)  # Field name made lowercase.
    scylinders = models.CharField(db_column='sCylinders', max_length=50,  null=True)  # Field name made lowercase.
    snumberofdoors = models.CharField(db_column='sNumberofDoors', max_length=10,  null=True)  # Field name made lowercase.
    snumberofseats = models.CharField(db_column='sNumberofSeats', max_length=10,  null=True)  # Field name made lowercase.
    splatenumber = models.CharField(db_column='sPlateNumber', max_length=20,  null=True)  # Field name made lowercase.
    splatecategory = models.CharField(db_column='sPlateCategory', max_length=20,  null=True)  # Field name made lowercase.
    splatecode = models.CharField(db_column='sPlateCode', max_length=10,  null=True)  # Field name made lowercase.
    binfostatus = models.BooleanField(db_column='bInfoStatus', blank=True, null=True)  # Field name made lowercase.
    dtdateenter = models.DateTimeField(db_column='dtDateEnter', blank=True, null=True)  # Field name made lowercase.
    iduser = models.IntegerField(db_column='IDUser', blank=True, null=True)  # Field name made lowercase.
    smessage = models.CharField(db_column='sMessage', max_length=150,  null=True)  # Field name made lowercase.
    semirates = models.CharField(db_column='sEmirates', max_length=50,  null=True)  # Field name made lowercase.
    scertificateid = models.CharField(db_column='sCertificateID', max_length=50,  null=True)  # Field name made lowercase.
    sinscoid = models.CharField(db_column='sInscoID', max_length=50,  null=True)  # Field name made lowercase.
    bresend = models.BooleanField(db_column='bResend', blank=True, null=True)  # Field name made lowercase.
    spolicytype = models.CharField(db_column='sPolicyType', max_length=50,  null=True)  # Field name made lowercase.
    motorpolicyid = models.IntegerField(db_column='MotorPolicyID', blank=True, null=True)  # Field name made lowercase.
    bcancelstatus = models.BooleanField(db_column='bCancelStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'TRTASendInfo'


class Thirdpartyrate(models.Model):
    thirdpartyrateid = models.AutoField(db_column='ThirdPartyRateID', primary_key=True)  # Field name made lowercase.
    bodytypeid = models.ForeignKey(Bodytype, models.DO_NOTHING, db_column='BodyTypeID', blank=True, null=True)  # Field name made lowercase.
    useofvehicleid = models.ForeignKey('Useofvehicle', models.DO_NOTHING, db_column='UseOfVehicleID', blank=True, null=True)  # Field name made lowercase.
    tpentereddate = models.DateTimeField(db_column='TPEnteredDate')  # Field name made lowercase.
    empid = models.IntegerField(db_column='EmpID')  # Field name made lowercase.
    insurancecompanyid = models.ForeignKey(Insurancecompany, models.DO_NOTHING, db_column='InsuranceCompanyID', blank=True, null=True)  # Field name made lowercase.
    tppremium = models.DecimalField(db_column='TPPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    tpcommision = models.DecimalField(db_column='TPCommision', max_digits=10, decimal_places=4)  # Field name made lowercase.
    tpratedriver = models.DecimalField(db_column='TPRateDriver', max_digits=19, decimal_places=4)  # Field name made lowercase.
    tpratepassenger = models.DecimalField(db_column='TPRatePassenger', max_digits=19, decimal_places=4)  # Field name made lowercase.
    tpageownerfrom = models.IntegerField(db_column='TPAgeOwnerFrom', blank=True, null=True)  # Field name made lowercase.
    tpageownerto = models.IntegerField(db_column='TPAgeOwnerTo', blank=True, null=True)  # Field name made lowercase.
    tpagelicensefrom = models.IntegerField(db_column='TPAgeLicenseFrom', blank=True, null=True)  # Field name made lowercase.
    tpagelicenseto = models.IntegerField(db_column='TPAgeLicenseTo', blank=True, null=True)  # Field name made lowercase.
    tpstatus = models.CharField(db_column='TPStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.
    tpdoors = models.IntegerField(db_column='TPDoors')  # Field name made lowercase.
    tptons = models.IntegerField(db_column='TPTons')  # Field name made lowercase.
    tpcylinders = models.IntegerField(db_column='TPCylinders')  # Field name made lowercase.
    tpapprovedby = models.IntegerField(db_column='TPApprovedBy')  # Field name made lowercase.
    tpenteredby = models.IntegerField(db_column='TPEnteredBy')  # Field name made lowercase.
    areaid = models.ForeignKey(Area, models.DO_NOTHING, db_column='AreaID', blank=True, null=True)  # Field name made lowercase.
    surplusareatppremium = models.DecimalField(db_column='SurplusAreaTPPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusareatpexcess = models.DecimalField(db_column='SurplusAreaTPExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusareatpminimum = models.DecimalField(db_column='SurplusAreaTPMinimum', max_digits=19, decimal_places=4)  # Field name made lowercase.
    nationalityid = models.ForeignKey(Nationality, models.DO_NOTHING, db_column='NationalityID', blank=True, null=True)  # Field name made lowercase.
    surplusnattppremium = models.DecimalField(db_column='SurplusNatTPPremium', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusnattpexcess = models.DecimalField(db_column='SurplusNatTPExcess', max_digits=19, decimal_places=4)  # Field name made lowercase.
    surplusnattpminimum = models.DecimalField(db_column='SurplusNatTPMinimum', max_digits=19, decimal_places=4)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'ThirdPartyRate'


class Useofvehicle(models.Model):
    useofvehicleid = models.AutoField(db_column='UseOfVehicleID', primary_key=True)  # Field name made lowercase.
    useofvehicleeng = models.CharField(db_column='UseOfVehicleEng', max_length=20, blank=True, null=True)  # Field name made lowercase.
    useofvehiclearab = models.CharField(db_column='UseOfVehicleArab', max_length=20, blank=True, null=True)  # Field name made lowercase.
    useenteredby = models.IntegerField(db_column='UseEnteredBy')  # Field name made lowercase.
    useentereddate = models.DateTimeField(db_column='UseEnteredDate')  # Field name made lowercase.
    usevehtypeid = models.CharField(db_column='UseVehTypeID', max_length=20,  null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'UseOfVehicle'

class User():
    pass

class Userwithic(models.Model):
    userwithicid = models.AutoField(db_column='UserWithICID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey(User, models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    insurancecompanyid = models.IntegerField(db_column='InsuranceCompanyID')  # Field name made lowercase.
    usericenteredby = models.IntegerField(db_column='UserICEnteredBy')  # Field name made lowercase.
    usericentereddate = models.DateTimeField(db_column='UserICEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'UserWithIC'


class Vehicledetail(models.Model):
    vehicledetailid = models.AutoField(db_column='VehicleDetailID', primary_key=True)  # Field name made lowercase.
    enginenumber = models.CharField(db_column='EngineNumber', max_length=30, blank=True, null=True)  # Field name made lowercase.
    chassisnumber = models.CharField(db_column='ChassisNumber', max_length=30, blank=True, null=True)  # Field name made lowercase.
    platecategory = models.CharField(db_column='PlateCategory', max_length=30, blank=True, null=True)  # Field name made lowercase.
    platenumber = models.CharField(db_column='PlateNumber', max_length=30, blank=True, null=True)  # Field name made lowercase.
    platecode = models.CharField(db_column='PlateCode', max_length=30,  null=True)  # Field name made lowercase.
    capacity = models.CharField(db_column='Capacity', max_length=30, blank=True, null=True)  # Field name made lowercase.
    enginecapacity = models.CharField(db_column='EngineCapacity', max_length=30, blank=True, null=True)  # Field name made lowercase.
    axles = models.CharField(db_column='Axles', max_length=20,  null=True)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    carryweight = models.DecimalField(db_column='CarryWeight', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tons = models.IntegerField(db_column='Tons', blank=True, null=True)  # Field name made lowercase.
    doors = models.IntegerField(db_column='Doors')  # Field name made lowercase.
    cylinders = models.IntegerField(db_column='Cylinders')  # Field name made lowercase.
    fueltype = models.CharField(db_column='FuelType', max_length=10,  null=True)  # Field name made lowercase.
    modelyear = models.IntegerField(db_column='ModelYear', blank=True, null=True)  # Field name made lowercase.
    mortgagecompany = models.CharField(db_column='MortgageCompany', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mortgagedate = models.DateTimeField(db_column='MortgageDate', blank=True, null=True)  # Field name made lowercase.
    mortgageecomparab = models.CharField(db_column='MortgageeCompArab', max_length=100,  null=True)  # Field name made lowercase.
    registrationexpiredate = models.DateTimeField(db_column='RegistrationExpireDate', blank=True, null=True)  # Field name made lowercase.
    registrationdate = models.DateTimeField(db_column='RegistrationDate', blank=True, null=True)  # Field name made lowercase.
    responsecode = models.CharField(db_column='ResponseCode', max_length=50,  null=True)  # Field name made lowercase.
    responsedesc = models.CharField(db_column='ResponseDesc', max_length=50,  null=True)  # Field name made lowercase.
    responselevel = models.CharField(db_column='ResponseLevel', max_length=50,  null=True)  # Field name made lowercase.
    trafficfileno = models.CharField(db_column='TrafficFileNo', max_length=50,  null=True)  # Field name made lowercase.
    modelid = models.ForeignKey(Model, models.DO_NOTHING, db_column='ModelID')  # Field name made lowercase.
    bodytypeid = models.ForeignKey(Bodytype, models.DO_NOTHING, db_column='BodyTypeID')  # Field name made lowercase.
    colorid = models.ForeignKey(Color, models.DO_NOTHING, db_column='ColorID')  # Field name made lowercase.
    useofvehicleid = models.ForeignKey(Useofvehicle, models.DO_NOTHING, db_column='UseOfVehicleID')  # Field name made lowercase.
    vehmakeid = models.IntegerField(db_column='VehMakeID')  # Field name made lowercase.
    vehmotorpolicyid = models.IntegerField(db_column='VehMotorPolicyID', blank=True, null=True)  # Field name made lowercase.
    platecityid = models.IntegerField(db_column='PlateCityID', blank=True, null=True)  # Field name made lowercase.
    bankid = models.IntegerField(db_column='BankID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'VehicleDetail'


class Vehiclemaster(models.Model):
    vehiclemasterid = models.AutoField(db_column='VehicleMasterId', primary_key=True)  # Field name made lowercase.
    makeid = models.IntegerField(db_column='MakeId')  # Field name made lowercase.
    modelid = models.IntegerField(db_column='ModelId')  # Field name made lowercase.
    bodytypeid = models.IntegerField(db_column='BodyTypeId')  # Field name made lowercase.
    vehiclemasterenteredby = models.IntegerField(db_column='VehicleMasterEnteredBy')  # Field name made lowercase.
    vehiclemasterentereddate = models.DateTimeField(db_column='VehicleMasterEnteredDate')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'VehicleMaster'


class Vehiclemasteraudit(models.Model):
    vehiclemasterauditid = models.AutoField(db_column='VehicleMasterAuditID', primary_key=True)  # Field name made lowercase.
    vehicledetailid = models.IntegerField(db_column='VehicleDetailID')  # Field name made lowercase.
    enginenumber = models.CharField(db_column='EngineNumber', max_length=30,  null=True)  # Field name made lowercase.
    chassisnumber = models.CharField(db_column='ChassisNumber', max_length=30,  null=True)  # Field name made lowercase.
    platecategory = models.CharField(db_column='PlateCategory', max_length=15,  null=True)  # Field name made lowercase.
    platenumber = models.CharField(db_column='PlateNumber', max_length=15,  null=True)  # Field name made lowercase.
    platecode = models.CharField(db_column='PlateCode', max_length=15,  null=True)  # Field name made lowercase.
    capacity = models.CharField(db_column='Capacity', max_length=5,  null=True)  # Field name made lowercase.
    enginecapacity = models.CharField(db_column='EngineCapacity', max_length=20,  null=True)  # Field name made lowercase.
    axles = models.CharField(db_column='Axles', max_length=20,  null=True)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    carryweight = models.DecimalField(db_column='CarryWeight', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    tons = models.IntegerField(db_column='Tons', blank=True, null=True)  # Field name made lowercase.
    doors = models.IntegerField(db_column='Doors')  # Field name made lowercase.
    cylinders = models.IntegerField(db_column='Cylinders')  # Field name made lowercase.
    fueltype = models.CharField(db_column='FuelType', max_length=10,  null=True)  # Field name made lowercase.
    modelyear = models.IntegerField(db_column='ModelYear', blank=True, null=True)  # Field name made lowercase.
    mortgagecompany = models.CharField(db_column='MortgageCompany', max_length=50,  null=True)  # Field name made lowercase.
    mortgagedate = models.DateTimeField(db_column='MortgageDate', blank=True, null=True)  # Field name made lowercase.
    mortgageecomparab = models.CharField(db_column='MortgageeCompArab', max_length=50,  null=True)  # Field name made lowercase.
    registrationexpiredate = models.DateTimeField(db_column='RegistrationExpireDate', blank=True, null=True)  # Field name made lowercase.
    registrationdate = models.DateTimeField(db_column='RegistrationDate', blank=True, null=True)  # Field name made lowercase.
    responsecode = models.CharField(db_column='ResponseCode', max_length=50,  null=True)  # Field name made lowercase.
    responsedesc = models.CharField(db_column='ResponseDesc', max_length=50,  null=True)  # Field name made lowercase.
    responselevel = models.CharField(db_column='ResponseLevel', max_length=50,  null=True)  # Field name made lowercase.
    trafficfileno = models.CharField(db_column='TrafficFileNo', max_length=50,  null=True)  # Field name made lowercase.
    modelid = models.IntegerField(db_column='ModelID')  # Field name made lowercase.
    bodytypeid = models.IntegerField(db_column='BodyTypeID')  # Field name made lowercase.
    colorid = models.IntegerField(db_column='ColorID')  # Field name made lowercase.
    useofvehicleid = models.IntegerField(db_column='UseOfVehicleID')  # Field name made lowercase.
    vehmakeid = models.IntegerField(db_column='VehMakeID')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'VehicleMasterAudit'

class Vehiclemasterhistory(models.Model):
    vehiclemasterhistoryid = models.AutoField(db_column='VehicleMasterHistoryID', primary_key=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'VehicleMasterHistory'

class Vehicletype(models.Model):
    vehicletypeid = models.AutoField(db_column='VehicleTypeID', primary_key=True )  # Field name made lowercase.
    vehicletypename = models.CharField(db_column='VehicleTypeName', max_length=15, blank=True, null=True)  # Field name made lowercase.
    vehicletypeenteredby = models.IntegerField(db_column='VehicleTypeEnteredBy', blank=True, null=True )  # Field name made lowercase.
    vehicletypeentereddate = models.DateTimeField(db_column='VehicleTypeEnteredDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'VehicleType'

class T15Icp10(models.Model):
    policy_number = models.CharField(max_length=255, blank=True, null=True)
    policy_type = models.CharField(max_length=40, blank=True, null=True)
    insurance_premium = models.FloatField(blank=True, null=True)
    gross_premium = models.FloatField(blank=True, null=True)
    original_invoice_amount = models.FloatField(blank=True, null=True)
    invoice_amount = models.FloatField(blank=True, null=True)
    mode_of_payment = models.FloatField(blank=True, null=True)
    cancelled = models.CharField(max_length=10, blank=True, null=True)
    deleted = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'T15ICP10'
        verbose_name = 'Ins Co Payment History'
"""
