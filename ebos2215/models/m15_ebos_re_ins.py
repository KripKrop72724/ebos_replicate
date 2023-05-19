from django.db import models

"""
class T33Cln10(models.Model):
    idcln10 = models.BigAutoField(db_column='IDCLN10', primary_key=True)
    idslp10 = models.BigIntegerField(db_column='IDSLP10', blank=True, null=True)
    idcvn10 = models.ForeignKey('T33Cvn10', models.DO_NOTHING, db_column='IDCVN10', blank=True, null=True)
    sprg = models.CharField(db_column='sPrg', max_length=10, blank=True, null=True)
    sdoctype = models.CharField(db_column='sDocType', max_length=10, blank=True, null=True)
    ndocno = models.BigIntegerField(db_column='nDocNo', blank=True, null=True)
    stype = models.CharField(db_column='sType', max_length=100, blank=True, null=True)
    stitle = models.CharField(db_column='sTitle', max_length=150, blank=True, null=True)
    dtdoc = models.DateTimeField(db_column='dtDoc', blank=True, null=True)
    idcur10 = models.ForeignKey(T01Cur10, models.DO_NOTHING, db_column='IDCUR10', blank=True, null=True)
    idinsured = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDInsured', blank=True, null=True)
    idreinsurer = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDReinsurer', blank=True, null=True)
    idcedent = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDCedent', blank=True, null=True)
    idloc10 = models.ForeignKey('T33Loc10', models.DO_NOTHING, db_column='IDLOC10', blank=True, null=True)
    fpcrt = models.FloatField(db_column='fPCRt', blank=True, null=True)
    fpmrt = models.FloatField(db_column='fPMRt', blank=True, null=True)
    srt = models.CharField(db_column='sRt', max_length=50, blank=True, null=True)
    fpccomm = models.FloatField(db_column='fPCComm', blank=True, null=True)
    scommission = models.CharField(db_column='sCommission', max_length=50, blank=True, null=True)
    fpcfac = models.FloatField(db_column='fPCFac', blank=True, null=True)
    sfac = models.CharField(db_column='sFac', max_length=50, blank=True, null=True)
    fpcnoclm = models.FloatField(db_column='fPCNoClm', blank=True, null=True)
    fbclsnoclm = models.FloatField(db_column='fBCLSNoClm', blank=True, null=True)
    ftclsnoclm = models.FloatField(db_column='fTCLSNoClm', blank=True, null=True)
    flsnoclm = models.FloatField(db_column='fLSNoClm', blank=True, null=True)
    snoclm = models.CharField(db_column='sNoClm', max_length=50, blank=True, null=True)
    ftcprem = models.FloatField(db_column='fTCPrem', blank=True, null=True)
    fbcprem = models.FloatField(db_column='fBCPrem', blank=True, null=True)
    fcurrrt = models.FloatField(db_column='fCurrRt', blank=True, null=True)
    sprem = models.CharField(db_column='sPrem', max_length=50, blank=True, null=True)
    fret = models.FloatField(db_column='fRet', blank=True, null=True)
    sret = models.CharField(db_column='sRet', max_length=50, blank=True, null=True)
    fpcrorder = models.FloatField(db_column='fPCROrder', blank=True, null=True)
    srorder = models.CharField(db_column='sROrder', max_length=50, blank=True, null=True)
    slaw = models.CharField(db_column='sLaw', max_length=200, blank=True, null=True)
    scover = models.CharField(db_column='sCover', max_length=1250, blank=True, null=True)
    sprd = models.CharField(db_column='sPrd', max_length=100, blank=True, null=True)
    dtfrom = models.DateTimeField(db_column='dtFrom', blank=True, null=True)
    dtto = models.DateTimeField(db_column='dtTo', blank=True, null=True)
    sinterest = models.CharField(db_column='sInterest', max_length=750, blank=True, null=True)
    sterms = models.CharField(db_column='sTerms', max_length=2000, blank=True, null=True)
    sded = models.CharField(db_column='sDed', max_length=300, blank=True, null=True)
    srmk = models.CharField(db_column='sRmk', max_length=250, blank=True, null=True)
    fsummd = models.FloatField(db_column='fSumMD', blank=True, null=True)
    fsumlop = models.FloatField(db_column='fSumLOP', blank=True, null=True)
    fsumtot = models.FloatField(db_column='fSumTOT', blank=True, null=True)
    sinfo = models.CharField(db_column='sInfo', max_length=500, blank=True, null=True)
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)
    dtde = models.DateTimeField(db_column='dtDE', blank=True, null=True)
    iduserinv = models.BigIntegerField(db_column='IDUserInv', blank=True, null=True)
    dtinv = models.DateTimeField(db_column='dtInv', blank=True, null=True)
    ndel = models.IntegerField(db_column='nDel', blank=True, null=True)
    iduserdel = models.BigIntegerField(db_column='IDUserDel', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    sform = models.CharField(db_column='sForm', max_length=100, blank=True, null=True)
    svoyage = models.CharField(db_column='sVoyage', max_length=100, blank=True, null=True)
    sconvey = models.CharField(db_column='sConvey', max_length=100, blank=True, null=True)
    spack = models.CharField(db_column='sPack', max_length=100, blank=True, null=True)
    slossrec = models.CharField(db_column='sLossRec', max_length=100, blank=True, null=True)
    nstatus = models.SmallIntegerField(db_column='nStatus', blank=True, null=True)
    ssuminsured = models.CharField(db_column='sSumInsured', max_length=100, blank=True, null=True)
    sdocno = models.CharField(db_column='sDocNo', max_length=25, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33CLN10'


class T33Cln11(models.Model):
    idcln11 = models.BigAutoField(db_column='IDCLN11', primary_key=True)
    idslp11 = models.ForeignKey('T33Slp11', models.DO_NOTHING, db_column='IDSLP11', blank=True, null=True)
    idcvn11 = models.ForeignKey('T33Cvn11', models.DO_NOTHING, db_column='IDCVN11', blank=True, null=True)
    idcln10 = models.ForeignKey(T33Cln10, models.DO_NOTHING, db_column='IDCLN10', blank=True, null=True)
    fbcshare = models.FloatField(db_column='fBCShare', blank=True, null=True)
    fcurrrt = models.FloatField(db_column='fCurrRt', blank=True, null=True)
    idinv10 = models.ForeignKey('T33Inv10', models.DO_NOTHING, db_column='IDINV10', blank=True, null=True)
    allpcfieldsfollow = models.FloatField(db_column='ALLPCFIELDSFOLLOW', blank=True, null=True)
    fcomm = models.FloatField(db_column='fComm', blank=True, null=True)
    ffac = models.FloatField(db_column='fFac', blank=True, null=True)
    fnoclm = models.FloatField(db_column='fNoClm', blank=True, null=True)
    fsuminsured = models.FloatField(db_column='fSumInsured', blank=True, null=True)
    fpcrt = models.FloatField(db_column='fPcRt', blank=True, null=True)
    fpmrt = models.FloatField(db_column='fPMRt', blank=True, null=True)
    ftcprem = models.FloatField(db_column='fTCPrem', blank=True, null=True)
    ftcshare = models.FloatField(db_column='fTCShare', blank=True, null=True)
    ftpcrt = models.FloatField(db_column='fTPcRt', blank=True, null=True)
    ftpmrt = models.FloatField(db_column='fTPMRt', blank=True, null=True)
    fduration = models.FloatField(db_column='fDuration', blank=True, null=True)
    fpremium = models.FloatField(db_column='fPremium', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33CLN11'


class T33Cvn10(models.Model):
    idcvn10 = models.BigAutoField(db_column='IDCVN10', primary_key=True)
    sprg = models.CharField(db_column='sPrg', max_length=10, blank=True, null=True)
    sdoctype = models.CharField(db_column='sDocType', max_length=10, blank=True, null=True)
    stype = models.CharField(db_column='sType', max_length=100, blank=True, null=True)
    stitle = models.CharField(db_column='sTitle', max_length=150, blank=True, null=True)
    ndocno = models.BigIntegerField(db_column='nDocNo', blank=True, null=True)
    sfileno = models.CharField(db_column='sFileNo', max_length=20, blank=True, null=True)
    dtdoc = models.DateTimeField(db_column='dtDoc', blank=True, null=True)
    idslp10 = models.BigIntegerField(db_column='IDSLP10', blank=True, null=True)
    idcedent = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDCedent', blank=True, null=True)
    scover = models.CharField(db_column='sCover', max_length=1250, blank=True, null=True)
    idinsured = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDInsured', blank=True, null=True)
    idcur10 = models.ForeignKey(T01Cur10, models.DO_NOTHING, db_column='IDCUR10', blank=True, null=True)
    idloc10 = models.ForeignKey('T33Loc10', models.DO_NOTHING, db_column='IDLOC10', blank=True, null=True)
    fpcrt = models.FloatField(db_column='fPCRt', blank=True, null=True)
    fpmrt = models.FloatField(db_column='fPMRt', blank=True, null=True)
    srt = models.CharField(db_column='sRt', max_length=50, blank=True, null=True)
    fpcfac = models.FloatField(db_column='fPCFac', blank=True, null=True)
    sfac = models.CharField(db_column='sFac', max_length=50, blank=True, null=True)
    fpcnoclm = models.FloatField(db_column='fPCNoClm', blank=True, null=True)
    ftclsnoclm = models.FloatField(db_column='fTCLSNoClm', blank=True, null=True)
    fbclsnoclm = models.FloatField(db_column='fBCLSNoClm', blank=True, null=True)
    snoclm = models.CharField(db_column='sNoClm', max_length=50, blank=True, null=True)
    fcurrrt = models.FloatField(db_column='fCurrRt', blank=True, null=True)
    ftcprem = models.FloatField(db_column='fTCPrem', blank=True, null=True)
    fbcprem = models.FloatField(db_column='fBCPrem', blank=True, null=True)
    sprem = models.CharField(db_column='sPrem', max_length=50, blank=True, null=True)
    fpcret = models.FloatField(db_column='fPCRet', blank=True, null=True)
    sret = models.CharField(db_column='sRet', max_length=50, blank=True, null=True)
    dtfrom = models.DateTimeField(db_column='dtFrom', blank=True, null=True)
    dtto = models.DateTimeField(db_column='dtTo', blank=True, null=True)
    sprd = models.CharField(db_column='sPrd', max_length=100, blank=True, null=True)
    slossrec = models.CharField(db_column='sLossRec', max_length=100, blank=True, null=True)
    sform = models.CharField(db_column='sForm', max_length=100, blank=True, null=True)
    sinfo = models.CharField(db_column='sInfo', max_length=500, blank=True, null=True)
    sinterest = models.CharField(db_column='sInterest', max_length=500, blank=True, null=True)
    srmk = models.CharField(db_column='sRmk', max_length=250, blank=True, null=True)
    sterms = models.CharField(db_column='sTerms', max_length=2000, blank=True, null=True)
    spack = models.CharField(db_column='sPack', max_length=100, blank=True, null=True)
    fsumtot = models.FloatField(db_column='fSumTOT', blank=True, null=True)
    sconvey = models.CharField(db_column='sConvey', max_length=100, blank=True, null=True)
    svoyage = models.CharField(db_column='sVoyage', max_length=100, blank=True, null=True)
    slaw = models.CharField(db_column='sLaw', max_length=200, blank=True, null=True)
    sded = models.CharField(db_column='sDed', max_length=300, blank=True, null=True)
    fpccomm = models.FloatField(db_column='fPCComm', blank=True, null=True)
    scomm = models.CharField(db_column='sComm', max_length=50, blank=True, null=True)
    fpcreinsur = models.FloatField(db_column='fPCReinsur', blank=True, null=True)
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)
    dtde = models.DateTimeField(db_column='dtDE', blank=True, null=True)
    ndel = models.IntegerField(db_column='nDel', blank=True, null=True)
    iduserdel = models.BigIntegerField(db_column='IDUserDel', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    dtinv = models.DateTimeField(db_column='dtInv', blank=True, null=True)
    iduserinv = models.BigIntegerField(db_column='IDUserInv', blank=True, null=True)
    idreinsurer = models.BigIntegerField(db_column='IDReinsurer', blank=True, null=True)
    nstatus = models.SmallIntegerField(db_column='nStatus', blank=True, null=True)
    ssuminsured = models.CharField(db_column='sSumInsured', max_length=100, blank=True, null=True)
    sdocno = models.CharField(db_column='sDocNo', max_length=25, blank=True, null=True)
    idslm10 = models.BigIntegerField(db_column='IDSLM10', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33CVN10'


class T33Cvn11(models.Model):
    idcvn11 = models.BigAutoField(db_column='IDCVN11', primary_key=True)
    idcvn10 = models.ForeignKey(T33Cvn10, models.DO_NOTHING, db_column='IDCVN10', blank=True, null=True)
    sitemname = models.CharField(db_column='sItemName', max_length=100, blank=True, null=True)
    idcur10 = models.ForeignKey(T01Cur10, models.DO_NOTHING, db_column='IDCUR10', blank=True, null=True)
    fcurrrt = models.FloatField(db_column='fCurrRt', blank=True, null=True)
    fsuminsured = models.FloatField(db_column='fSumInsured', blank=True, null=True)
    fpcshare = models.FloatField(db_column='fPcShare', blank=True, null=True)
    ftctoinsure = models.FloatField(db_column='fTCToInsure', blank=True, null=True)
    ftpcrt = models.FloatField(db_column='fTPcRt', blank=True, null=True)
    ftpmrt = models.FloatField(db_column='fTPMRt', blank=True, null=True)
    fduration = models.FloatField(db_column='fDuration', blank=True, null=True)
    fpcrt = models.FloatField(db_column='fPcRt', blank=True, null=True)
    fpmrt = models.FloatField(db_column='fPMRt', blank=True, null=True)
    ftcprem = models.FloatField(db_column='fTCPrem', blank=True, null=True)
    fbctoinsure = models.FloatField(db_column='fBCToInsure', blank=True, null=True)
    fbcprem = models.FloatField(db_column='fBCPrem', blank=True, null=True)
    idinv10 = models.ForeignKey('T33Inv10', models.DO_NOTHING, db_column='IDINV10', blank=True, null=True)
    iditm10 = models.ForeignKey('T33Itm10', models.DO_NOTHING, db_column='IDITM10', blank=True, null=True)
    fpctopup = models.FloatField(db_column='fPcTopup', blank=True, null=True)
    ftinsure = models.FloatField(db_column='fTInsure', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33CVN11'


class T33End10(models.Model):
    idend10 = models.BigAutoField(db_column='IDEND10', primary_key=True)
    idcom10 = models.BigIntegerField(db_column='IDCOM10', blank=True, null=True)
    idcur10 = models.BigIntegerField(db_column='IDCUR10', blank=True, null=True)
    idcvl10 = models.BigIntegerField(db_column='IDCVL10', blank=True, null=True)
    nendno = models.BigIntegerField(db_column='nEndNo', blank=True, null=True)
    sprg = models.CharField(db_column='sPrg', max_length=4, blank=True, null=True)
    sfileno = models.CharField(db_column='sFileNo', max_length=10, blank=True, null=True)
    srefno = models.CharField(db_column='sRefNo', max_length=15, blank=True, null=True)
    sdesc = models.CharField(db_column='sDesc', max_length=500, blank=True, null=True)
    sterms = models.CharField(db_column='sTerms', max_length=1000, blank=True, null=True)
    dtdate = models.DateTimeField(db_column='dtDate', blank=True, null=True)
    binvtype = models.BooleanField(db_column='bInvType', blank=True, null=True)
    fshamt = models.FloatField(db_column='fShAmt', blank=True, null=True)
    fpcshare = models.FloatField(db_column='fPcShare', blank=True, null=True)
    fpccomm = models.FloatField(db_column='fPcComm', blank=True, null=True)
    finvamt = models.FloatField(db_column='fInvAmt', blank=True, null=True)
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)
    dtde = models.DateTimeField(db_column='dtDE', blank=True, null=True)
    iduseredit = models.BigIntegerField(db_column='IDUserEdit', blank=True, null=True)
    dtedit = models.DateTimeField(db_column='dtEdit', blank=True, null=True)
    iduserdel = models.BigIntegerField(db_column='IDUserDel', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    bdelete = models.BooleanField(db_column='bDelete', blank=True, null=True)
    idinvoice = models.BigIntegerField(db_column='IDInvoice', blank=True, null=True)
    nstatus = models.SmallIntegerField(db_column='nStatus', blank=True, null=True)
    dtinv = models.DateTimeField(db_column='dtInv', blank=True, null=True)
    iduserinv = models.BigIntegerField(db_column='IDUserInv', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33END10'


class T33End11(models.Model):
    idend11 = models.BigAutoField(db_column='IDEND11')
    idend10 = models.BigIntegerField(db_column='IDEND10')
    sdescription = models.CharField(db_column='sDescription', max_length=255, blank=True, null=True)
    idcur10 = models.BigIntegerField(db_column='IDCUR10')
    idbcur10 = models.BigIntegerField(db_column='IDBCUR10', blank=True, null=True)
    fcurrrate = models.FloatField(db_column='fCurrRate', blank=True, null=True)
    fsuminsured = models.FloatField(db_column='fSumInsured', blank=True, null=True)
    fpcrate = models.FloatField(db_column='fPcRate', blank=True, null=True)
    fpmrate = models.FloatField(db_column='fPMRate', blank=True, null=True)
    fpremium = models.FloatField(db_column='fPremium', blank=True, null=True)
    idinv10 = models.BigIntegerField(db_column='IDINV10', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33END11'


class T33End12(models.Model):
    idend12 = models.BigAutoField(db_column='IDEND12')
    idreinsurer = models.BigIntegerField(db_column='IDReInsurer', blank=True, null=True)
    fpcshare = models.FloatField(db_column='fPcShare', blank=True, null=True)
    sremarks = models.CharField(db_column='sRemarks', max_length=255, blank=True, null=True)
    idend10 = models.BigIntegerField(db_column='IDEND10')

    class Meta:
    #    managed = False
        db_table = 'T33END12'


class T33Inv10(models.Model):
    idinv10 = models.BigAutoField(db_column='IDINV10', primary_key=True)
    ndocno = models.BigIntegerField(db_column='nDocNo', blank=True, null=True)
    dtdoc = models.DateTimeField(db_column='dtDoc', blank=True, null=True)
    idcus10 = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDCUS10', blank=True, null=True)
    sremarks = models.CharField(db_column='sRemarks', max_length=200, blank=True, null=True)
    idcom10 = models.BigIntegerField(db_column='IDCOM10', blank=True, null=True)
    idcur10 = models.ForeignKey(T01Cur10, models.DO_NOTHING, db_column='IDCUR10', blank=True, null=True)
    idcvl10 = models.BigIntegerField(db_column='IDCVL10', blank=True, null=True)
    sprg = models.CharField(db_column='sPrg', max_length=4, blank=True, null=True)
    dtdue = models.DateTimeField(db_column='dtDue', blank=True, null=True)
    finsured = models.FloatField(db_column='fInsured', blank=True, null=True)
    fpremium = models.FloatField(db_column='fPremium', blank=True, null=True)
    fpcshare = models.FloatField(db_column='fpcShare', blank=True, null=True)
    fpccomm = models.FloatField(db_column='fpcComm', blank=True, null=True)
    fcomm = models.FloatField(db_column='fComm', blank=True, null=True)
    finvamt = models.FloatField(db_column='fInvAmt', blank=True, null=True)
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)
    dtde = models.DateTimeField(db_column='dtDE', blank=True, null=True)
    nglcode = models.IntegerField(db_column='nGLCode', blank=True, null=True)
    idvoucher = models.BigIntegerField(db_column='IDVoucher', blank=True, null=True)
    npost = models.SmallIntegerField(db_column='nPost', blank=True, null=True)
    iduserpost = models.BigIntegerField(db_column='IDUserPost', blank=True, null=True)
    dtpost = models.DateTimeField(db_column='dtPost', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    ndel = models.IntegerField(db_column='nDel', blank=True, null=True)
    sfrom = models.CharField(db_column='sFrom', max_length=4, blank=True, null=True)
    fagentcomm = models.FloatField(db_column='fAgentComm', blank=True, null=True)
    fctotal = models.FloatField(db_column='fCTotal', blank=True, null=True)
    fcustomer = models.FloatField(db_column='fCustomer', blank=True, null=True)
    fdtotal = models.FloatField(db_column='fDTotal', blank=True, null=True)
    finscomp = models.FloatField(db_column='fInsComp', blank=True, null=True)
    fsalescomm = models.FloatField(db_column='fSalesComm', blank=True, null=True)
    fthirdparty = models.FloatField(db_column='fThirdParty', blank=True, null=True)
    idity10 = models.BigIntegerField(db_column='IDITY10', blank=True, null=True)
    idpol10 = models.BigIntegerField(db_column='IDPOL10', blank=True, null=True)
    sthirdparty = models.CharField(db_column='sThirdParty', max_length=50, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33INV10'


class T33Itm10(models.Model):
    iditm10 = models.BigAutoField(db_column='IDItm10', primary_key=True)
    sname = models.CharField(db_column='sName', max_length=50, blank=True, null=True)
    scode = models.CharField(db_column='sCode', max_length=4, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33ITM10'


class T33Ity10(models.Model):
    idity10 = models.BigAutoField(db_column='IDITY10', primary_key=True)
    npolytype = models.CharField(db_column='nPolytype', max_length=50, blank=True, null=True)
    sprg = models.CharField(db_column='sPrg', max_length=10, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33ITY10'


class T33Lib10(models.Model):
    idlib10 = models.BigAutoField(db_column='IDLIB10', primary_key=True)
    sprg = models.CharField(db_column='sPrg', max_length=4, blank=True, null=True)
    sdoctype = models.CharField(db_column='sDocType', max_length=4, blank=True, null=True)
    sdocno = models.CharField(db_column='sDocNo', max_length=25, blank=True, null=True)
    ndocno = models.BigIntegerField(db_column='nDocNo', blank=True, null=True)
    dtdoc = models.DateTimeField(db_column='dtDoc', blank=True, null=True)
    idinsured = models.BigIntegerField(db_column='IDInsured', blank=True, null=True)
    idprincipal = models.BigIntegerField(db_column='IDPrincipal', blank=True, null=True)
    sdescription = models.TextField(db_column='sDescription', blank=True, null=True)
    slocation = models.CharField(db_column='sLocation', max_length=255, blank=True, null=True)
    fordvalue = models.FloatField(db_column='fOrdValue', blank=True, null=True)
    nstaff = models.IntegerField(db_column='nStaff', blank=True, null=True)
    sstaffcomm = models.CharField(db_column='sStaffComm', max_length=255, blank=True, null=True)
    speriod = models.CharField(db_column='sPeriod', max_length=255, blank=True, null=True)
    scover = models.TextField(db_column='sCover', blank=True, null=True)
    sform = models.CharField(db_column='sForm', max_length=255, blank=True, null=True)
    strigger = models.CharField(db_column='sTrigger', max_length=255, blank=True, null=True)
    dtractive = models.DateTimeField(db_column='dtRActive', blank=True, null=True)
    idloc10 = models.BigIntegerField(db_column='IDLOC10', blank=True, null=True)
    slaw = models.CharField(db_column='sLaw', max_length=255, blank=True, null=True)
    slimitliability = models.TextField(db_column='sLimitLiability', blank=True, null=True)
    sconditions = models.TextField(db_column='sConditions', blank=True, null=True)
    sexclusions = models.TextField(db_column='sExclusions', blank=True, null=True)
    sexcess = models.CharField(db_column='sExcess', max_length=255, blank=True, null=True)
    fpremium = models.FloatField(db_column='fPremium', blank=True, null=True)
    spremium = models.CharField(db_column='sPremium', max_length=255, blank=True, null=True)
    fsecurity = models.FloatField(db_column='fSecurity', blank=True, null=True)
    ssecurity = models.CharField(db_column='sSecurity', max_length=255, blank=True, null=True)
    fcommission = models.FloatField(db_column='fCommission', blank=True, null=True)
    scommission = models.CharField(db_column='sCommission', max_length=255, blank=True, null=True)
    ssubject = models.CharField(db_column='sSubject', max_length=255, blank=True, null=True)
    frate = models.FloatField(db_column='fRate', blank=True, null=True)
    srate = models.CharField(db_column='sRate', max_length=255, blank=True, null=True)
    ndel = models.IntegerField(db_column='nDel', blank=True, null=True)
    iduserdel = models.BigIntegerField(db_column='IDUserDel', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    dtinv = models.DateTimeField(db_column='dtInv', blank=True, null=True)
    iduserinv = models.BigIntegerField(db_column='IDUserInv', blank=True, null=True)
    fcurrrate = models.FloatField(db_column='fCurrRate', blank=True, null=True)
    idbcur10 = models.BigIntegerField(db_column='IDBCUR10', blank=True, null=True)
    idcom10 = models.BigIntegerField(db_column='IDCOM10', blank=True, null=True)
    idcur10 = models.BigIntegerField(db_column='IDCUR10', blank=True, null=True)
    nstatus = models.IntegerField(db_column='nStatus', blank=True, null=True)
    nvehicles = models.IntegerField(db_column='nVehicles', blank=True, null=True)
    svehicles = models.CharField(db_column='sVehicles', max_length=255, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33LIB10'


class T33Lib20(models.Model):
    idlib20 = models.BigAutoField(db_column='IDLIB20', primary_key=True)
    idlib10 = models.ForeignKey(T33Lib10, models.DO_NOTHING, db_column='IDLIB10', blank=True, null=True)
    sprg = models.CharField(db_column='sPrg', max_length=4, blank=True, null=True)
    sdoctype = models.CharField(db_column='sDocType', max_length=4, blank=True, null=True)
    sdocno = models.CharField(db_column='sDocNo', max_length=25, blank=True, null=True)
    ndocno = models.BigIntegerField(db_column='nDocNo', blank=True, null=True)
    dtdoc = models.DateTimeField(db_column='dtDoc', blank=True, null=True)
    idinsured = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDInsured', blank=True, null=True)
    idprincipal = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDPrincipal', blank=True, null=True)
    idreinsurer = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDReInsurer', blank=True, null=True)
    sdescription = models.TextField(db_column='sDescription', blank=True, null=True)
    slocation = models.CharField(db_column='sLocation', max_length=255, blank=True, null=True)
    fordvalue = models.FloatField(db_column='fOrdValue', blank=True, null=True)
    nstaff = models.IntegerField(db_column='nStaff', blank=True, null=True)
    sstaffcomm = models.CharField(db_column='sStaffComm', max_length=255, blank=True, null=True)
    speriod = models.CharField(db_column='sPeriod', max_length=255, blank=True, null=True)
    scover = models.TextField(db_column='sCover', blank=True, null=True)
    sform = models.CharField(db_column='sForm', max_length=255, blank=True, null=True)
    strigger = models.CharField(db_column='sTrigger', max_length=255, blank=True, null=True)
    dtractive = models.DateTimeField(db_column='dtRActive', blank=True, null=True)
    idloc10 = models.ForeignKey('T33Loc10', models.DO_NOTHING, db_column='IDLOC10', blank=True, null=True)
    slaw = models.CharField(db_column='sLaw', max_length=255, blank=True, null=True)
    slimitliability = models.TextField(db_column='sLimitLiability', blank=True, null=True)
    sconditions = models.TextField(db_column='sConditions', blank=True, null=True)
    sexclusions = models.TextField(db_column='sExclusions', blank=True, null=True)
    sexcess = models.CharField(db_column='sExcess', max_length=510, blank=True, null=True)
    fpremium = models.FloatField(db_column='fPremium', blank=True, null=True)
    spremium = models.CharField(db_column='sPremium', max_length=255, blank=True, null=True)
    fshare = models.FloatField(db_column='fShare', blank=True, null=True)
    fcommission = models.FloatField(db_column='fCommission', blank=True, null=True)
    scommission = models.CharField(db_column='sCommission', max_length=255, blank=True, null=True)
    ssubject = models.CharField(db_column='sSubject', max_length=255, blank=True, null=True)
    frate = models.FloatField(db_column='fRate', blank=True, null=True)
    srate = models.CharField(db_column='sRate', max_length=255, blank=True, null=True)
    ndel = models.IntegerField(db_column='nDel', blank=True, null=True)
    iduserdel = models.BigIntegerField(db_column='IDUserDel', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    dtinv = models.DateTimeField(db_column='dtInv', blank=True, null=True)
    iduserinv = models.BigIntegerField(db_column='IDUserInv', blank=True, null=True)
    fcurrrate = models.FloatField(db_column='fCurrRate', blank=True, null=True)
    idbcur10 = models.BigIntegerField(db_column='IDBCUR10', blank=True, null=True)
    idcom10 = models.BigIntegerField(db_column='IDCOM10', blank=True, null=True)
    idcur10 = models.BigIntegerField(db_column='IDCUR10', blank=True, null=True)
    nstatus = models.IntegerField(db_column='nStatus', blank=True, null=True)
    nvehicles = models.IntegerField(db_column='nVehicles', blank=True, null=True)
    svehicles = models.CharField(db_column='sVehicles', max_length=255, blank=True, null=True)
    fsecurity = models.FloatField(db_column='fSecurity', blank=True, null=True)
    ssecurity = models.CharField(db_column='sSecurity', max_length=255, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33LIB20'


class T33Loc10(models.Model):
    idloc10 = models.BigAutoField(db_column='IDLoc10', primary_key=True)
    sname = models.CharField(db_column='sName', max_length=50, blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33LOC10'


class T33Pol10(models.Model):
    idpol10 = models.BigAutoField(db_column='IDPOL10', primary_key=True)
    idinv10 = models.BigIntegerField(db_column='IDINV10')
    idity10 = models.ForeignKey(T33Ity10, models.DO_NOTHING, db_column='IDITY10', blank=True, null=True)
    spolyno = models.CharField(db_column='sPolyno', max_length=100, blank=True, null=True)
    dtpoly = models.DateTimeField(db_column='dtPoly', blank=True, null=True)
    sendono = models.CharField(db_column='sEndono', max_length=100, blank=True, null=True)
    dtfrom = models.DateTimeField(db_column='dtFrom', blank=True, null=True)
    dtto = models.DateTimeField(db_column='dtTo', blank=True, null=True)
    finvamt = models.FloatField(db_column='fINVamt', blank=True, null=True)
    fdiscount = models.FloatField(db_column='fDiscount', blank=True, null=True)
    sdiscountdesc = models.CharField(db_column='sDiscountdesc', max_length=100, blank=True, null=True)
    sname = models.CharField(db_column='sName', max_length=50, blank=True, null=True)
    slare = models.CharField(db_column='sLAre', max_length=50, blank=True, null=True)
    nage = models.IntegerField(db_column='nAge', blank=True, null=True)
    dtdob = models.DateTimeField(db_column='dtDOB', blank=True, null=True)
    sarea = models.CharField(db_column='sArea', max_length=50, blank=True, null=True)
    sename = models.CharField(db_column='sEName', max_length=50, blank=True, null=True)
    saddress = models.CharField(db_column='sAddress', max_length=50, blank=True, null=True)
    sphone = models.CharField(db_column='sPhone', max_length=10, blank=True, null=True)
    semail = models.CharField(db_column='sEMail', max_length=50, blank=True, null=True)
    syear = models.CharField(max_length=10, blank=True, null=True)
    schassisno = models.CharField(db_column='sChassisno', max_length=10, blank=True, null=True)
    sengno = models.CharField(db_column='sEngno', max_length=10, blank=True, null=True)
    suse = models.CharField(db_column='sUse', max_length=50, blank=True, null=True)
    semort = models.CharField(db_column='sEMort', max_length=50, blank=True, null=True)
    splateco = models.CharField(db_column='sPlateco', max_length=50, blank=True, null=True)
    snumber = models.CharField(db_column='sNumber', max_length=50, blank=True, null=True)
    fvechicle = models.FloatField(db_column='fVechicle', blank=True, null=True)
    idsalescnt = models.BigIntegerField(db_column='IDsalesCNT', blank=True, null=True)
    idcustcnt = models.ForeignKey(T01Cnt10, models.DO_NOTHING, db_column='IDcustCNT', blank=True, null=True)
    idagentscnt = models.BigIntegerField(db_column='IDagentsCNT', blank=True, null=True)
    idinsurcnt = models.BigIntegerField(db_column='IDinsurCNT', blank=True, null=True)
    idthirdcnt = models.BigIntegerField(db_column='IDthirdCNT', blank=True, null=True)
    finsvalue = models.FloatField(db_column='fInsvalue', blank=True, null=True)
    fpremium = models.FloatField(blank=True, null=True)
    idmanuf = models.ForeignKey('Tmake', models.DO_NOTHING, db_column='IDManuf', blank=True, null=True)
    idbody = models.ForeignKey('Tbodytype', models.DO_NOTHING, db_column='IDBody', blank=True, null=True)
    idcolor = models.ForeignKey('Tcolor', models.DO_NOTHING, db_column='IDColor', blank=True, null=True)
    idnationality = models.ForeignKey('Tnationality', models.DO_NOTHING, db_column='IDNationality', blank=True, null=True)
    idmodel = models.ForeignKey('Tmodel', models.DO_NOTHING, db_column='IDModel', blank=True, null=True)
    fdisc = models.FloatField(db_column='fDisc', blank=True, null=True)
    npolcategory = models.IntegerField(db_column='nPolCategory', blank=True, null=True)
    npassenger = models.IntegerField(db_column='nPassenger', blank=True, null=True)
    binsdriver = models.BooleanField(db_column='bInsDriver', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33POL10'


class T33Slp10(models.Model):
    idslp10 = models.BigAutoField(db_column='IDSLP10', primary_key=True)
    nstatus = models.IntegerField(db_column='nStatus', blank=True, null=True)
    sprg = models.CharField(db_column='sPrg', max_length=10, blank=True, null=True)
    ntype = models.BigIntegerField(db_column='nType', blank=True, null=True)
    sdoctype = models.CharField(db_column='sDocType', max_length=10, blank=True, null=True)
    ndocno = models.BigIntegerField(db_column='nDocNo', blank=True, null=True)
    dtdoc = models.DateTimeField(db_column='dtDoc', blank=True, null=True)
    idcur10 = models.BigIntegerField(db_column='IDCUR10', blank=True, null=True)
    stype = models.CharField(db_column='sType', max_length=50, blank=True, null=True)
    idinsured = models.BigIntegerField(db_column='IDInsured', blank=True, null=True)
    idcedent = models.BigIntegerField(db_column='IDCedent', blank=True, null=True)
    idloc10 = models.ForeignKey(T33Loc10, models.DO_NOTHING, db_column='IDLOC10', blank=True, null=True)
    fpmrt = models.FloatField(db_column='fPMRt', blank=True, null=True)
    fpcrt = models.FloatField(db_column='fPCRt', blank=True, null=True)
    srt = models.CharField(db_column='sRt', max_length=50, blank=True, null=True)
    fpccomm = models.FloatField(db_column='fPCComm', blank=True, null=True)
    scommission = models.CharField(db_column='sCommission', max_length=50, blank=True, null=True)
    fpcfac = models.FloatField(db_column='fPCFac', blank=True, null=True)
    sfac = models.CharField(db_column='sFac', max_length=50, blank=True, null=True)
    fpcnoclm = models.FloatField(db_column='fPCNoClm', blank=True, null=True)
    ftclsnoclm = models.FloatField(db_column='fTCLSNoClm', blank=True, null=True)
    fbclsnoclm = models.FloatField(db_column='fBCLSNoClm', blank=True, null=True)
    snoclm = models.CharField(db_column='sNoClm', max_length=50, blank=True, null=True)
    ftcprem = models.FloatField(db_column='fTCPrem', blank=True, null=True)
    fbcprem = models.FloatField(db_column='fBCPrem', blank=True, null=True)
    sprem = models.CharField(db_column='sPrem', max_length=50, blank=True, null=True)
    fpcret = models.FloatField(db_column='fPCRet', blank=True, null=True)
    sret = models.CharField(db_column='sRet', max_length=50, blank=True, null=True)
    sprd = models.CharField(db_column='sPrd', max_length=50, blank=True, null=True)
    dtfrom = models.DateTimeField(db_column='dtFrom', blank=True, null=True)
    dtto = models.DateTimeField(db_column='dtTo', blank=True, null=True)
    slaw = models.CharField(db_column='sLaw', max_length=50, blank=True, null=True)
    fsummd = models.FloatField(db_column='fSumMD', blank=True, null=True)
    fsumlop = models.FloatField(db_column='fSumLOP', blank=True, null=True)
    fsumtot = models.FloatField(db_column='fSumTOT', blank=True, null=True)
    srmk = models.CharField(db_column='sRmk', max_length=500, blank=True, null=True)
    scover = models.CharField(db_column='sCover', max_length=500, blank=True, null=True)
    sdeduct = models.CharField(db_column='sDeduct', max_length=500, blank=True, null=True)
    slossrec = models.CharField(db_column='sLossRec', max_length=50, blank=True, null=True)
    sinterest = models.CharField(db_column='sInterest', max_length=500, blank=True, null=True)
    spack = models.CharField(db_column='sPack', max_length=50, blank=True, null=True)
    svoyage = models.CharField(db_column='sVoyage', max_length=50, blank=True, null=True)
    sconvey = models.CharField(db_column='sConvey', max_length=50, blank=True, null=True)
    sterms = models.CharField(db_column='sTerms', max_length=50, blank=True, null=True)
    sform = models.CharField(db_column='sForm', max_length=50, blank=True, null=True)
    sinformation = models.CharField(db_column='sInformation', max_length=500, blank=True, null=True)
    ndel = models.IntegerField(db_column='nDel', blank=True, null=True)
    dtdel = models.DateTimeField(db_column='dtDel', blank=True, null=True)
    iduser = models.BigIntegerField(db_column='IDUser', blank=True, null=True)
    dtde = models.DateTimeField(db_column='dtDE', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33SLP10'


class T33Slp11(models.Model):
    idslp11 = models.BigAutoField(db_column='IDSLP11', primary_key=True)
    idslp10 = models.ForeignKey(T33Slp10, models.DO_NOTHING, db_column='IDSLP10', blank=True, null=True)
    iditm10 = models.ForeignKey(T33Itm10, models.DO_NOTHING, db_column='IDItm10', blank=True, null=True)
    ftctoinsure = models.FloatField(db_column='fTCToInsure', blank=True, null=True)
    fbctoinsure = models.FloatField(db_column='fBCToInsure', blank=True, null=True)
    ftcinsured = models.FloatField(db_column='fTCInsured', blank=True, null=True)
    fbcinsured = models.FloatField(db_column='fBCInsured', blank=True, null=True)
    fcurrrt = models.FloatField(db_column='fCurrRt', blank=True, null=True)
    fpcrt = models.FloatField(db_column='fPCRt', blank=True, null=True)
    fpmrt = models.FloatField(db_column='fPMRt', blank=True, null=True)
    fprem = models.FloatField(db_column='fPrem', blank=True, null=True)
    fldsupdatedbycvnfolllowallintransactioncurrency = models.CharField(db_column='FldsUpdatedByCVNFolllowAllInTransactionCurrency', max_length=10, blank=True, null=True)
    frt = models.FloatField(db_column='fRt', blank=True, null=True)
    fcomm = models.FloatField(db_column='fComm', blank=True, null=True)
    ffac = models.FloatField(db_column='fFac', blank=True, null=True)
    fnoclm = models.FloatField(db_column='fNoClm', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33SLP11'


class T33Slp12(models.Model):
    idslp12 = models.BigAutoField(db_column='IDSLP12', primary_key=True)
    idslp10 = models.ForeignKey(T33Slp10, models.DO_NOTHING, db_column='IDSLP10', blank=True, null=True)
    idreinsurer = models.BigIntegerField(db_column='IDReinsurer', blank=True, null=True)
    dtdate = models.DateTimeField(db_column='dtDate', blank=True, null=True)

    class Meta:
    #    managed = False
        db_table = 'T33SLP12'
"""
