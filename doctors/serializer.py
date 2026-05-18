from django.db.models import Sum
from rest_framework import serializers
from departs.models import Doctors,Appointments,Payment,Days,Patients


# دي نفس فكرة prefetch_related
class DocNameSerializer(serializers.ModelSerializer):
    part = serializers.CharField(source='part.get_name_display')
    class Meta:
        model = Doctors
        fields =['pk','name','part','email']



class PaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['paid_type','paid_date','amount']


class AppSerializer(serializers.ModelSerializer):
    detect = serializers.CharField(source='get_detect_display')
    status = serializers.CharField(source='get_status_display')
    employee = serializers.CharField(source='employee.username')
    doctor = serializers.CharField(source='doctor.name')
    part = serializers.CharField(source='doctor.part.get_name_display')
    paid_type = PaySerializer(source='payment_set',many=True,read_only=True)
    class Meta:
        model = Appointments
        fields = ['part','doctor','detect','detect_value','created_at','status','employee','paid_type']

class PatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = ['name']

class DaySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_display',read_only=True)
    class Meta:
        model= Days
        fields =['day_name','available']


#=====================================================================

class DocSerializer(serializers.ModelSerializer):
    depart = serializers.CharField(source='part.get_name_display',read_only=True) # ده علشان part موحود في model الدكتور

    pat_count = serializers.SerializerMethodField()# عامود محسوب لازم ليه معادلة
    detects = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    count_day = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField() # هنا عملتها كده علشان نحذف التكرار


    days = DaySerializer(source='days_set',many=True,read_only=True)
    detect = AppSerializer(source='appointments_set',many=True,read_only=True)


    class Meta:
        model = Doctors
        fields = ['pk','name','depart','phone','email','pat_count','detects','amount','count_day','patient','days','detect']

    def get_detects(self,obj): # obj هنا بيكون دكتور
        detects = Appointments.objects.filter(paid_stat=True,doctor=obj).count()
        return detects
    def get_amount(self,obj):
        amount = Payment.objects.filter(appoint__doctor=obj).aggregate(total=Sum('amount'))['total']or 0
        return amount
    def get_count_day(self,obj):
        count_day = Days.objects.filter(doctor=obj).count()
        return count_day
    def get_pat_count(self,obj):
        count =Patients.objects.filter(appointments__doctor=obj).distinct().count()
        return count
    def get_patient(self,obj):
        pats = Patients.objects.filter(appointments__doctor=obj).distinct()
        return PatSerializer(pats,many=True).data # فكره جديده
