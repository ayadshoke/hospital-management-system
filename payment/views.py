from datetime import datetime,timedelta,date
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from departs.models import Appointments, Patients, Doctors, Days,Payment,Departments
from django.db.models.functions import Coalesce  # علشان القيم ما تطلعش none
from django.db.models import Sum, Count, Avg, Q,Max
from django.contrib import messages
from decimal import Decimal
from num2words import num2words
from django.contrib.auth.decorators import login_required
import pandas as pd


def cash_view(request):
    order = request.GET.get('order', 'created_at')
    date_pay = datetime.now()
    day = datetime.now().date()
    qs = Payment.objects.all()
    count_patient = qs.filter(paid_date=date_pay).values_list('appoint__id',flat=True).distinct().count()
    count = qs.filter(paid_date=date_pay).aggregate(count=Count('amount'))['count']or 0
    amount = qs.filter(paid_date=date_pay).aggregate(amount=Sum('amount'))['amount']or 0

    last_num = Appointments.objects.aggregate(max=Coalesce(Max("pk",filter=Q(paid_stat=True)),0))['max']
    receipt_num = last_num + 1

    apps = Appointments.objects.filter(paid_stat = False).exclude(status='3').order_by(order)
    context = {'appoints':apps,'amount':amount,'date_pay':date_pay,'count':count,'num':receipt_num,
               'count2':count_patient,'day':day}
    return render(request,'payment_appoint.html',context)


@login_required
def payment_appoint(request,pk):
    with transaction.atomic():  #دي علشان قفل الصف
        item = Appointments.objects.select_for_update().get(pk=pk)
    method = Payment.payment_type
    if item.status =='3' or item.paid_stat == True:
        messages.error(request,f' the patient:'
        f' {item.patient} the status is :{item.get_status_display()}')
        return redirect('cash_view')
    if request.POST:
        methods = request.POST.getlist('method')
        amounts = request.POST.getlist('amount')
        tot_paid = Decimal(0)
        for amount in amounts:
            tot_paid+= Decimal(amount)
        if not methods or item.detect_value != tot_paid :
            messages.error(request,'يجب اختيار طريقة السداد والتاكد من صحة المبلغ')
            return redirect('cash_view')
        for m, a in zip(methods, amounts):
            Payment.objects.create(
                appoint = item,
                paid_type= m,
                amount =Decimal(a) )
        messages.success(request, 'تم السداد عملية ناجحه')
        item.paid_stat=True
        item.save()
        return redirect('cash_view')

    tafqeet = num2words(int(item.detect_value),lang='ar',)
    pounds = item.detect_value - int(item.detect_value)
    piasters = num2words(pounds,lang='ar')

    qs = Payment.objects.all()
    date_pay = datetime.now()
    # count = qs.filter(paid_date=date_pay).aggregate(count=Count('amount'))['count']
    # amount = qs.filter(paid_date=date_pay).aggregate(amount=Sum('amount'))['amount']

    total_amount = qs.filter(appoint=item).annotate(tt=Sum('amount'))
    # last_num = Appointments.objects.aggregate(max=Coalesce(Max("pk",filter=Q(paid_stat=True)),0))['max']
    count_paid = Appointments.objects.filter(paid_stat=True).count()
    receipt_num = count_paid + 1


    context={'item':item,'num':receipt_num,'method':method,'total':total_amount,'date_pay':date_pay,
        'tafqeet':tafqeet,'piasters':piasters}
    return render(request,'payment_appoint.html',context)


# ===================
@login_required
def payments(request):
    docs = Doctors.objects.values('id','name').order_by('name')
    detect_list = Appointments.list
    part = Departments.specialization
    st = Appointments.detect_stat
    rows = []
    part_id = request.POST.get('part_id')#دي جاية من depart_list.html
    depart =None
    doc = request.POST.get('doc')
    dep = request.POST.get('depart')
    det = request.POST.get('detect')
    det_st = request.POST.get('status')
    methods = Payment.payment_type

    paid = Payment.objects.all()
    amount_cash = paid.aggregate(cash1=Coalesce(Sum('amount',filter=Q(paid_type='cash')),Decimal(0)))['cash1']
    amount_visa = paid.aggregate(visa1=Coalesce(Sum('amount',filter=Q(paid_type='visa')),Decimal(0)))['visa1']
    amount_cheque = paid.aggregate(cheque1=Coalesce(Sum('amount',filter=Q(paid_type='cheque')),Decimal(0)))['cheque1']
    amount_bank = paid.aggregate(bank1=Coalesce(Sum('amount',filter=Q(paid_type='bank')),Decimal(0)))['bank1']
    qs = Appointments.objects.filter(paid_stat=True).prefetch_related('payment_set__appoint')

    if part_id :
        depart = Departments.objects.get(pk=part_id)
        qs = qs.filter(doctor__part__id = part_id)
        amount_cash = paid.filter(appoint__doctor__part__id=part_id).aggregate(cash1=Coalesce(Sum('amount', filter=Q(paid_type='cash')), Decimal(0)))['cash1']
        amount_visa = paid.filter(appoint__doctor__part__id=part_id).aggregate(visa1=Coalesce(Sum('amount', filter=Q(paid_type='visa')), Decimal(0)))['visa1']
        amount_cheque = paid.filter(appoint__doctor__part__id=part_id).aggregate(cheque1=Coalesce(Sum('amount', filter=Q(paid_type='cheque')), Decimal(0)))['cheque1']
        amount_bank = paid.filter(appoint__doctor__part__id=part_id).aggregate(bank1=Coalesce(Sum('amount', filter=Q(paid_type='bank')), Decimal(0)))['bank1']



    if doc :
        qs = qs.filter(doctor=doc)
        amount_cash = paid.filter(appoint__doctor=doc).aggregate(cash1=Coalesce(Sum('amount',filter=Q(paid_type='cash')), Decimal(0)))['cash1']
        amount_visa = paid.filter(appoint__doctor=doc).aggregate(visa1=Coalesce(Sum('amount',filter=Q(paid_type='visa')), Decimal(0)))['visa1']
        amount_cheque = paid.filter(appoint__doctor=doc).aggregate(cheque1=Coalesce(Sum('amount',filter=Q(paid_type='cheque')), Decimal(0)))['cheque1']
        amount_bank = paid.filter(appoint__doctor=doc).aggregate(bank1=Coalesce(Sum('amount',filter=Q(paid_type='bank')), Decimal(0)))['bank1']
    if dep :
        qs = qs.filter(doctor__part__name = dep)
        amount_cash = paid.filter(appoint__doctor__part__name=dep).aggregate(cash1=Coalesce(Sum('amount', filter=Q(paid_type='cash')), Decimal(0)))['cash1']
        amount_visa = paid.filter(appoint__doctor__part__name=dep).aggregate(visa1=Coalesce(Sum('amount', filter=Q(paid_type='visa')), Decimal(0)))['visa1']
        amount_cheque = paid.filter(appoint__doctor__part__name=dep).aggregate(cheque1=Coalesce(Sum('amount', filter=Q(paid_type='cheque')), Decimal(0)))['cheque1']
        amount_bank = paid.filter(appoint__doctor__part__name=dep).aggregate(bank1=Coalesce(Sum('amount', filter=Q(paid_type='bank')), Decimal(0)))['bank1']
    if det :
        qs = qs.filter(detect = det)
        amount_cash = paid.filter(appoint__detect=det).aggregate(cash1=Coalesce(Sum('amount', filter=Q(paid_type='cash')), Decimal(0)))['cash1']
        amount_visa = paid.filter(appoint__detect=det).aggregate(visa1=Coalesce(Sum('amount', filter=Q(paid_type='visa')), Decimal(0)))['visa1']
        amount_cheque = paid.filter(appoint__detect=det).aggregate(cheque1=Coalesce(Sum('amount', filter=Q(paid_type='cheque')), Decimal(0)))['cheque1']
        amount_bank = paid.filter(appoint__detect=det).aggregate(bank1=Coalesce(Sum('amount', filter=Q(paid_type='bank')), Decimal(0)))['bank1']
    if det_st:
        qs = qs.filter(status=det_st)
        amount_cash = paid.filter(appoint__status=det_st).aggregate(cash1=Coalesce(Sum('amount', filter=Q(paid_type='cash')), Decimal(0)))['cash1']
        amount_visa = paid.filter(appoint__status=det_st).aggregate(visa1=Coalesce(Sum('amount', filter=Q(paid_type='visa')), Decimal(0)))['visa1']
        amount_cheque = paid.filter(appoint__status=det_st).aggregate(cheque1=Coalesce(Sum('amount', filter=Q(paid_type='cheque')), Decimal(0)))['cheque1']
        amount_bank = paid.filter(appoint__status=det_st).aggregate(bank1=Coalesce(Sum('amount', filter=Q(paid_type='bank')), Decimal(0)))['bank1']
    for item in qs:
        cash = 0
        visa= 0
        cheque= 0
        bank = 0
        sum = 0
        date = None
        for p in item.payment_set.all():
            date = p.paid_date
            if p.paid_type=='cash':
                cash+=p.amount
            elif p.paid_type=='visa':
                visa+=p.amount
            elif p.paid_type=='cheque':
                cheque+=p.amount
            elif p.paid_type=='bank':
                bank+=p.amount
            sum += p.amount
        rows.append({
            'appoint':item,
            'cash':cash,
            'visa':visa,
            'cheque':cheque,
            'bank':bank,
            'sum':sum,
            'date':date})

    #download
    load = request.GET.get('name')
    if load =='excel':
        df = pd.DataFrame(rows)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['content_Disposition'] = 'attachment;filename=payment.xlsx', df.to_excel(response, index=False)
        return response


    tot_amount = qs.aggregate(amounts=Sum('detect_value'))['amounts']

    context = {'payment':rows,'methods':methods,'docs':docs,'st':st,'detect_list':detect_list,'part':part,'depart':depart,
               'tot_amount':tot_amount,'cash':amount_cash,'visa':amount_visa,'cheque':amount_cheque,'bank':amount_bank}
    return render(request, 'payments.html', context)





@login_required
def total_day(request):
    method=Payment.payment_type
    date = request.POST.get('date') # اللي جاي من amount_cases.html
    date_from = request.POST.get('from')
    date_to = request.POST.get('to')

    qs = Payment.objects.values('paid_date').annotate(
        num=Count('appoint',distinct=True),  #لمنع تكرار الميعاد
        cash=Coalesce(Sum('amount',filter=Q(paid_type='cash')),Decimal(0)),
        visa=Coalesce(Sum('amount',filter=Q(paid_type='visa')),Decimal(0)),
        cheque=Coalesce(Sum('amount',filter=Q(paid_type='cheque')),Decimal(0)),
        bank=Coalesce(Sum('amount',filter=Q(paid_type='bank')),Decimal(0)),
        the_count=Count('amount'),total_value=Sum('amount'),
            ).order_by('-paid_date')

    if date_from and date_to:
        qs = qs.filter(paid_date__range=[date_from,date_to])
    if date:
        qs = qs.filter(paid_date=date)

    count_cases = qs.aggregate(num=Count('appoint'))['num']
    count_receipts = qs.aggregate(count=Count('pk'))['count']

    cash = qs.filter(paid_type='cash').aggregate(cash=Coalesce(Sum('amount'),Decimal(0)))['cash']
    visa = qs.aggregate(visa=Coalesce(Sum('amount', filter=Q(paid_type='visa')),Decimal(0)))['visa']
    cheque = qs.aggregate(cheque=Coalesce(Sum('amount', filter=Q(paid_type='cheque')),Decimal(0)))['cheque']
    bank = qs.aggregate(bank=Coalesce(Sum('amount', filter=Q(paid_type='bank')),Decimal(0)))['bank']

    total_amount=qs.aggregate(total=Sum('amount'))['total']


    context = {'data':qs,'total':total_amount,'num':count_cases,'count':count_receipts,'method':method,
               'cash':cash,'visa':visa,'cheque':cheque,'bank':bank}
    return render(request,'total_day.html',context)


def paid(request,date):
    method = Payment.payment_type
    payment = Payment.objects.filter(paid_date=date).values('appoint__patient__name','paid_date').annotate(
        num=Count('appoint', distinct=True),  # لمنع تكرار الميعاد
        cash=Coalesce(Sum('amount', filter=Q(paid_type='cash')), Decimal(0)),
        visa=Coalesce(Sum('amount', filter=Q(paid_type='visa')), Decimal(0)),
        cheque=Coalesce(Sum('amount', filter=Q(paid_type='cheque')), Decimal(0)),
        bank=Coalesce(Sum('amount', filter=Q(paid_type='bank')), Decimal(0)),
        the_count=Count('amount'),
        total_value=Sum('amount'),
        ).order_by('-paid_date')

    cash = payment.filter(paid_type='cash').aggregate(cash=Coalesce(Sum('amount'), Decimal(0)))['cash']
    visa = payment.aggregate(visa=Coalesce(Sum('amount', filter=Q(paid_type='visa')), Decimal(0)))['visa']
    cheque = payment.aggregate(cheque=Coalesce(Sum('amount', filter=Q(paid_type='cheque')), Decimal(0)))['cheque']
    bank = payment.aggregate(bank=Coalesce(Sum('amount', filter=Q(paid_type='bank')), Decimal(0)))['bank']



    amount_day = payment.aggregate(sum=Sum('amount'))['sum']

    context = {'payment':payment,'date':date,'amount':amount_day,'method':method,
               'cash':cash,'visa':visa,'cheque':cheque,'bank':bank}
    return render(request,'paid.html',context)


def day_details(request,date):
    method = Payment.payment_type
    patient = request.POST.get('patient')# اللي جاي من doc_cases.html
    type_paid = request.POST.get('type')
    qs = Payment.objects.filter(paid_date=date)
    if patient:
        qs = qs.filter(appoint__patient__name=patient)
    if type_paid:
        qs = Payment.objects.filter(paid_date=date,paid_type=type_paid)

    day_amount = qs.aggregate(sum=Sum('amount'))['sum']
    count = qs.values_list('appoint',flat=True).distinct().count()

    context = {'qs': qs,'details':'details','date':date,'day_amount':day_amount,
               'count':count,'method':method}
    return render(request, 'paid.html', context)



