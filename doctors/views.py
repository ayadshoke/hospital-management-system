from django.shortcuts import render, redirect
from departs.models import Departments, Doctors,Payment, Area,Appointments
from shared.forms import DocForm,DayForm
from django.contrib import messages
from django.db.models import Sum,Count,Q,OuterRef,Subquery
from django.contrib.auth.decorators import login_required
import datetime as dt


def doc_list(request):
    depart_list = Departments.objects.all()
    area =Area.objects.all()
    look_for = request.GET.get('q')
    ser_doc = request.GET.get('search_doc')# دي من صفحة البحث
    if look_for :
        doc = Doctors.objects.filter(name__icontains=look_for)
    elif ser_doc:
        doc = Doctors.objects.filter(pk=ser_doc)
    else:
        doc = Doctors.objects.all()
    apps = Appointments.objects.filter(paid_stat=True)
    for d in doc:
        d.count = apps.filter(doctor=d).count()
        d.amount = Payment.objects.filter(appoint__doctor=d).aggregate(total=Sum('amount'))['total']or 0
    tt = apps.aggregate(total=Sum('detect_value'))['total']
    if request.POST:
        part_id = request.POST.get('depart')
        part_name = Departments.objects.get(id=part_id)  # هنا تم استدعاء ال object من class department

        if request.user.is_authenticated:
             Doctors.objects.create(
                name=request.POST.get('name'),
                part= part_name,
                phone=request.POST.get('phone'),
                email=request.POST.get('email'),
                address=request.POST.get('area')),
        messages.success(request,'Added successfully')
    context = {'docs':doc,'areas':area,'depart':depart_list,
               'type':'dddd','total':tt,'ap':apps}
    return render(request,'doc_list.html',context)


@login_required
def doc_update(request, pk):
    item = Doctors.objects.get(pk = pk)
    if request.POST:
        form = DocForm(request.POST,instance=item)
        if form.is_valid():
            form.save()
            return redirect('doc_list')
    else:
        form = DocForm(instance=item)
    context = {'form':form,}
    return render(request ,'add_update.html',context)


@login_required
def doc_delete(request, pk):
    item = Doctors.objects.get(pk=pk)
    if request.POST:
        item.delete()
        return redirect('doc_list')
    context = {'obj':item}
    return render(request, 'delete_obj.html', context)


@login_required
def doc_case(request , pk):
    From = request.POST.get('from')
    TO = request.POST.get('to')
    doc = Doctors.objects.get(pk=pk)
    data = Appointments.objects.filter(doctor=doc,paid_stat=True)
    if From and TO:
        data = data.filter(created_at__range=[From,TO])
    total_row = 0
    for m in data:
        total_row += m.detect_value or 0
        m.running_total = total_row  # هنا بالطريقة دي علشان m كائن object
    tot_value = data.aggregate(total=Sum('detect_value'))['total']

    context = {'cases':data,'doctor':doc,'total':tot_value,'pk':pk}
    return render(request ,'doc_cases.html',context)


@login_required
def amount_cases(request,pk):
    form = request.POST.get('from')
    to = request.POST.get('to')
    doc = Doctors.objects.get(pk=pk)
    doc_payment = Payment.objects.filter(appoint__doctor=doc)
    if form and to:
        payment = doc_payment.filter(paid_date__range=[form,to])
    else:
        payment = doc_payment
    TotalDay = 0
    tot_row = payment.values('paid_date').annotate(
        total_count=Count('appoint',distinct=True),
        total_amount=Sum('amount')).order_by('paid_date')
    for date in tot_row:
        TotalDay += date['total_amount']or 0
        date['running_total'] = TotalDay # هنا اتعملت كده علشان date dictionary مش object

    general_count = payment.aggregate(count=Count('appoint',distinct=True))['count']or 0
    general_total = payment.aggregate(total=Sum('amount'))['total']or 0

    context = {'cases':tot_row,'total':general_total,'count':general_count}
    return render(request,'amount_cases.html',context)




