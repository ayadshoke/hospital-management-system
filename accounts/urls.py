from django.urls import path, reverse_lazy,include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views,api_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('permissions',api_views.ViewSet_perm)
router.register('Departments',api_views.ViewSet_Depart)
router.register('Doctors',api_views.ViewSet_doc)
# router.register('product',views.viewsets_product)



app_name = 'accounts'
urlpatterns =[
    path('register/',views.register,name ='register'),

    # دي طريقة اخري لحماية الدالة ويبقي لازم يعمل login الاول
    path('profile/',login_required(views.profile),name='profile'),
    path('edit_profile/',login_required(views.Edit_profile),name='edit_profile'),
    path('edit_image/<int:id>/',login_required(views.edit_image),name='edit_image'),

    #users
    path('users_perm/',login_required(views.users_permission),name='view_users'),
    path('edit_user_perm/<int:id>/',login_required(views.edit_user_perm),name='edit_permissions'),

    #permissions
    path('permission/',views.permission,name='permissions'),
    path('add_perm/',views.add_permissions,name='add_perm'),
    path('cust_perm/<int:perm_id>/',views.cust_perm,name='cust_perm'),
    path('delete_perm/<str:codename>/',login_required(views.delete_perm),name='delete_perm'),

    #models
    path('show_model/',views.show_model,name='show_model'),



    # API
    path('api/users/',api_views.UserList.as_view(),name='api_users'),
    path('api/users/<int:id>/',api_views.Edit_user.as_view(),name='Edit_user'),
    path('add/perm/<int:id>/',api_views.add_perm.as_view(),name='add_perm_user'),

    # FBV
    path('api/perm/',api_views.api_perm , name='api_perm'),
    path('api/perm/<int:perm_id>/',api_views.api_perm_detail , name='api_perm'),

    #APIview
    path('ViewPerm/',api_views.View_Perm.as_view(),name='View_Perm'),
    path('ViewPerm/<int:id>/',api_views.View_Perm_pk.as_view(),name='View_Perm_pk'),

    #Generic views
    path('GenerPerm/',api_views.Gener_Perm.as_view(),name='Gener_Perm'),
    path('GenerPerm/<int:pk>/',api_views.Gener_Perm_pk.as_view(),name='Gener_Perm_pk'),

    #ViewSet
    path('ViewSetPerm/',include(router.urls)),



]
    # دي علشان لو استخدم حاجات django داخل app لازم اكتب url بس بدون views
    # path('password_change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
    # path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
