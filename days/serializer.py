from django.db.models import Sum

from departs.models import Days, Appointments
from rest_framework import serializers
from doctors.serializer import AppSerializer,DocNameSerializer




class DaySerializer(serializers.ModelSerializer):
    day_nam = serializers.CharField(source='get_day_display',read_only=True)
    doc_name = serializers.CharField(source='doctor.name',read_only=True)
    apps = serializers.SerializerMethodField()
    detect_day = serializers.SerializerMethodField()
    amount_day = serializers.SerializerMethodField()
    part = serializers.CharField(source='doctor.part.get_name_display',read_only=True)

    class Meta:
        model = Days
        fields = ['day','doctor','day_nam','pk','doc_name','available','part','detect_day','amount_day','apps']

    def get_apps(self,obj):
        apps = Appointments.objects.filter(paid_stat=True,created_at__week_day=int(obj.day)) # دي قوية جدا علشان اجيب رقم اليوم من التاريخ
        return AppSerializer(apps,many=True).data
    def get_detect_day(self,obj):
        data = self.get_apps(obj)
        return f'{len(data)}   كشف '
    def get_amount_day(self,obj):
        amount = Appointments.objects.filter(paid_stat=True,
                created_at__week_day=int(obj.day)).aggregate(sum=Sum('detect_value'))['sum']or 0
        return f'{amount} جنيها '

