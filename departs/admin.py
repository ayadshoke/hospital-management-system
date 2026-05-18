from django.contrib import admin
from .models import Doctors,Departments,Area,Appointments,Patients,Days,Payment

# Register your models here.
admin.site.register(Departments)
admin.site.register(Doctors)
admin.site.register(Patients)
admin.site.register(Appointments)
admin.site.register(Area)
admin.site.register(Days)
admin.site.register(Payment)




