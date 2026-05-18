import os

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .form import CustomUserCreationForm
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required, permission_required
from .models import Profile
from shared.forms import CustForm,ProForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from PIL import Image
import subprocess
User=get_user_model()

# def safe_perm_dynamic(func):
#     def wrapper(request,codename,*args,**kwargs):
#         return func(request, codename, *args, **kwargs)
#     return wrapper

@login_required
def register(request):
    if request.user.is_superuser:
        if request.POST:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                # لو عايز تعمل login علي طول استخدم دي
                # username = form.cleaned_data['username']
                # password = form.cleaned_data['password1']
                # user = authenticate(username=username,password=password)
                # login(request, user)
                return redirect('login')
        else:
            form = CustomUserCreationForm()
    else:
        return redirect('login')
    context = {'form':form}
    return render(request,'registration/register.html',context)

def profile(request):
    qs = Profile.objects.get(user=request.user)

    return render(request,'profile.html',{'qs':qs})

# تم حمايتها من url الخاص بيها
def Edit_profile(request):
    user = request.user
    pro = Profile.objects.get(user=request.user)
    if request.POST:
        user_form = CustForm(request.POST,request.FILES,instance=user)
        pro_form = ProForm(request.POST,request.FILES,instance=pro)
        if user_form.is_valid() and pro_form.is_valid():
            user_form.save()
            pro_form.save()
            return redirect('accounts:profile')
    else:
        user_form = CustForm(instance=user)
        pro_form = ProForm(instance=pro)
    context = {'user_form':user_form,'pro_form':pro_form}
    return render(request,'add_update.html',context)


def users_permission(request):
    order = request.GET.get('order','username') #لو انا عامل في url في صفحة html علامة ؟
    all_users = None
    if request.user.is_superuser:
        all_users = User.objects.all().prefetch_related('user_permissions').order_by(order) # هنا مش هانتعامل مع User  علشان abstract

    context = {'users':all_users}
    return render(request,'view_users.html',context)


def edit_user_perm(request,id):
    word = request.GET.get('q')
    se_type = request.GET.get('type')
    item = User.objects.get(pk=id)
    ##filter(content_type__app_label='departs')  دي لو عايز تعمل فلتر علي app معين
    permissions = Permission.objects.all().select_related('content_type')
    if word and se_type == 'Start':
        permissions = permissions.filter(name__startswith=word)
    if word and se_type == 'End':
        permissions = permissions.filter(name__endswith=word)
    if word and se_type == 'Contain':
        permissions = permissions.filter(name__icontains=word)
    if request.POST:
        perms_ids = request.POST.getlist('permission')
        item.user_permissions.set(perms_ids) # ده اهم سطر بيمسح الصلاحيات القديمة ويجيب الجديد
        return redirect('accounts:view_users')

    per_page = request.GET.get('pages')

    # if per_page :#and per_page.isdigit():
    #     per_page = int(per_page)
    # else:
    #     per_page = 10

    try:     #   ودي طريقة تانية
        per_page = int(per_page)
    except:
        per_page = 10
    page_count = Paginator(permissions, per_page)
    page_number = request.GET.get('page')
    page_obj = page_count.get_page(page_number)

    context = {'item':item,'permissions':page_obj,'id':id,'per_page':per_page}
    return render(request,'edit_permissions.html',context)


def permission(request):
    perms = Permission.objects.all()
    content = ContentType.objects.all().order_by('app_label')
    users = User.objects.values_list('username',flat=True).distinct()

    app = request.POST.get('app')
    search = request.POST.get('q')
    user_id = request.POST.get('user')
    if app:
        perms = Permission.objects.filter(content_type=app)
    if search:
        perms = Permission.objects.filter(name__icontains=search)
    if user_id != 'no_user':
        perms = Permission.objects.filter(user__username=user_id)

    if user_id == 'no_user':
        perms = Permission.objects.filter(user__username__isnull=True)

    row = int(request.GET.get('index',0))
    current_row = perms[row:row+1]


    context = {'permissions':perms,'content':content,'users':users,'row':row,'current_row':current_row}
    return render(request,'permission.html',context)


def add_permissions(request):
    content = ContentType.objects.all().order_by('app_label')
    if request.POST:
        model_id = request.POST.get('model')
        name = request.POST.get('perm')
        codename = request.POST.get('codename')
        content_type = ContentType.objects.get(pk=model_id)
        Permission.objects.create(
            name = name,
            codename = codename,
            content_type = content_type)
        return redirect('accounts:permissions')

    context = {'content': content,'add':'add'}
    return render(request, 'permission.html', context)

def cust_perm(request,perm_id):
    perm = Permission.objects.get(pk=perm_id)
    perm_user = User.objects.filter(user_permissions=perm) # دي كل اليوزرات الي عندهم الصاحية
    al_user = User.objects.all()
    if request.POST:
        selected_users = request.POST.getlist('user')
        perm.user_set.clear()# اولا يتم مسح كل اليوزرات

        for user_id in selected_users:
            user = User.objects.get(pk=user_id)
            user.user_permissions.add(perm) #ده اهم سطر في الكود
            messages.success(request,'تم الحفظ بنجاح')
        return redirect('accounts:permissions')

    context = {'users':al_user,'perm':perm,'perm_user':perm_user,'pk':'pk'}
    return render(request,'permission.html', context)



# @safe_perm_dynamic
def delete_perm(request,codename):
    item = Permission.objects.filter(codename=codename).first()
    if request.POST:
        item.user_set.clear()
        item.group_set.clear()
        item.delete()
        return redirect('accounts:permissions')
    context = {'obj': item}
    return render(request, 'delete_obj.html', context)



        # for user in User.objects.filter(user_permissions =item ):
        #     user.user_permissions.remove(item)
        # for group in Group.objects.filter(permissions = item):
        #     group.permissions.remove(item)



def show_model(request):
    content = ContentType.objects.all().order_by('pk')

    context = {'content': content,'model':'model'}
    return render(request, 'permission.html', context)

def edit_image(request,id):
    item = User.objects.get(pk=id)

    image_path = item.image.path #ده اسم العامود اللي في الموديل الخاص بالصورة
    print(item.username)
    # img = Image.open(image_path) # بيتم فتح الصورة باستخدام المكتبة
    os.startfile(image_path)
    # img = img.resize((300,400))
    # img = img.convert('L')# لتحويل لون الصورة
    # img.save(image_path) # الحفظ بنفس الاسم لو عايز تغير الاسم نكتبه في القوسين
    return redirect(item.image.url)










# @login_required
# def logout_account(request):
#     logout(request)
#     return redirect('sign_up')

# def reset_password(request):
#     pass
#     return redirect('sign_up')
# def sign_up(request):
#     page = 'login'
#     if request.user.is_authenticated:
#         messages.error(request,'you are already login ')
#         return redirect('general_search')
#     else:
#         if request.POST:
#             form = CustomAuthenticationForm(request , request.POST)
#             if form.is_valid():
#                 # username = form.cleaned_data['username']
#                 # password = form.cleaned_data['password1']
#                 # user = authenticate(username=username,password=password)
#                 # login(request, user)
#                 return redirect('general_search')
#             else:
#                 messages.error(request,'your username or password is not correct')
#         else:
#             form = CustomAuthenticationForm()
#     context = {'page':page ,'form':form}
#     return render(request,'login_register.html',context)


