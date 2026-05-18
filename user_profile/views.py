from django.shortcuts import render,redirect
from departs.models import Appointments
from accounts.models import Profile
from django.db.models import Sum,Count,Q
from shared.forms import CustForm,ProForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
User = get_user_model()

@login_required
def user_appoint(request):
    users = Appointments.objects.values_list('employee__id','employee__username').order_by('employee__username').distinct()
    username = request.POST.get('user')
    pro = Profile.objects.get(user=request.user)
    if request.user.is_superuser:
        appoints = Appointments.objects.filter(paid_stat=True)
        if username:
            appoints = Appointments.objects.filter(paid_stat=True, employee=username)
    else:
        appoints = Appointments.objects.filter(employee=request.user,paid_stat=True)
    total = appoints.aggregate(amount=Sum('detect_value'))['amount']
    context = {'appoints':appoints,'total':total,'users':users,'pro':pro}
    return render(request,'user_appoint.html',context)


# @login_required
# def edit_profile(request):
#     user = request.user
#     pro = Profile.objects.get(user=request.user)
#     if request.POST:
#         user_form = CustForm(request.POST,request.FILES,instance=user)
#         pro_form = ProForm(request.POST,request.FILES,instance=pro)
#         if user_form.is_valid() and pro_form.is_valid():
#             user_form.save()
#             pro_form.save()
#             return redirect('profile')
#     else:
#         user_form = CustForm(instance=user)
#         pro_form = ProForm(instance=pro)
#     context = {'user_form':user_form,'pro_form':pro_form}
#     return render(request,'add_update.html',context)
