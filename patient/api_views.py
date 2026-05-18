from django.db.models import Sum
from rest_framework import status,filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from departs.models import Patients, Appointments
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .serializer import PatSer,PatNameSer
from django_filters.rest_framework import DjangoFilterBackend

@api_view(['GET','POST'])
def all_patient(request):
    if request.method == 'GET':
        patients = Patients.objects.all()
        total_amount = patients.aggregate(total=Sum('appointments__detect_value'))['total']or 0 # جميله جدا
        pat = Patients.objects.filter(appointments__isnull=True)
        pats = Patients.objects.filter(appointments__isnull=False).distinct().order_by('name')
        pats_ser = PatSer(pats,many=True)
        pat_ser = PatNameSer(pat,many=True)
        detects = Appointments.objects.filter(paid_stat=True)

        data ={'اجمالي عدد المرضي':patients.count(),
               'عدد بدون حجز':pat.count(),
                'المرضي بدون حجز':pat_ser.data,
                'عدد الحجوزات':pats.count(),
                'عدد الكشوفات':detects.count(),
               'اجمالي المبلغ':total_amount,
                'من قاموا بالحجز':pats_ser.data}

        return Response(data,status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = PatSer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'item added','data':serializer.data},status=status.HTTP_201_CREATED)


@api_view(['GET','PUT','PATCH','DELETE'])
def all_patient_pk(request,pk):
    if request.method == 'GET':
        item = Patients.objects.get(pk=pk)
        serializer = PatSer(instance=item)
        data ={'data':serializer.data}

        return Response(data , status=status.HTTP_200_OK)

    if request.method == 'PUT':
        item = Patients.objects.get(pk=pk)
        serializer = PatSer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
        data = {'data': serializer.data}
        return Response(data, status=status.HTTP_202_ACCEPTED)

    if request.method == 'PATCH':
        item = Patients.objects.get(pk=pk)
        serializer = PatSer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
        data = {'data': serializer.data}
        return Response(data, status=status.HTTP_202_ACCEPTED)

    if request.method == 'DELETE':
        item = Patients.objects.get(pk=pk)
        item.delete()
        return Response({'message':'item deleted'})



class Show_patient(APIView):
    def get(self,request):
        patients = Patients.objects.all()
        total_amount = patients.aggregate(total=Sum('appointments__detect_value'))['total'] or 0  # جميله جدا
        pat = Patients.objects.filter(appointments__isnull=True)
        pats = Patients.objects.filter(appointments__isnull=False).distinct().order_by('name')
        pats_ser = PatSer(pats, many=True)
        pat_ser = PatNameSer(pat, many=True)

        data = {'اجمالي عدد المرضي': patients.count(),
                'عدد بدون حجز': pat.count(),
                'المرضي بدون حجز': pat_ser.data,
                'عدد الحجوزات': pats.count(),
                'اجمالي المبلغ': total_amount,
                'من قاموا بالحجز': pats_ser.data}

        return Response(data, status=status.HTTP_200_OK)

    def post(self,request):
        serializer = PatSer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'item added', 'data': serializer.data}, status=status.HTTP_201_CREATED)



class Show_patient_pk(APIView):
    def get(self,request,pk):
        item = Patients.objects.get(pk=pk)
        serializer = PatSer(instance=item)
        data ={'data':serializer.data}

        return Response(data , status=status.HTTP_200_OK)

    def put(self, request, pk):
        item = Patients.objects.get(pk=pk)
        serializer = PatSer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
        data = {'data': serializer.data}
        return Response(data, status=status.HTTP_202_ACCEPTED)

    def patch(self, request, pk):
        item = Patients.objects.get(pk=pk)
        serializer = PatSer(instance=item,data=request.data)
        if serializer.is_valid():
            serializer.save()
        data = {'data': serializer.data}
        return Response(data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk):
        item = Patients.objects.get(pk=pk)
        item.delete()
        return Response({'message':'item deleted'})


class Gener_patient(ListCreateAPIView):
    queryset = Patients.objects.filter(appointments__isnull=False).distinct().order_by('name')
    serializer_class = PatSer
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    ordering_fields = ['pk','name']
    search_fields = ['name']
    filterset_fields = ['name']
    def list(self, request, *args, **kwargs):
        patient = self.filter_queryset(self.get_queryset()) #ده السطر الوحيد اللي جديد في الدالة
        pat_serial = PatSer(patient,many=True)

        patients = Patients.objects.all()
        pat_non_appoint =patients.filter(appointments__isnull=True).distinct()
        pat_ser_non_app = PatNameSer(pat_non_appoint,many=True)
        total_amount = patients.aggregate(total=Sum('appointments__detect_value'))['total']or 0

        data = {'اجمالي عدد المرضي':patients.count(),
                'اجمالي المبلغ':total_amount,
                '=':'================================================',
                'عدد بدون حجز': pat_non_appoint.count(),
                'مرضي بدون حجز':pat_ser_non_app.data,
                '': '================================================',
                'عدد من قام بالحجز':patient.count(),
                'من قام بالحجز':pat_serial.data}
        return Response(data)

class Gener_patient_id(RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    queryset = Patients.objects.all()
    serializer_class = PatNameSer


class View_patient(ModelViewSet):
    queryset = Patients.objects.filter(appointments__isnull=False).distinct()
    serializer_class = PatNameSer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['pk', 'name']
    search_fields = ['name']
    filterset_fields = ['name']


    def list(self, request, *args, **kwargs):
        patient = self.filter_queryset(self.get_queryset())  # ده السطر الوحيد اللي جديد في الدالة
        pat_serial = PatSer(patient, many=True)

        patients = Patients.objects.all()
        pat_non_appoint = patients.filter(appointments__isnull=True).distinct()
        pat_ser_non_app = PatNameSer(pat_non_appoint, many=True)
        total_amount = patients.aggregate(total=Sum('appointments__detect_value'))['total'] or 0

        data = {'اجمالي عدد المرضي': patients.count(),
                'اجمالي المبلغ': total_amount,
                '=': '================================================',
                'عدد بدون حجز': pat_non_appoint.count(),
                'مرضي بدون حجز': pat_ser_non_app.data,
                '': '================================================',
                'عدد من قام بالحجز': patient.count(),
                'من قام بالحجز': pat_serial.data}
        return Response(data)










