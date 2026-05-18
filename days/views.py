from django.shortcuts import render, redirect
from departs.models import Days
from shared.forms import DocForm,DayForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


#days
def days_list(request,day=None):
    dd = Days.days
    input_day = request.POST.get('day')# دمن doc_list.html
    in_day = request.POST.get('available')# دي من appoint_list.html
    if input_day and in_day == None:
        all_days = Days.objects.filter(day=input_day,available=True).order_by('day')
        if not all_days:
            messages.warning(request,'no exists doctors in this day')
            return redirect('days_list')
    elif in_day:
        all_days = Days.objects.filter(day=in_day,available=True).order_by('day')
    else:
        all_days = Days.objects.all().order_by('day')

    context = {'days':all_days,'type':'day','day':dd}
    return render(request, 'doc_list.html', context)


@login_required
def add_day(request):
    error = None
    if request.POST:
        form = DayForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('days_list')
        else:
            error = 'رجاء الرجوع لمدير النظام '
    else:
        form = DayForm()

    context = {'form':form,'error':error}
    return render(request,'add_update.html',context)


@login_required
def day_update(request,pk):
    item = Days.objects.get(pk=pk)
    if request.POST:
        form = DayForm(request.POST,instance=item)
        if form.is_valid():
            form.save()
            return redirect('days_list')
    else:
        form = DayForm(instance=item)
    context = {'form':form}
    return render(request,'add_update.html',context)

