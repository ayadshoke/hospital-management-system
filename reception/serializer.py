from departs.models import Appointments,Payment
from rest_framework import serializers
from departs.serializer import PaySerializer

class AppointSer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name',read_only=True)
    patient_age = serializers.CharField(source='patient.age',read_only=True)
    patient_area = serializers.CharField(source='patient.area',read_only=True)
    patient = serializers.CharField(write_only=True) # دي علشان اخفاء العامود في العرض
    det = serializers.CharField(source='get_detect_display',read_only=True)
    detect = serializers.CharField(write_only=True)
    stat = serializers.CharField(source='get_status_display',read_only=True)
    status = serializers.CharField(write_only=True)
    doct = serializers.CharField(source='doctor.name',read_only=True)
    doctor = serializers.CharField(write_only=True)
    emp = serializers.CharField(source='employee.username',read_only=True)
    employee = serializers.CharField(write_only=True)
    part = serializers.CharField(source='doctor.part.get_name_display',read_only=True)
    day = serializers.SerializerMethodField()
    paid_type = serializers.SerializerMethodField()
    class Meta:
        model = Appointments
        # fields = '__all__'
        exclude =['slug']
        # extra_kwargs ={'patient':{'required':True},
        #                'doctor':{'required':True},
        #                'detect':{'required':True}} # دي علشان يبقي الحقل الزامي لو الموديل مش متظبط

    def get_day(self,obj):
        day = obj.created_at.strftime('%A') #دالة ارجاع اسم اليوم من التاريخ
        return day
    def get_paid_type(self,obj):
        paid_type = Payment.objects.filter(appoint=obj)
        return PaySerializer(paid_type,many=True).data


class AddUpdate_appointSer(serializers.ModelSerializer):
    class Meta:
        model = Appointments
        fields = ['patient','doctor','detect']