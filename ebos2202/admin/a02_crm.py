from django.contrib import admin
from ebos2202.models.m02_crm import *



class T02Cnt11Inline(admin.TabularInline):
    model = T02Cnt11
    fields= ('contact_master', 'name', 'mobile', 'email', 'designation', 'telephone')
    

class T02Cnt10Admin(admin.ModelAdmin):
    inlines = [T02Cnt11Inline]
    list_display = ('contact_name','contact_number', 'telephone', 'email', 'mobile', 'gender')
    extra = 1

class T02Tsk10Inline(admin.TabularInline):
    model = T02Tsk10
    fields= ('task_date', 'task_type', 'task_notes', 'status', 'priority', 'due_date')
    extra = 1
    
class T02Led10Admin(admin.ModelAdmin):
     inlines=[T02Tsk10Inline]
     list_display = ('first_name', 'last_name', 'email', 'phone')
     
     
class T02Opp10Admin(admin.ModelAdmin):
    inlines=[T02Tsk10Inline]
    list_display = ('lead', 'opportunity_name', 'pipeline_stage', 'currency', 'amount',
                    'probability', 'description', 'created_on', 'closed_on')

class T02Evt10Admin(admin.ModelAdmin):
    list_display = ('event_name', 'event_type', 'status', 'start_date', 'end_date', 'description')

class T02Sat10Admin(admin.ModelAdmin):
    list_display = ('division', 'date_from', 'date_upto', 'report_csv')
    exclude = ('rpt_code',)

class T02Sfc10Admin(admin.ModelAdmin):
    list_display = ('division', 'date_from', 'date_upto', 'report_csv')
    exclude = ('rpt_code',)

class T02Plr10Admin(admin.ModelAdmin):
    list_display = ('division', 'date_from', 'date_upto', 'report_csv')
    exclude = ('rpt_code',)
    
class T02Por10Admin(admin.ModelAdmin):
    list_display = ('division', 'date_from', 'date_upto', 'report_csv')
    exclude = ('rpt_code',)
    
class T02Opr10Admin(admin.ModelAdmin):
    list_display = ('division', 'date_from', 'date_upto', 'report_csv')
    exclude = ('rpt_code',)
    
admin.site.register(T02Cnt10, T02Cnt10Admin)
admin.site.register(T02Led10, T02Led10Admin)
admin.site.register(T02Opp10, T02Opp10Admin)
admin.site.register(T02Evt10, T02Evt10Admin)
admin.site.register(T02Sat10, T02Sat10Admin)
admin.site.register(T02Sfc10, T02Sfc10Admin)
admin.site.register(T02Plr10, T02Plr10Admin)
admin.site.register(T02Por10, T02Por10Admin)
admin.site.register(T02Opr10, T02Opr10Admin)
admin.site.register([T02Pil10,T02Rpt10, T02Tsk10,T02Inv10])


