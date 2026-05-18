import calendar
from calendar import firstweekday

from django.contrib.auth.models import Permission
from django.utils import timezone
from django.db.models import Sum,Q,Count
from django.shortcuts import render,redirect
from departs.models import Patients, Appointments,Doctors,Area
from shared.forms import PatientForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
# Create your views here.

#لتامين دالة الحذف
def safe_perm_dynamic(func):
    def wrapper(request,codename,*args,**kwargs):
        perm = Permission.objects.filter(codename=kwargs.get('codename')).first()
        # if perm and request.user.has_perm(f'{perm.content_type.app_label}{codename}'):
        #     return func(request, codename, *args, **kwargs)
        # if not perm:
        return func(request, codename, *args, **kwargs)
    return wrapper





@login_required
def patient_list(request):
    look_for = request.POST.get('q')
    if look_for:
        patients = Patients.objects.filter(Q(name__icontains=look_for))#|Q(area__icintains=look_for))
    else:
        patients = Patients.objects.all()
    for p in patients:
        p.count = Appointments.objects.filter(patient=p,paid_stat=True).exclude(detect='3').count()
        p.amount = Appointments.objects.filter(patient=p,paid_stat=True).exclude(detect='3').aggregate(total=Sum('detect_value'))['total']
    form = PatientForm()
    show_add = 'add' in request.GET
    context = {'patients':patients,'form':form,'show_add':show_add}
    return render(request,'patient_list.html',context)


@login_required
def Add_patient(request):
    if not request.user.has_perm('departs.can_add_patient'):
        messages.error(request,'المستخدم لا يمتلك الصلاحية')
        # raise PermissionDenied
        return redirect('patient_list')
    if request.POST:
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appoint_list')

@login_required
def update_patient(request , slug):
    if not request.user.has_perm('departs.can_edit_patient'):
        messages.error(request,'المستخدم لا يمتلك الصلاحية')
        # raise PermissionDenied
        return redirect('patient_list')
    item = Patients.objects.get(pk =slug )
    if request.POST:
        form = PatientForm(request.POST,instance=item)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm(instance=item)

    patients = Patients.objects.all() # السطر علشان الجدول يظهر لما نعمل update
    context = {'form': form,'patients':patients,'update_id':slug} # وهنا برجع slug علشان نميز الطلب ده اللي فوق مع الطلب في الدالة
    return render(request, 'patient_list.html', context)


# @permission_required('departs.can_delete_patient',raise_exception=True)
@safe_perm_dynamic
def delete_patient(request , slug):
    item = Patients.objects.get(pk =slug )
    if request.POST:
            item.delete()
            messages.success(request, 'تم الحذف بنجاح')
            return redirect('patient_list')
    context = {'obj': item}
    return render(request, 'delete_obj.html', context)


#دي طريقة تانية
# if not request.user.has_perm('departs.can_delete_patient'):
    #     messages.error(request,'المستخدم لا يمتلك الصلاحية')
        # raise PermissionDenied
        # return redirect('patient_list')



@login_required
def patient_details(request,slug):
    patients = Patients.objects.all()
    pat = Patients.objects.prefetch_related('appointments_set__patient').get(pk=slug)
    pat_details = pat.appointments_set.filter(paid_stat=True)

    context = {'pat_details':pat_details,'patients':patients,'pat':pat}
    return render(request,'patient_list.html',context)


def general_search(request):
    docs = Doctors.objects.values('id','name').order_by('name')
    appoints =Appointments.objects.all()
    search_type = request.POST.get('search_type')
    q = request.POST.get('query')
    q_date = request.POST.get('query_date')
    if search_type =='slug' and q:
        item = appoints.filter(pk=q)
        if not item :
            messages.error(request,f'بيانات  {search_type} {q}  غير موجوده ')
            return redirect('general_search')

    elif search_type =='patient' and q:
        item = appoints.filter(Q(patient__name__icontains=q))
        if not item :
            messages.error(request,f'بيانات  {search_type} {q}  غير موجوده ')
            return redirect('general_search')

    elif search_type =='doctor' and q:
        item = appoints.filter(Q(doctor__name__icontains=q))
        if not item :
            messages.error(request,f'بيانات  {search_type} {q}  غير موجوده ')
            return redirect('general_search')

    elif search_type =='depart' and q:
        item = appoints.filter(doctor__part__name__icontains=q)
        if not item :
            messages.error(request,f'بيانات  {search_type} {q}  غير موجوده ')
            return redirect('general_search')


    elif search_type =='employee' and q:
        item = appoints.filter(Q(employee__username__icontains=q))
        if not item :
            messages.error(request,f'بيانات  {search_type} {q}  غير موجوده ')
            return redirect('general_search')

    elif search_type =='date' and q_date:
        item = appoints.filter(Q(created_at=q_date))
        if not item :
            messages.error(request,f'بيانات  {search_type} {q_date}  غير موجوده ')
            return redirect('general_search')

    else:
        item = None

    to_day = timezone.now().date()
    month = int(request.GET.get('month',to_day.month))
    year = int(request.GET.get('year',to_day.month))
    if year < 1000 :
        year = to_day.year

    # عمل زرار التالي للشهر
    next_month = month + 1
    next_year = year + 1
    if next_month > 12 :
        next_month = 1
        next_year += 1

    # التاريخ الحالي
    current_month = calendar.month_name[month]
    week_days = list(calendar.day_name)

    # الشهر السابق
    prev_month = month-1
    prev_year = year - 1
    if prev_month < 1 :
        prev_month = 12
        prev_year -= 1

    cal = calendar.Calendar(firstweekday=6)
    month_day = cal.monthdayscalendar(year, month)

    context = {'appoints':item,'docs':docs,'cal':month_day,'to_day':to_day,'month':month,'year':year,
              'next_month':next_month,'next_year':next_year,'current_month':current_month,'day_name':week_days,
               'prev_month':prev_month,'prev_year':prev_year}
    return render(request,'g_search.html',context)

