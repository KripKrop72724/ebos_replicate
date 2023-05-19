from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.


def dashboard(request):
    if request.user.is_authenticated:

        if request.user.groups.filter(name="Finance").exists():
            return render(request, "dashboard/fin_dashboard.html")
        elif request.user.groups.filter(name="Crm").exists():
            return render(request, "dashboard/crm_dashboard.html")
        elif request.user.groups.filter(name="Trade").exists():
            return render(request, "dashboard/trade_dashboard.html")
        elif request.user.groups.filter(name="Hrms").exists():
            return render(request, "dashboard/hr_dashboard.html")

        return render(request, "dashboard/dashboard.html")
    else:
        return HttpResponseRedirect(reverse("admin:index"))
