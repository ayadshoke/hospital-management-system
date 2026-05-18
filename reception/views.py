from datetime import datetime,timedelta,date
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from departs.models import Appointments, Patients, Doctors, Days, Payment, Departments, Area
from django.db.models import Sum, Count, Avg, Q,Max
from django.contrib import messages
from django.utils import timezone
import datetime as dt
import pandas as pd
from django.contrib.auth.decorators import login_required
from shared.forms import PatientForm


@login_required
def appoint_list(request):
    doctors = Doctors.objects.values('id', 'name')
    patients = Patients.objects.values('id', 'name')
    al_days = Days.days
    from_date = request.POST.get('from')
    to_date = request.POST.get('to')
    look_for = request.POST.get('q')
    to_day = datetime.now().date()
    if look_for:
        appoints = Appointments.objects.filter(
                    Q(patient__name__icontains=look_for)|
                    Q(doctor__name__icontains=look_for))
    elif from_date and to_date:
        appoints = Appointments.objects.filter(created_at__range=[from_date, to_date])
    else:
        appoints = Appointments.objects.all()
        # appoints = Appointments.objects.filter(created_at__lt = to_day-timedelta(days=7),paid_stat=False)
    for x in appoints:
        diff = (to_day - x.created_at).days
        count = Appointments.objects.filter(patient=x.patient,paid_stat=True).count()
        if x.paid_stat == False and diff >=1:
            x.status = '3'
            x.save()
        if x.paid_stat == False and diff >= 2:
            x.delete()
        if x.paid_stat ==True and count == 1 and x.detect !='3' and diff >= 7 :
            x.status = '3'
            x.save()
    detect = []
    for i in Appointments.list:
        if i[0] != "3":
            detect.append(i)
    status = Appointments.detect_stat

    total_amount = appoints.filter(paid_stat=False).exclude(status='3').aggregate(total=Sum('detect_value'))['total']
    total_count = appoints.filter(paid_stat=False).exclude(status='3').aggregate(count=Count('pk'))['count']

    normal = appoints.filter(paid_stat=False,detect='1').exclude(status='3').aggregate(count=Count('pk'))['count']
    normal_amount = appoints.filter(paid_stat=False,detect='1').exclude(status='3').aggregate(total=Sum('detect_value'))['total']

    urgent = appoints.filter(paid_stat=False,detect='2').exclude(status='3').aggregate(count=Count('pk'))['count']
    urgent_amount = appoints.filter(paid_stat=False,detect='2').exclude(status='3').aggregate(total=Sum('detect_value'))['total']

    form = PatientForm()# علشان نضيف المريض من هنا
    day = dt.datetime.now().date()
    day_week = (day.weekday()+3) % 7 # علشان نجيب ترتيب اليوم داخل الاسبوع
    doc_day = Doctors.objects.filter(days__day=day_week,days__available=True)
    if doc_day == None:
        messages.error(request,'لا يوجد دكاتره متاحه اليوم')
        return redirect('appoint_list')
    print(day_week)
    area = Area.objects.all()

    context = {'appoints': appoints, 'doctors': doctors,'days':al_days,'patients': patients,'doc_day':doc_day,'day':day,
               'detects': detect, 'status': status,'total': total_amount, 'unpaid': total_count,'area':area,
               'form':form,'normal':normal,'urgent':urgent,'normal_amount':normal_amount,'urgent_amount':urgent_amount}
    return render(request, 'appoint_list.html', context)


@login_required
def add_appoint(request):
    qs = Appointments.objects.filter(paid_stat=True)
    to_day = timezone.now().date()
    diff = to_day - timedelta(days=7)
    new_detect = Appointments()
    if request.POST:
        day_number = (datetime.now().weekday() + 3) % 7  # للحصول علي رقم اليوم في الاسبوع
        patient_id = request.POST.get('patient')
        new_detect.patient = Patients.objects.get(id=patient_id)  # بيتم استدعاء ال class
        doc_id = request.POST.get('doctor')
        doc = Doctors.objects.get(id=doc_id)
        doc_day = Days.objects.filter(doctor = doc, day=day_number,available=True)
        if not doc_day:
            messages.error(request, f'  غير موجود اليوم {doc} الدكتور ')
            return redirect('appoint_list')
        else:
            new_detect.doctor = doc
        if qs.filter(patient=patient_id,created_at__gt = to_day-timedelta(days=7),doctor=doc_id) and new_detect.status != '3':
            new_detect.detect = '3'
            messages.success(request,'تمت الاستشارة')
        else:
            new_detect.detect = request.POST.get('detect')
            messages.success(request,'تم الحجز')
            # new_detect.save()
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
        return redirect('appoint_list')


@login_required
def update_appoint(request, pk):
    item = Appointments.objects.get(pk=pk)
    count = Appointments.objects.filter(patient=item.patient,paid_stat=False).count()
    if item.status != '1' or item.detect =='3'or item.paid_stat == True:
        messages.error(request, f'the detect number :{item.pk} status is:{item.get_status_display()}')
        return redirect('appoint_list')
    detect = []
    for i in sorted(Appointments.list):
        if i[0]!= "3":
            detect.append(i)
    docs = Doctors.objects.all().order_by('name')  # values_list('doc_name',flat=True).distinct()
    if request.POST:
        doc_id = request.POST.get('doctor')
        doc_name = docs.get(pk=doc_id)
        day_num = (datetime.now().weekday() + 3) % 7
        doc_day = Days.objects.filter(doctor=doc_name, day=day_num,available=True)
        if not doc_day:
            messages.error(request, f'the doctor {doc_name}  is not available in this day')
            return redirect('appoint_list')
        else:
            item.doctor = doc_name
        det = request.POST.get('detect')
        if det == '3':
            messages.error(request, 'لا يجوز تحويل الكشف الي استشاره')
            return redirect('appoint_list')
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
        messages.success(request, 'تم تحديث البيانات بنجاح')
        return redirect('appoint_list')
    appoints = Appointments.objects.all()
    context = {'item': item, 'appoints': appoints, 'doctors': docs, 'detects': detect,'pk':pk}
    return render(request, 'appoint_list.html', context)


def paid_appoint(request):
    part_id = request.POST.get('part')# دي جاي من depart_list
    part = None
    paid_app = Appointments.objects.filter(paid_stat=True)
    if part_id:
        part = Departments.objects.get(pk=part_id)
        paid_app = Appointments.objects.filter(paid_stat=True,doctor__part__id=part_id)

    nor_value=paid_app.aggregate(nor_amount=Sum('detect_value',filter=Q(detect='1')))['nor_amount']or 0
    nor_count=paid_app.filter(detect='1').aggregate(count=Count('detect_value'))['count']or 0

    ur_value=paid_app.filter(detect='2').aggregate(ur_amount=Sum('detect_value'))['ur_amount']or 0
    ur_count=paid_app.filter(detect='2').aggregate(ur_count=Count('detect_value'))['ur_count']or 0

    con_count=paid_app.filter(detect='3').aggregate(con_count=Count('detect_value'))['con_count']or 0

    tot_count=paid_app.aggregate(tot_count=Count('pk'))['tot_count']or 0
    tot_value=paid_app.aggregate(tot_amount=Sum('detect_value'))['tot_amount']or 0

    #download
    excel = request.GET.get('name')

    if excel == 'excel':
        df = pd.DataFrame(list(paid_app.values()))
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['content_Disposition'] = 'attachment;filename=paid_app.xlsx', df.to_excel(response, index=False)
        return response


    context = {'paid_app': paid_app,'part':part,'nor_value':nor_value,'nor_count':nor_count,'ur_value':ur_value,
               'ur_count':ur_count,'con_count':con_count,'tot_count':tot_count,'tot_value':tot_value}
    return render(request, 'paid_appoint.html', context)





