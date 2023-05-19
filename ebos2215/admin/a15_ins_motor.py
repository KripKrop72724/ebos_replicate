from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.translation import ngettext

from ..models.m15_ins_motor import *

admin.site.register([Customer, Certificate, Insurancecompany, Branch])


class T15Mop10Admin(admin.ModelAdmin):
    list_display = ("certificateid", "customerid", "isposted", "isdeleted")
    actions = ["post_motor_policy"]
    list_filter = ("isposted",)

    """Post motor policy custom action functionality"""

    @admin.action(description="Mark selected motor policy as posted")
    def post_motor_policy(self, request, queryset):
        try:
            posted = 0
            for q in queryset:
                if q.isdeleted == False and q.isposted == False:
                    try:
                        T15Mop10.motor_policy_post(q)
                        # update the deleted and posted flag
                        q.isdeleted = True
                        q.isposted = True
                        q.save()
                        posted += 1
                    except Exception as e:
                        raise ValueError(e)

            mess = messages.SUCCESS if posted > 0 else messages.ERROR
            self.message_user(
                request,
                ngettext(
                    "%d motor policy was successfully marked as posted.",
                    "%d motor policies were successfully marked as posted.",
                    posted,
                )
                % posted,
                mess,
            )
        except Exception as e:
            self.message_user(request, e, messages.ERROR)


admin.site.register(T15Mop10, T15Mop10Admin)
