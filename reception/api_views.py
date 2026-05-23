from django.db.models import Sum
from datetime import datetime,timedelta,date
from rest_framework import status,filters,generics
from departs.models import Appointments,Patients,Days,Doctors
from .serializer import AppointSer,AddUpdate_appointSer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend



@api_view(['GET','POST'])
def get_appoint(request):
    if request.method == 'GET':
        to_day = datetime.now().date()
        appoints = Appointments.objects.all()
        un_paid = AppointSer(appoints.filter(paid_stat=False),many=True)
        paid = AppointSer(appoints.filter(paid_stat=True),many=True)
        if not un_paid.data :
            return Response({'message':'لا يوجد كشوفات معلقة'})
        for x in appoints:
            diff = (to_day - x.created_at).days
            count = Appointments.objects.filter(patient=x.patient, paid_stat=True).count()
            if x.paid_stat == False and diff >= 1:
                x.status = '3'
                x.save()
            if x.paid_stat == False and diff >= 2:
                x.delete()
            if x.paid_stat == True and count == 1 and x.detect != '3' and diff >= 7:
                x.status = '3'
                x.save()

        data = {'اجمال عدد الكشف':appoints.count(),
                'اجمالي المبلغ':appoints.aggregate(amount=Sum('detect_value'))['amount']or 0,
                'عدد المسدد':appoints.filter(paid_stat=True).count(),
                'مبلغ المسدد':appoints.filter(paid_stat=True).aggregate(amount=Sum('detect_value'))['amount']or 0,
                'عدد الغير مسدد': appoints.filter(paid_stat=False).count(),
                'مبلغ الغير مسدد':appoints.filter(paid_stat=False).aggregate(amount=Sum('detect_value'))['amount']or 0,
                'الحجز':un_paid.data,
                '*':'---------------------------------------------------------',
                'الكشوفات المسدده':paid.data}

        return Response(data,status=status.HTTP_200_OK)

    # if request.method == 'POST':
    #     serializer = AppointSer(data=request.data)
    #     if not request.data :  # لازم تستخد بالشكل ده
    #         return Response({'message':'يجب ادخال البيانات الحقول الزامية'},status=400)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data,status=201)
    #     return Response(serializer.errors,status=400)

    # دي شكل تاني لدلة ده شغل احترافي POST
    if request.method == 'POST':
        to_day = datetime.now().date()
        qs = Appointments.objects.filter(paid_stat=True)
        day_number = (datetime.now().weekday() + 3) % 7
        new_detect = Appointments()
        pat_id = request.POST.get('patient')
        if pat_id is None :
            return Response({'message':'المريض غير مدرج علي قاعدة البيانات'})

        new_detect.patient = Patients.objects.get(id=pat_id)
        doc_id = request.POST.get('doctor')
        doctor = Doctors.objects.get(id=doc_id)
        doc_day = Days.objects.filter(doctor=doctor,day=day_number,available=True)
        if not doc_day:
            return Response({'message':f'doctor {doctor} not available to day'})
        else:
            new_detect.doctor = doctor
        if qs.filter(patient=pat_id,created_at__gt = to_day-timedelta(days=7),doctor=doc_id) and new_detect.status != '3':
            new_detect.detect = '3'
            return Response({'message':'تمت الاستشارة'})
        else:
            new_detect.detect = request.POST.get('detect')

        if new_detect.detect == '1':
            detect_value = 70
        elif new_detect.detect == '2':
            detect_value = 200
        else:
            detect_value = 0
        new_detect.detect_value = detect_value
        new_detect.employee = request.user
        new_detect.save()
        if new_detect.detect == '1' or new_detect.detect == '2':
            new_detect.status = '1'
        else:
            new_detect.status = '2'
        new_detect.save()

        serializer = AppointSer(data=new_detect)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


@api_view(['GET','PUT','PATCH','DELETE'])
def get_appoint_pk(request,id):
    item = Appointments.objects.get(pk=id)
    if request.method == 'GET':
        serializer = AppointSer(instance=item)

        data ={'item':item.patient.name,'data':serializer.data}
        return Response(data,status=200)

    if request.method == 'PUT':
        docs = Doctors.objects.all().order_by('name')
        if item.status != '1' or item.detect == '3' or item.paid_stat == True:
            return Response({'message':'لا يجوز التعديل الشكف مدفوع'})
        doc_id = request.POST.get('doctor')
        doc_name = docs.get(pk=doc_id)
        day_num = (datetime.now().weekday() + 3) % 7
        doc_day = Days.objects.filter(doctor=doc_name, day=day_num, available=True)
        if not doc_day:
            return Response({'message':f'doctor {doc_name} not available to day'})
        else:
            item.doctor = doc_name
        det = request.POST.get('detect')
        if det == '3':
            return Response({'message':'لا يجوز تحويل الكشف الي استشاره'})
        else:
            item.detect = det
        item.save()
        if item.detect == '1':
            item.detect_value = 70
        elif item.detect == '2':
            item.detect_value = 200
        else:
            item.detect_value = 0
        item.save()
        serializer = AppointSer(instance=item,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data ={'message':'edited successfully','data':serializer.data}
        return Response(data,status=202)

    if request.method == 'DELETE':
        item.delete()
        return Response({'message':'item deleted'})

class all_appoints(APIView):
    def get(self,request):
        to_day = datetime.now().date()
        appoints = Appointments.objects.all()
        un_paid = AppointSer(appoints.filter(paid_stat=False), many=True)
        paid = AppointSer(appoints.filter(paid_stat=True), many=True)
        if not un_paid.data:
            return Response({'message': 'لا يوجد كشوفات معلقة'})
        for x in appoints:
            diff = (to_day - x.created_at).days
            count = Appointments.objects.filter(patient=x.patient, paid_stat=True).count()
            if x.paid_stat == False and diff >= 1:
                x.status = '3'
                x.save()
            if x.paid_stat == False and diff >= 2:
                x.delete()
            if x.paid_stat == True and count == 1 and x.detect != '3' and diff >= 7:
                x.status = '3'
                x.save()

        data = {'اجمال عدد الكشف': appoints.count(),
                'اجمالي المبلغ': appoints.aggregate(amount=Sum('detect_value'))['amount'] or 0,
                'عدد المسدد': appoints.filter(paid_stat=True).count(),
                'مبلغ المسدد': appoints.filter(paid_stat=True).aggregate(amount=Sum('detect_value'))['amount'] or 0,
                'عدد الغير مسدد': appoints.filter(paid_stat=False).count(),
                'مبلغ الغير مسدد': appoints.filter(paid_stat=False).aggregate(amount=Sum('detect_value'))[
                                       'amount'] or 0,
                'الحجز': un_paid.data,
                '*': '---------------------------------------------------------',
                'الكشوفات المسدده': paid.data}

        return Response(data, status=status.HTTP_200_OK)
    def post(self,request):
        to_day = datetime.now().date()
        qs = Appointments.objects.filter(paid_stat=True)
        day_number = (datetime.now().weekday() + 3) % 7
        new_detect = Appointments()
        pat_id = request.POST.get('patient')
        if pat_id is None:
            return Response({'message': 'المريض غير مدرج علي قاعدة البيانات'})

        new_detect.patient = Patients.objects.get(id=pat_id)
        doc_id = request.POST.get('doctor')
        doctor = Doctors.objects.get(id=doc_id)
        doc_day = Days.objects.filter(doctor=doctor, day=day_number, available=True)
        if not doc_day:
            return Response({'message': f'doctor {doctor} not available to day'})
        else:
            new_detect.doctor = doctor
        if qs.filter(patient=pat_id, created_at__gt=to_day - timedelta(days=7),
                     doctor=doc_id) and new_detect.status != '3':
            new_detect.detect = '3'
            return Response({'message': 'تمت الاستشارة'})
        else:
            new_detect.detect = request.POST.get('detect')

        if new_detect.detect == '1':
            detect_value = 70
        elif new_detect.detect == '2':
            detect_value = 200
        else:
            detect_value = 0
        new_detect.detect_value = detect_value
        new_detect.employee = request.user
        new_detect.save()
        if new_detect.detect == '1' or new_detect.detect == '2':
            new_detect.status = '1'
        else:
            new_detect.status = '2'
        new_detect.save()

        serializer = AppointSer(data=new_detect)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class all_appoints_Pk(APIView):
    def get(self,request,id):
        item = Appointments.objects.get(pk=id)
        serializer = AppointSer(instance=item)

        data = {'item': item.patient.name, 'data': serializer.data}
        return Response(data, status=200)
    def put(self,request,id):
        item = Appointments.objects.get(pk=id,paid_stat=True)
        docs = Doctors.objects.all().order_by('name')
        if item.status != '1' or item.detect == '3' or item.paid_stat == True:
            return Response({'message': 'لا يجوز التعديل الشكف مدفوع'})
        doc_id = request.POST.get('doctor')
        doc_name = docs.get(pk=doc_id)
        day_num = (datetime.now().weekday() + 3) % 7
        doc_day = Days.objects.filter(doctor=doc_name, day=day_num, available=True)
        if not doc_day:
            return Response({'message': f'doctor {doc_name} not available to day'})
        else:
            item.doctor = doc_name
        det = request.POST.get('detect')
        if det == '3':
            return Response({'message':'لا يجوز تحويل الكشف الي استشاره'})
        else:
            item.detect = det
        item.save()
        if item.detect == '1':
            item.detect_value = 70
        elif item.detect == '2':
            item.detect_value = 200
        else:
            item.detect_value = 0
        item.save()
        serializer = AppointSer(instance=item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'edited successfully', 'data': serializer.data}
        return Response(data, status=202)



"""النوع الثالث"""
class Gener_app(generics.ListCreateAPIView):
    queryset = Appointments.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['patient', 'created_at']
    ordering_fields = ['pk', 'patient']
    filterset_fields = ['created_at', 'detect', 'status']

    # السيريلزر يتغير حسب نوع الريكويست
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddUpdate_appointSer
        return AppointSer
    # ===================== GET =====================
    def list(self, request, *args, **kwargs):
        appoints = self.get_queryset()
        to_day = datetime.now().date()
        un_paid = AppointSer(appoints.filter(paid_stat=False),many=True)
        paid = AppointSer(appoints.filter(paid_stat=True),many=True)
        if not un_paid.data:
            return Response({'message': 'لا يوجد كشوفات معلقة'})
        for x in appoints:
            diff = (to_day - x.created_at).days
            count = Appointments.objects.filter(patient=x.patient,paid_stat=True).count()
            if x.paid_stat == False and diff >= 1:
                x.status = '3'
                x.save()
            if x.paid_stat == False and diff >= 2:
                x.delete()
            if x.paid_stat == True and count == 1 and x.detect != '3'and diff >= 7:
                x.status = '3'
                x.save()
        data = {'اجمال عدد الكشف': appoints.count(),
            'اجمالي المبلغ':appoints.aggregate(amount=Sum('detect_value'))['amount'] or 0,
            'عدد المسدد':appoints.filter(paid_stat=True).count(),'مبلغ المسدد':appoints.filter(paid_stat=True).aggregate(amount=Sum('detect_value'))['amount'] or 0,
            'عدد الغير مسدد':appoints.filter(paid_stat=False).count(),
            'مبلغ الغير مسدد':
                appoints.filter(paid_stat=False).aggregate(amount=Sum('detect_value'))['amount'] or 0,
            'الحجز': un_paid.data,
            '*': '--------------------------------',
            'الكشوفات المسدده': paid.data}
        return Response(data, status=status.HTTP_200_OK)

    # ===================== POST =====================
    def create(self, request, *args, **kwargs):
        new_detect = Appointments()
        to_day = datetime.now().date()
        qs = Appointments.objects.filter(paid_stat=True)
        day_number = (datetime.now().weekday() + 3) % 7
        pat_id = request.POST.get('patient')
        if pat_id is None:
            return Response({'message': 'المريض غير مدرج علي قاعدة البيانات'})
        new_detect.patient = Patients.objects.get(id=pat_id)
        doc_id = request.POST.get('doctor')
        doctor = Doctors.objects.get(id=doc_id)
        doc_day = Days.objects.filter(doctor=doctor,day=day_number,available=True)
        if not doc_day:
            return Response({'message': f'doctor {doctor} not available today'})
        new_detect.doctor = doctor
        if qs.filter(patient=pat_id,created_at__gt=to_day - timedelta(days=7),doctor=doc_id) and new_detect.status != '3':
            new_detect.detect = '3'
            return Response({'message': 'تمت الاستشارة'})
        else:
            new_detect.detect = request.POST.get('detect')
        if new_detect.detect == '1':
            detect_value = 70
        elif new_detect.detect == '2':
            detect_value = 200
        else:
            detect_value = 0
        new_detect.detect_value = detect_value
        new_detect.employee = request.user
        if new_detect.detect in ['1', '2']:
            new_detect.status = '1'
        else:
            new_detect.status = '2'
        new_detect.save()
        serializer = AppointSer(new_detect)
        return Response({'message': 'تمت الاضافة بنجاح','data': serializer.data},status=status.HTTP_201_CREATED)


class Gener_app_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointments.objects.all()
    serializer_class = AddUpdate_appointSer
    def update(self, request, *args, **kwargs):
        item = self.get_object()
        if item.paid_stat is True :
            return Response({'message':' لا يجوز التعديل الكشف مسدد '})

        if item.status != '1'or item.detect == '3':
            return Response({'message': f' {item.get_detect_display()} {item.get_status_display()} لا يجوز التعديل الكشف      :   '})
        serializer = AddUpdate_appointSer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        doc_id = request.data.get('doctor')
        doctor = Doctors.objects.get(pk=doc_id)
        day_num = (datetime.now().weekday() + 3) % 7
        doc_day = Days.objects.filter(doctor=doctor,day=day_num,available=True)
        if not doc_day:
            return Response({'message':f'doctor {doctor} not available today'})
        det = request.data.get('detect')
        if det == '3':
            return Response({ 'message':'لا يجوز تحويل الكشف الي استشارة' })
        item = serializer.save(doctor=doctor)
        # حساب قيمة الكشف
        if item.detect == '1':
            item.detect_value = 70
        elif item.detect == '2':
            item.detect_value = 200
        else:
            item.detect_value = 0
        item.save()
        response_serializer = AppointSer(item)
        return Response({'message': 'edited successfully','data': response_serializer.data}, status=202)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        if item.paid_stat is True:
            return Response({'message': ' لا يجوز الحذف الكشف مسدد '})
        else:
            item.delete()
            return Response({'message': ' تم الحذف للكشف  '})



"""النوع الرابع   ViewsSetModel"""
class View_appoint(ModelViewSet):
    queryset = Appointments.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['patient', 'created_at']
    ordering_fields = ['pk', 'patient']
    filterset_fields = ['created_at', 'detect', 'status']

    # السيريلزر يتغير حسب نوع الريكويست
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return AddUpdate_appointSer
        return AppointSer

    # ===================== GET =====================
    def list(self, request, *args, **kwargs):
        appoints = self.get_queryset()
        to_day = datetime.now().date()
        un_paid = AppointSer(appoints.filter(paid_stat=False), many=True)
        paid = AppointSer(appoints.filter(paid_stat=True), many=True)
        if not un_paid.data:
            return Response({'message': 'لا يوجد كشوفات معلقة'})
        for x in appoints:
            diff = (to_day - x.created_at).days
            count = Appointments.objects.filter(patient=x.patient, paid_stat=True).count()
            if x.paid_stat == False and diff >= 1:
                x.status = '3'
                x.save()
            if x.paid_stat == False and diff >= 2:
                x.delete()
            if x.paid_stat == True and count == 1 and x.detect != '3' and diff >= 7:
                x.status = '3'
                x.save()
        data = {'اجمال عدد الكشف': appoints.count(),
                'اجمالي المبلغ': appoints.aggregate(amount=Sum('detect_value'))['amount'] or 0,
                'عدد المسدد': appoints.filter(paid_stat=True).count(),
                'مبلغ المسدد': appoints.filter(paid_stat=True).aggregate(amount=Sum('detect_value'))['amount'] or 0,
                'عدد الغير مسدد': appoints.filter(paid_stat=False).count(),
                'مبلغ الغير مسدد':
                    appoints.filter(paid_stat=False).aggregate(amount=Sum('detect_value'))['amount'] or 0,
                'الحجز': un_paid.data,
                '*': '--------------------------------',
                'الكشوفات المسدده': paid.data}
        return Response(data, status=status.HTTP_200_OK)

    # ===================== POST =====================
    def create(self, request, *args, **kwargs):
        new_detect = Appointments()
        to_day = datetime.now().date()
        qs = Appointments.objects.filter(paid_stat=True)
        day_number = (datetime.now().weekday() + 3) % 7
        pat_id = request.POST.get('patient')
        if pat_id is None:
            return Response({'message': 'المريض غير مدرج علي قاعدة البيانات'})
        new_detect.patient = Patients.objects.get(id=pat_id)
        doc_id = request.POST.get('doctor')
        doctor = Doctors.objects.get(id=doc_id)
        doc_day = Days.objects.filter(doctor=doctor, day=day_number, available=True)
        if not doc_day:
            return Response({'message': f'doctor {doctor} not available today'})
        new_detect.doctor = doctor
        if qs.filter(patient=pat_id, created_at__gt=to_day - timedelta(days=7),
                     doctor=doc_id) and new_detect.status != '3':
            new_detect.detect = '3'
            return Response({'message': 'تمت الاستشارة'})
        else:
            new_detect.detect = request.POST.get('detect')
        if new_detect.detect == '1':
            detect_value = 70
        elif new_detect.detect == '2':
            detect_value = 200
        else:
            detect_value = 0
        new_detect.detect_value = detect_value
        new_detect.employee = request.user
        if new_detect.detect in ['1', '2']:
            new_detect.status = '1'
        else:
            new_detect.status = '2'
        new_detect.save()
        serializer = AppointSer(new_detect)
        return Response({'message': 'تمت الاضافة بنجاح', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    # ===================== POST =====================

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        if item.paid_stat is True :
            return Response({'message':' لا يجوز التعديل الكشف مسدد '})

        if item.status != '1'or item.detect == '3':
            return Response({'message': f' {item.get_detect_display()} {item.get_status_display()} لا يجوز التعديل الكشف      :   '})
        serializer = AddUpdate_appointSer(instance=item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        doc_id = request.data.get('doctor')
        doctor = Doctors.objects.get(pk=doc_id)
        day_num = (datetime.now().weekday() + 3) % 7
        doc_day = Days.objects.filter(doctor=doctor,day=day_num,available=True).exists()
        if not doc_day:
            return Response({'message':f'doctor {doctor} not available today'})
        det = request.data.get('detect')
        if det == '3':
            return Response({ 'message':'لا يجوز تحويل الكشف الي استشارة' })
        item = serializer.save(doctor=doctor)
        # حساب قيمة الكشف
        if item.detect == '1':
            item.detect_value = 70
        elif item.detect == '2':
            item.detect_value = 200
        else:
            item.detect_value = 0
        item.save()
        response_serializer = AppointSer(item)
        return Response({'message': 'edited successfully','data': response_serializer.data}, status=202)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if item.paid_stat is True:
            return Response({'message': ' لا يجوز الحذف الكشف مسدد '})
        else:
            item.delete()
            return Response({'message': ' تم الحذف للكشف  '})


























































































































# class Gener_app(generics.ListAPIView):
#     queryset = Appointments.objects.all()
#     serializer_class = AppointSer
#     filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
#     search_fields = ['patient','created_at']
#     ordering_fields =['pk','patient']
#     filterset_fields =['created_at','detect','status']
#
#     def list(self, request, *args, **kwargs):
#         appoints = self.get_queryset()
#         to_day = datetime.now().date()
#         un_paid = AppointSer(appoints.filter(paid_stat=False), many=True)
#         paid = AppointSer(appoints.filter(paid_stat=True), many=True)
#         if not un_paid.data:
#             return Response({'message': 'لا يوجد كشوفات معلقة'})
#         for x in appoints:
#             diff = (to_day - x.created_at).days
#             count = Appointments.objects.filter(patient=x.patient, paid_stat=True).count()
#             if x.paid_stat == False and diff >= 1:
#                 x.status = '3'
#                 x.save()
#             if x.paid_stat == False and diff >= 2:
#                 x.delete()
#             if x.paid_stat == True and count == 1 and x.detect != '3' and diff >= 7:
#                 x.status = '3'
#                 x.save()
#
#         data = {'اجمال عدد الكشف': appoints.count(),
#                 'اجمالي المبلغ': appoints.aggregate(amount=Sum('detect_value'))['amount'] or 0,
#                 'عدد المسدد': appoints.filter(paid_stat=True).count(),
#                 'مبلغ المسدد': appoints.filter(paid_stat=True).aggregate(amount=Sum('detect_value'))['amount'] or 0,
#                 'عدد الغير مسدد': appoints.filter(paid_stat=False).count(),
#                 'مبلغ الغير مسدد': appoints.filter(paid_stat=False).aggregate(amount=Sum('detect_value'))[
#                                        'amount'] or 0,
#                 'الحجز': un_paid.data,
#                 '*': '---------------------------------------------------------',
#                 'الكشوفات المسدده': paid.data}
#
#         return Response(data, status=status.HTTP_200_OK)
#
# class Create_app(generics.CreateAPIView):
#     queryset = Appointments.objects.all()
#     serializer_class = AddUpdate_appointSer
#     def post(self, request, *args, **kwargs):
#         new_detect = Appointments()
#         to_day = datetime.now().date()
#         qs = Appointments.objects.filter(paid_stat=True)
#         day_number = (datetime.now().weekday() + 3) % 7
#         pat_id = request.POST.get('patient')
#         if pat_id is None:
#             return Response({'message': 'المريض غير مدرج علي قاعدة البيانات'})
#         new_detect.patient = Patients.objects.get(id=pat_id)
#         doc_id = request.POST.get('doctor')
#         doctor = Doctors.objects.get(id=doc_id)
#         doc_day = Days.objects.filter(doctor=doctor,day=day_number,available=True)
#         if not doc_day:
#             return Response({'message': f'doctor {doctor} not available today'})
#         new_detect.doctor = doctor
#         if qs.filter(patient=pat_id,created_at__gt=to_day - timedelta(days=7),doctor=doc_id) and new_detect.status != '3':
#             new_detect.detect = '3'
#             return Response({'message': 'تمت الاستشارة'})
#         else:
#             new_detect.detect = request.POST.get('detect')
#         if new_detect.detect == '1':
#             detect_value = 70
#         elif new_detect.detect == '2':
#             detect_value = 200
#         else:
#             detect_value = 0
#         new_detect.detect_value = detect_value
#         new_detect.employee = request.user
#         if new_detect.detect in ['1', '2']:
#             new_detect.status = '1'
#         else:
#             new_detect.status = '2'
#         new_detect.save()
#         serializer = AppointSer(new_detect)
#         return Response({'message':'تمت الاضافة بنجاح','data':serializer.data},status=status.HTTP_201_CREATED)