from django.urls import path,include
from . import views,api_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('Doctors',api_views.ViewSet_doc) # هنا بنكتب اسم الموديل بالظبط

urlpatterns =[
#doctor
    path('doctor_list/',views.doc_list , name='doc_list'),
    path('doc_update/<int:pk>/',views.doc_update, name='doc_update'),
    path('doc_delete/<int:pk>/',views.doc_delete, name='doc_delete'),
    path('doc_cases/<int:pk>/',views.doc_case , name='doc_case'),
    path('amount_cases/<int:pk>/',views.amount_cases, name='doc_amount'),

    #API
    #FBV
    path('api_doc/',api_views.api_doc,name='api_doc'),
    path('api_doc/<int:id>/',api_views.api_doc_pk,name='api_doc'),

    path('doc_list/',api_views.Doc_list.as_view(),name='doctor_list'),
    path('doc_list/<int:id>/',api_views.Doc_list_pk.as_view(),name='doc_pk'),

    path('gen_doc/',api_views.Gen_doc.as_view(),name='Gen_doc'),
    # هنا لازم int : pk لازم نكتب pk علشان الدالة تروح عليه ممنوع التغيير
    path('gen_doc/<int:pk>/',api_views.Gen_doc_pk.as_view(),name='Gen_doc'),

    path('view_doc/',include(router.urls)),
]