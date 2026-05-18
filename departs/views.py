from itertools import groupby
from operator import attrgetter

from django.shortcuts import render, redirect
from .models import Departments, Doctors, Appointments, Patients,Payment
from shared.forms import DepartForm,DocForm
from django.contrib import messages
from django.db.models import Count,Sum
from django.contrib.auth.decorators import login_required


def show_depart(request):
    look_for = request.GET.get('num_floor')
    depart_list = Departments.specialization
    floors = Departments.floors
    if request.POST:
        Departments.objects.create(
            name=request.POST.get('depart'),
            floor= request.POST.get('floor'),
            phone=request.POST.get('phone'))
        return redirect('depart')
    if look_for:
        department = Departments.objects.filter(floor=look_for,doctors__isnull=False)
    else:
        department = Departments.objects.filter(doctors__isnull=False)

    all_count = []
    for dep in department:
        dep.doc = Doctors.objects.filter(part=dep).count()or 0
        dep.pat = Patients.objects.filter(appointments__doctor__part=dep,appointments__paid_stat=True).distinct().count()or 0
        dep.amount =Payment.objects.filter(appoint__doctor__part=dep).aggregate(value=Sum('amount'))['value']or 0
        dep.detects =Appointments.objects.filter(doctor__part=dep,paid_stat=True).aggregate(t_count=Count('detect'))['t_count']or 0

        all_count.append(dep.doc)
    all = sum(all_count)
    counts = Departments.objects.exclude(doctors__isnull=True).distinct().count()
    cases = Patients.objects.filter(appointments__paid_stat=True).count() #هام جدددددا
    pats = Patients.objects.filter(appointments__paid_stat=True).distinct().count() #هام جدددددا
    amount = Appointments.objects.filter(paid_stat=True).aggregate(sum=Sum('detect_value'))['sum']or 0
    show_add = 'add' in request.GET

    context = {'departs': department,'list':depart_list,'floors':floors,'pats':pats,
               'show_add':show_add,'sum':all,'count':counts,'cases':cases,'amount':amount}
    return render(request, 'depart_list.html', context)


@login_required
def update_depart(request , slug):
    change_depart = Departments.objects.get(pk = slug)
    if request.POST:
        form = DepartForm(request.POST , instance=change_depart)
        if form.is_valid():
            form.save()
            messages.success(request, 'updated successfully')
            return redirect('depart')
    else:
        form = DepartForm(instance=change_depart)
    context = {'form':form}
    return render(request ,'add_update.html',context)



@login_required
def delete_depart(request ,slug):
    depart_delete = Departments.objects.get(pk=slug)
    if request.POST:
        depart_delete.delete()
        messages.success(request, 'deleted successfully')
        return redirect('depart')
    context = {'obj':depart_delete}
    return render(request ,'delete_obj.html',context)




@login_required
def view_doctor(request , slug):
    depart = Departments.objects.prefetch_related('doctors_set__part').get(pk =slug)
    doctors = depart.doctors_set.all()
    context ={'doctors':doctors,'depart':depart}
    return render(request,'depart_doctor.html',context)



def part_no_work(request):
    depart_list = Departments.specialization
    floors = Departments.floors
    department = Departments.objects.filter(doctors__isnull=True)

    for dep in department:
        dep.count = Doctors.objects.filter(part=dep).count()

    count = Departments.objects.prefetch_related('doctors_set').exclude(doctors__isnull=False).distinct().count()
    show_table = 'add' in request.GET

    context = {'departs': department, 'list': depart_list, 'floors': floors,
               'show_table': show_table, 'count': count}
    return render(request, 'depart_list.html', context)


def part_cases(request,slug):
    part = Departments.objects.get(pk=slug)
    # qs = Patients.objects.filter(appointments__isnull=False,appointments__detect='1').order_by('id').distinct()
    qs = Appointments.objects.filter(doctor__part__id=slug).select_related('patient').order_by('patient','created_at')
    # مع select_related بنكتب اسم الحقل فقط وليس اسم الموديل وبدون set وليس اسم العلاقة
    grouped = groupby(qs,key=attrgetter('patient'))# وممكن نكتب كده key=lambda x:x.patient

    context = {'patients':grouped,'id':slug,'part':part}
    return render(request,'depart_list.html', context)












# qs = Appointments.objects.filter(doctor__part__id=slug,paid_stat=True).order_by('patient','created_at').distinct('patient')
# counts = Departments.objects.prefetch_related('doctors_set').exclude(doctors__isnull=True).distinct().count()


