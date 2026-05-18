from django.db.models import Sum

from departs.models import Patients,Appointments,Payment
from rest_framework import serializers
from doctors.serializer import AppSerializer



class PatNameSer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields =['pk','name','age','area']

class PatSer(serializers.ModelSerializer):
    appoints =AppSerializer(source='appointments_set',many=True,read_only=True)
    appoint_count = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    class Meta:
        model =Patients
        fields = ['pk','name','age','area','appoint_count','amount','appoints']

    def get_appoint_count(self,obj):
        appoint_count= Appointments.objects.filter(patient=obj).count()
        return appoint_count
    def get_amount(self,obj):
        amount = Payment.objects.filter(appoint__patient=obj).aggregate(total=Sum('amount'))['total']or 0
        return amount