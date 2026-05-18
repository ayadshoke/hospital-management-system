from django.db.models import Sum
from rest_framework import serializers
from .models import Appointments,Doctors,Departments,Patients,Payment
from doctors.serializer import AppSerializer,PatSerializer


"""علشان اجيب بيانات الدكاتره ولازم يكون فيه علاقة """
class DocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctors
        fields= ['name','phone','email','address']

class PaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['paid_type','paid_date','amount']

#============================================================================
class DepSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='get_name_display', read_only=True)
    floor = serializers.CharField(source='get_floor_display', read_only=True)
    patient = serializers.SerializerMethodField()
    # doc_url = serializers.HyperlinkedModelSerializer(view_name='dep_doc',lookup_field='pk')
    docs = DocSerializer(source='doctors_set',many=True,read_only=True) # لة فيه علاقة بين الموديلات مع بعض

    detects = serializers.SerializerMethodField() # في حالة عدم وجود علاقة مباشره مع models
    doc_count = serializers.SerializerMethodField()
    detect_count = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    patient_count = serializers.SerializerMethodField()
    paid_type = serializers.SerializerMethodField()


    class Meta:
        model = Departments
        fields=('pk','part_name','floor','phone','doc_count','docs','patient_count','detect_count','amount','patient','detects','paid_type')
    def get_doc_count(self,obj):
        return obj.doctors_set.count()
    def get_detect_count(self,obj):
        return Appointments.objects.filter(paid_stat=True,doctor__part=obj).exclude(status='3').count()
    def get_patient_count(self,obj):
        return Appointments.objects.filter(paid_stat=True,status='1',doctor__part=obj).count()
    def get_amount(self,obj):
        total = Appointments.objects.filter(paid_stat=True,doctor__part=obj).aggregate(sum=Sum('detect_value'))['sum']or 0
        return total
    def get_patient(self,obj):
        patients = Patients.objects.filter(
            appointments__paid_stat=True,
            appointments__doctor__part=obj).distinct()
        return PatSerializer(patients,many=True).data # تستخدم في حالة عدم وجود علاقة مباشرة بين models
    def get_detects(self,obj):
        detects = Appointments.objects.filter(doctor__part=obj,paid_stat=True)
        return AppSerializer(detects,many=True).data
    def get_paid_type(self,obj):
        paid_type = Payment.objects.filter(appoint__doctor__part=obj)
        return PaySerializer(paid_type,many=True).data
