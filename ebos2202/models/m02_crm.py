from webbrowser import get
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import gettext_lazy as _
# from dev2201.ebos2202.models.m02_crm import Opportunity
from ebos2202.utils import *
from ebos2201.models.m01_core_mas import T01Div10, T01Slu10, T01Nat10, T01Cat10 , T01Uom10
from ebos2201.models.m01_fin_mas import T01Sld10, T01Slt10, T01Lan10, T01Slm10
from django.dispatch import receiver
from io import StringIO
from django.core.files.base import ContentFile
import csv, os
from django.core.files.storage import default_storage


# contact company / agents / freelancer group ...etc
class T02Cnt10(models.Model):
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column='IdDivCnt', null=True)
    contact_name = models.CharField(db_column='sName', max_length=50, blank=True)
    short_name = models.CharField(db_column='sNameShort', max_length=5, blank=True)
    address_line1 = models.CharField(db_column='sAddr1', max_length=50, blank=True)
    address_line2 = models.CharField(db_column='sAddr2', max_length=50, blank=True)
    address_line3 = models.CharField(db_column='sAddr3', max_length=50, blank=True)
    contact_number = models.BigIntegerField(db_column='nCntNo', null=True)
    telephone = models.CharField(db_column='sTel', max_length=25, blank=True)
    fax = models.CharField(db_column='sFax', max_length=25, blank=True)
    email = models.CharField(db_column='sEmail', max_length=50, blank=True)
    mobile = models.CharField(db_column='sMobile', max_length=30, blank=True)
    gender = models.CharField(db_column='sSex', max_length=6, blank=True)
    postal_code = models.CharField(db_column='sPostCode', max_length=30, blank=True)
    region = models.CharField(db_column='sRegion', max_length=50, blank=True)
    website = models.CharField(db_column='sWebsite', max_length=50, blank=True)
    city = models.CharField(db_column='sCity', max_length=50, blank=True)
    attn_To = models.CharField(db_column='sAttnTo', max_length=50, blank=True)
    category1 = models.ForeignKey(T01Cat10, models.PROTECT, db_column='IdCntCat1', blank=True, null=True)
    category2 = models.ForeignKey(T01Cat10, models.PROTECT, related_name='cntcat2', db_column='IdCntCat2', blank=True, null=True)
    category3 = models.ForeignKey(T01Cat10, models.PROTECT, related_name='cntcat3', db_column='IdCntCat3', blank=True, null=True)
    category4 = models.ForeignKey(T01Cat10, models.PROTECT, related_name='cntcat4', db_column='IdCntCat4', blank=True, null=True)
    category5 = models.ForeignKey(T01Cat10, models.PROTECT, related_name='cntcat5', db_column='IdCntCat5', blank=True, null=True)
    nationality = models.ForeignKey(T01Nat10, models.PROTECT, db_column='IDNAT10', null=True)
    salutation = models.ForeignKey(T01Slu10, models.PROTECT, db_column='IdCntSalut', null=True)
    status = models.IntegerField(db_column='nStatus', blank=True, null=True)
    subledger = models.ForeignKey(T01Sld10, models.PROTECT, db_column='IDSubLed', null=True)
    subledger_type = models.ForeignKey(T01Slt10, models.PROTECT, db_column='IDSLType', null=True)

    class Meta:
        db_table = 'T02CNT10'
        verbose_name = 'a2.Contact Master'

    def __str__(self):
        return f"{self.division} - {self.contact_number}"

# multiple contacts in one company / agent / freelancer group
class T02Cnt11(models.Model):
    contact_master = models.ForeignKey(T02Cnt10, models.CASCADE, db_column='IDCnt10', null=True)
    name = models.CharField(db_column='sName', max_length=50)
    mobile = models.CharField(db_column='sMob', max_length=25)
    email = models.CharField(db_column='sEmail', max_length=50, blank=True)
    designation = models.CharField(db_column='sDesignation', max_length=50, blank=True)
    telephone = models.CharField(db_column='sTelNo', max_length=50, blank=True)

    class Meta:
        db_table = 'T02CNT11'
        verbose_name = 'Contact Person'

    def __str__(self) -> str:
        return self.name

# currency used in esAccounts, esEM, esIN, esIS, esWO, eTender only
class T02Led10(models.Model):
    contact = models.ForeignKey('T02Cnt10', models.PROTECT, db_column='IdCnt', null=True, blank=True)
    first_name = models.CharField(db_column='sNameF', max_length=255, blank=True)
    last_name = models.CharField(db_column='sNameL', max_length=255, blank=True)
    email = models.EmailField(db_column='eEmail',  max_length=80, null=True, blank=True)
    phone = models.CharField(db_column='sPhone', max_length=20)
    language = models.ForeignKey(T01Lan10, models.PROTECT, db_column='IdLan', null=True, blank=True)
    STATUS_CHOICE = (('assigned', 'Assigned'),('in process', 'In Process'), ('converted', 'Converted'),
                     ('recycled', 'Recycled'),('closed', 'Closed'))
    lead_status = models.CharField(db_column='sLedStats', max_length=50, choices=STATUS_CHOICE, blank=True)
    lead_source = models.ForeignKey('T02Evt10', models.PROTECT, db_column='IdEvt', null=True, blank=True) # From event
    pipeline = models.ForeignKey('T02Pil10', models.PROTECT, db_column='IdPil', null=True, blank=True)
    city = models.CharField(db_column='sCity', max_length=40, blank=True)
    country = models.CharField(db_column='sCountry', max_length=40, blank=True)
    website = models.CharField(db_column='sWebsite', max_length=60, blank=True)
    description = models.TextField(db_column='tDesc', blank=True)
    assigned_to = models.ForeignKey(T01Slm10, models.PROTECT, db_column='IdSlm', null=True, blank=True) 
    opportunity_amount = models.IntegerField(db_column='nOppAmt', blank=True, null= True)
    generated_by = models.CharField(db_column='sGenBy', max_length=80, blank=True)
    created_on = models.DateTimeField(db_column='dCreatedOn', auto_now_add=True)
    enquiry_type = models.CharField(db_column='sEnqType', max_length=40, blank=True)
    IND_CHOICE = (("ADVERTISING", "ADVERTISING"),
                  ("REAL_ESTATE", "REAL_ESTATE"),
                  ("RETAIL", "RETAIL"),
                  ("AUTOMOTIVE", "AUTOMOTIVE"),
                  ("BANKING", "BANKING"),
                  ("CONTRACTING", "CONTRACTING"),
                  ("DISTRIBUTOR", "DISTRIBUTOR"),
                  ("SERVICES", "SERVICES"),
                  ("OTHERS", "OTHERS"))
    industry = models.CharField(db_column='sIndstry', max_length=20, choices=IND_CHOICE, blank=True)
    class Meta:
        db_table = 'T02LED10'
        verbose_name = 'b1.Lead'
        
    def __str__(self):
        return str(self.first_name) + str(self.last_name)
    
    
class T02Opp10(models.Model):
    lead = models.ForeignKey(T02Led10, models.PROTECT, db_column='IdLed', null=True, blank=True)
    opportunity_name = models.CharField(db_column='sOppName', max_length=255)
    pipeline_stage = models.ForeignKey('T02Pil10', models.PROTECT, db_column='IdPil', null=True, blank=True)
    CURRENCY_CHOICE = (('AED', 'AED'), ('EUR', 'EUR'), ('USD', 'USD'), ('GBP','GBP'))
    currency = models.CharField(db_column='sCurr', max_length=3, choices=CURRENCY_CHOICE, blank=True)
    amount = models.IntegerField(db_column='nAmt', blank=True, default = 0)
    probability = models.IntegerField(db_column='nProb',default=0)
    description = models.TextField(db_column='tDesc', blank=True)
    created_on = models.DateTimeField(db_column='dtCreatedOn', auto_now_add=True)
    target_date = models.DateField(db_column='dTrgtdte', blank=True, null=True)
    closed_on = models.DateField(db_column='dClosedOn', blank=True, null=True)
    
    class Meta:
        db_table = 'T02OPP10'
        verbose_name = 'b2.Opportunity'

    def __str__(self):
        return self.opportunity_name
  
class T02Evt10(models.Model):
    event_name = models.CharField(db_column='sEvtName', max_length=255)
    EVENT_TYPE = (
        ("telecalling", "Telecalling"),
        ("visit", "Visit"),
        ("call", "Call"),
        ('email', 'Email'),
        ('webad', 'Web Advt')
    ) 
    event_type = models.CharField(db_column='sEvtType',max_length=25, choices=EVENT_TYPE)
    EVENT_STATUS = (
        ("Planned", "Planned"),
        ("Held", "Held"),
        ("Not Held", "Not Held"),
        ("Not Started", "Not Started"),
        ("Started", "Started"),
        ("Completed", "Completed"),
        ("Canceled", "Canceled"),
        ("Deferred", "Deferred"),
    )
    status = models.CharField(db_column='sEvtStats', choices=EVENT_STATUS, max_length=25, blank=True,null=True)
    start_date = models.DateTimeField(db_column='dtSrtdtetm', blank=True, null=True) 
    end_date = models.DateTimeField(db_column='dtEndDteTm', blank=True, null=True)
    description = models.TextField(db_column='tDesc', blank=True, null=True)
    
    class Meta:
        db_table = 'T02EVT10'
        verbose_name = 'a1.Marketing Event'

    def __str__(self):
        return self.event_type
    
class T02Tsk10(models.Model):
    opportunity = models.ForeignKey(T02Opp10, models.PROTECT, db_column='IdOpp', null=True)
    lead = models.ForeignKey(T02Led10, models.PROTECT, db_column='IdLed', null=True)
    STATUS_CHOICES = (
        ("New", "New"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    )
    PRIORITY_CHOICES = (("Low", "Low"), ("Medium", "Medium"), ("High", "High"))
    TASKTYPE_CHOICES = (
            ("call", "Call"),
            ("telephone call", "TelePhone Call"),
            ("email", "Email"),
            ("visit", "Visit"),
            ("meeting", "Meeting"),
            ("demo", "Demo"),
        )
    task_date = models.DateField(db_column='dTskDt', blank=True, null=True) #default current date
    task_type = models.CharField(db_column='sTskType',max_length=25, choices=TASKTYPE_CHOICES)
    task_notes = models.TextField(db_column='tTskNts', max_length=255) 
    status = models.CharField(db_column='sStatus', max_length=25, choices=STATUS_CHOICES)
    priority = models.CharField(db_column='sPriorty', max_length=25, choices=PRIORITY_CHOICES)
    due_date = models.DateField(db_column='dduedt', blank=True, null=True)
    created_on = models.DateTimeField(db_column='dtCreatedOn', auto_now_add=True)
    
    class Meta:
        db_table = 'T02TSK10'
        verbose_name = 'b3.Task'

    def __str__(self):
        return self.task_type
    
class T02Rem10(models.Model):
    reminder_date = models.DateTimeField(db_column='dtremdte', blank=True, null=True)
    reminder_type = models.CharField(db_column= 'sRemTyp', max_length=25, blank=True, null=True)
    task_to_remind = models.ForeignKey(T02Tsk10, models.PROTECT, db_column='IdTsk', null=True, blank=True)
    opportunity_follow = models.ForeignKey(T02Opp10, models.PROTECT, db_column='IdOpp', null=True, blank=True)
    lead_follow = models.ForeignKey(T02Led10, models.PROTECT, db_column='IdLed', null=True, blank=True)
    event_follow = models.ForeignKey(T02Evt10, models.PROTECT, db_column='Idevt', null=True, blank=True)
    
    def __str__(self):
        return self.reminder_type
    
class T02Pil10(models.Model):  
    pipeline_name = models.CharField(db_column='sPilName', max_length=255)
    target_days = models.IntegerField(db_column='nAllwDur', default= 0)
    probability_percent = models.IntegerField(db_column='nProbPerc', default = 10)
    is_active = models.BooleanField(db_column='bIsActive', default=False)
        
    class Meta:
        db_table = 'T02PIL10'
        verbose_name = 'a4.Pipeline Setup'
    
    def __str__(self):
        return self.pipeline_name

# Reports Base Model 
class T02Rpt10(models.Model):  
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column='IdDivCnt', null=True)
    date_from = models.DateField(db_column='dFrom', null=True)   
    date_upto = models.DateField(db_column='dUpTo', null=True) 
    rpt_code = models.CharField(db_column='sRptCode', max_length=3, blank=True, null=True)
    report_csv = models.FileField(db_column='flSlAcRpt', upload_to = 'sales_reports', null=True,  blank=True)
    class Meta:
        db_table = 'T02RPT10'
        verbose_name = 'c0.Sales Report'
        

# Sales Action Report 
class T02Sat10Manager(models.Manager):
    def get_queryset(self):
        return super(T02Sat10Manager, self).get_queryset().filter(rpt_code='SAR')
    
class T02Sat10(T02Rpt10):
    objects = T02Sat10Manager()
    
    class Meta:
        proxy = True
        verbose_name = 'c1.Sales Action Report'
    
    def save(self, *args, **kwargs):
        self.rpt_code = 'SAR'
        super(T02Sat10, self).save(*args, **kwargs)
    
# Sales forecast Report  
class T02Sfc10Manager(models.Manager):
    def get_queryset(self):
        return super(T02Sfc10Manager, self).get_queryset().filter(rpt_code='SFR')
       
class T02Sfc10(T02Rpt10):
    objects = T02Sfc10Manager()
    
    class Meta:
        proxy = True
        verbose_name = 'c2.Sales Forecast Report'

    def save(self, *args, **kwargs):
        self.rpt_code = 'SFR'
        super(T02Sfc10, self).save(*args, **kwargs)
        
        
# Pipeline Status based on Leads 
class T02Plr10Manager(models.Manager):
    def get_queryset(self):
        return super(T02Plr10Manager, self).get_queryset().filter(rpt_code='PLR')

class T02Plr10(T02Rpt10):
    objects = T02Plr10Manager()
        
    class Meta:
        proxy = True
        verbose_name = 'c3.Pipeline Status based on Lead'
        
    
    def save(self, *args, **kwargs):
        self.rpt_code = 'PLR'
        super(T02Plr10, self).save(*args, **kwargs)
        
# Pipeline Status based on Opportunities 
class T02Por10Manager(models.Manager):
    def get_queryset(self):
        return super(T02Por10Manager, self).get_queryset().filter(rpt_code='POR')

class T02Por10(T02Rpt10):
    objects = T02Por10Manager()
        
    class Meta:
        proxy = True
        verbose_name = 'c4.Pipeline Status based on Opportunity'
        
    def save(self, *args, **kwargs):
        self.rpt_code = 'POR'
        super(T02Por10, self).save(*args, **kwargs)
        
# Opportunity Review Report 
class T02Opr10Manager(models.Manager):
    def get_queryset(self):
        return super(T02Opr10Manager, self).get_queryset().filter(rpt_code='ORR')

class T02Opr10(T02Rpt10):
    objects = T02Opr10Manager()
    
    class Meta:
        proxy = True
        verbose_name = 'c5.Opportunity Review Report'

    def save(self, *args, **kwargs):
        self.rpt_code = 'ORR'
        super(T02Opr10, self).save(*args, **kwargs)
        
        
#### Actions Post Save of Proxy Models
@receiver(models.signals.post_save, sender=T02Sat10)
@receiver(models.signals.post_save, sender=T02Sfc10)
@receiver(models.signals.post_save, sender=T02Plr10)
@receiver(models.signals.post_save, sender=T02Por10)
@receiver(models.signals.post_save, sender=T02Opr10)
def sales_reports(sender, instance, **kwargs):
    division = instance.division
    date_from = instance.date_from
    date_upto = instance.date_upto
    reports = T02Rpt10.objects.filter(id = instance.id)

    if reports.filter(rpt_code='SAR').exists():
        name = "sales_action_report"
        response = StringIO()
        writer = csv.writer(response)
        
        # Adding Task record heading to csv 
        writer.writerow(['Opportunity', 'Lead', 'Task Type', 'Task Notes', 'Status', 'Priority', 'Due Date', 'Created On'])     
        
        values_list = []
        
        # filter division = input_division, task_create_date = input_date and pipleline <= 90 
        T02Tsk10_records = T02Tsk10.objects.filter(created_on__date__gte = date_from, created_on__date__lte = date_upto,
                                               opportunity__pipeline_stage__probability_percent__lte = 90,
                                               opportunity__lead__contact__division = division)
        
        # Adding Task record values to csv 
        for T02Tsk10_record in T02Tsk10_records:
            values = (T02Tsk10_record.id,T02Tsk10_record.opportunity, T02Tsk10_record.lead, T02Tsk10_record.task_type, T02Tsk10_record.task_notes,
                               T02Tsk10_record.status, T02Tsk10_record.priority, T02Tsk10_record.due_date, T02Tsk10_record.created_on)
            values_list.append(values)
            
        for value in values_list:
                writer.writerow(value)
                
        csv_file = ContentFile(response.getvalue().encode('utf-8'))
    
    elif reports.filter(rpt_code='SFR').exists():
        name = "sales_forecast_report"
        response = StringIO()
        writer = csv.writer(response)
        writer.writerow(['Opportunity Name', 'Pipeline Stage', 'Currency', 'Amount',
                         'Probability', 'Description', 'Created On', 'Target Date', 'Closed On','Lead'])
        
        # filter division, pipeline prob > 50 and prob <= 90, target_date = input_date
        T02Opp10_records = T02Opp10.objects.filter(lead__contact__division = division,
                                                   pipeline_stage__probability_percent__lte = 90,
                                                   pipeline_stage__probability_percent__gt = 50,
                                                   target_date__gte = date_from,
                                                   target_date__lte = date_upto
                                               )
        values_list = []
        
        for T02Opp10_record in T02Opp10_records:
            values = (T02Opp10_record.opportunity_name, T02Opp10_record.pipeline_stage, T02Opp10_record.currency, T02Opp10_record.amount,
                         T02Opp10_record.probability, T02Opp10_record.description, T02Opp10_record.created_on, T02Opp10_record.target_date,
                         T02Opp10_record.closed_on,T02Opp10_record.lead)
            values_list.append(values)
            
        for value in values_list:
                writer.writerow(value)
                
        csv_file = ContentFile(response.getvalue().encode('utf-8'))

    
    elif reports.filter(rpt_code='POR').exists():
        name = "pipeline_status_opportunities"
        response = StringIO()
        writer = csv.writer(response)
        pipleline_records = T02Pil10.objects.all().values('id').distinct()
        # Report on basis of Opportunities
        values_list = []
        for pipleline_record in pipleline_records:
            writer.writerow(['PIPELINE NAME', 'TARGET DAYS', 'PROBABILITY PERCENT', 'IS ACTIVE'])
            get_pipeline_data = T02Pil10.objects.get(id = pipleline_record.get('id'))
            value = (get_pipeline_data.pipeline_name, get_pipeline_data.target_days, 
                       get_pipeline_data.probability_percent, get_pipeline_data.is_active)
            writer.writerow(value)
            writer.writerow("")
            writer.writerow(['OPPORTUNITY NAME', 'PIPELINE STAGE', 'CURRENCY', 'AMOUNT', 'PROBABILITY', 'DESCRIPTION',
                         'CREATED ON', 'TARGET DATE', 'CLOSED ON'])
           
            values_list = []
            get_oppor = T02Opp10.objects.filter(pipeline_stage = get_pipeline_data.id)
            for oppor in get_oppor:
               child_values = (oppor.opportunity_name, oppor.pipeline_stage, oppor.currency, oppor.amount, oppor.probability,
                                oppor.description, oppor.created_on, oppor.target_date, oppor.closed_on)
               values_list.append(child_values)     
        
            for child_data in values_list:
                    writer.writerow(child_data)
             
            writer.writerow("")
            writer.writerow("")
               
        csv_file = ContentFile(response.getvalue().encode('utf-8'))
    
    elif reports.filter(rpt_code='PLR').exists():
        name = "pipeline_status_leads"
        pipleline_records = T02Pil10.objects.all().values('id').distinct()
        response = StringIO()
        writer = csv.writer(response)
        values_list = []
        for pipleline_record in pipleline_records:
            writer.writerow(['PIPELINE NAME', 'TARGET DAYS', 'PROBABILITY PERCENT', 'IS ACTIVE'])
            get_pipeline_data = T02Pil10.objects.get(id = pipleline_record.get('id'))
            value = (get_pipeline_data.pipeline_name, get_pipeline_data.target_days, 
                       get_pipeline_data.probability_percent, get_pipeline_data.is_active)
            writer.writerow(value)
            writer.writerow("")
            writer.writerow(['CONTACT', 'FIRST NAME', 'LAST NAME', 'EMAIL', 'PHONE', 'LANGUAGE', 'LEAD STATUS', 'LEAD SOURCE',
                             'CITY', 'COUNTRY', 'WEBSITE', 'DESCRIPTION', 'ASSIGNED TO', 'OPPORUNITY AMOUNT', 'GENERATED BY',
                             'CREATED ON', 'ENQUIRY TYPE', 'INDUSTRY'])
            values_list = []
            get_Leads = T02Led10.objects.filter(pipeline = get_pipeline_data.id)
            for get_Lead in get_Leads:
               child_values = (get_Lead.contact, get_Lead.first_name, get_Lead.last_name, get_Lead.email, get_Lead.phone, 
                               get_Lead.language, get_Lead.lead_status, get_Lead.lead_source, get_Lead.city, get_Lead.country,
                               get_Lead.website, get_Lead.description, get_Lead.assigned_to, get_Lead.opportunity_amount, 
                               get_Lead.generated_by, get_Lead.created_on, get_Lead.enquiry_type, get_Lead.industry)
               values_list.append(child_values)     
        
            for child_data in values_list:
                    writer.writerow(child_data)
             
            writer.writerow("")
            writer.writerow("")
               
        csv_file = ContentFile(response.getvalue().encode('utf-8'))
    
    elif reports.filter(rpt_code='ORR').exists():
        name = "opportunity_review_report"
        response = StringIO()
        writer = csv.writer(response)
        writer.writerow(['Opportunity Name', 'Pipeline Stage', 'Currency', 'Amount',
                         'Probability', 'Description', 'Created On', 'Target Date', 'Closed On','Lead'])

        # filter division, opportunity prob <= 90 and prob > 10, 
        T02Opp10_records = T02Opp10.objects.filter(lead__contact__division = division,
                                                   pipeline_stage__probability_percent__lte = 90,
                                                   pipeline_stage__probability_percent__gt = 10
                                                   )
        values_list = []
        for T02Opp10_record in T02Opp10_records:
            values = (T02Opp10_record.opportunity_name, T02Opp10_record.pipeline_stage, T02Opp10_record.currency, T02Opp10_record.amount,
                         T02Opp10_record.probability, T02Opp10_record.description, T02Opp10_record.created_on, T02Opp10_record.target_date,
                         T02Opp10_record.closed_on,T02Opp10_record.lead)
            values_list.append(values)
            
        for value in values_list:
                writer.writerow(value)
                
        csv_file = ContentFile(response.getvalue().encode('utf-8'))
        
    csv_file_name = f"sales_report/{name}_{str(instance.id)}.csv"
    
    if default_storage.exists(csv_file_name):
        default_storage.delete(csv_file_name)
    file_name = default_storage.save(csv_file_name, csv_file)
    
    # Update File Fields
    reports.update(report_csv = file_name)
    return True

# delete files when record delete from model...
@receiver(models.signals.post_delete, sender=T02Sat10)
@receiver(models.signals.post_delete, sender=T02Sfc10)
@receiver(models.signals.post_delete, sender=T02Plr10)
@receiver(models.signals.post_delete, sender=T02Por10)
@receiver(models.signals.post_delete, sender=T02Opr10)

def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.report_csv:
        if os.path.isfile(instance.report_csv.path):
            os.remove(instance.report_csv.path)

class T02Inv10(models.Model):
    division = models.ForeignKey(T01Div10, models.PROTECT, db_column='IdDivInv', null=True)
    item_code = models.CharField(db_column='sItmCode', max_length=19, blank=True, null=True)  
    tax_percent = models.DecimalField(max_digits=10, db_column='fTaxPerc', decimal_places=2, default='0.05') 
    item_name = models.CharField(db_column='sDesc', max_length=50, blank=True, null=True)  
    add_desc = models.CharField(db_column='sAddDesc', max_length=50, blank=True, null=True)  
    primary_uom = models.ForeignKey(T01Uom10, models.DO_NOTHING, db_column='IDPrimUnit', blank=True, null=True)  
    category1 = models.ForeignKey(T01Cat10, models.PROTECT, db_column='IdInvCat1', blank=True, null=True)
    category2 = models.ForeignKey(T01Cat10, models.PROTECT, related_name='invcat2', db_column='IdInvCat2', blank=True, null=True)
    category3 = models.ForeignKey(T01Cat10, models.PROTECT, related_name='invcat3', db_column='IdInvCat3', blank=True, null=True)
    gl_code = models.IntegerField(db_column='nGLCode', blank=True, null=True)  
    current_stock = models.FloatField(db_column='fCurStk', blank=True, null=True)  
    reserve_stock = models.FloatField(db_column='fResStk', blank=True, null=True)  
    average_cost = models.FloatField(db_column='fCostAvg', blank=True, null=True)  
    market_cost = models.FloatField(db_column='fCostMkt', blank=True, null=True)  
    sell_price = models.FloatField(db_column='fSellPrice', blank=True, null=True)  

    class Meta:
    #    managed = False
        db_table = 'T02INV10'
        verbose_name = 'a3.Product Master'
            