from django.urls import path,include
from . import views,api_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('Patients',api_views.View_patient)




urlpatterns =[
    path('patient_list/',views.patient_list ,name='patient_list'),
    path('patient_search/',views.patient_list ,name='patient_search'),
    path('patient_form/',views.Add_patient,name='patient_form'),
    path('update/<int:slug>/',views.update_patient,name='patient_update'),
    path('patient_delete/<int:slug>/',views.delete_patient,name='patient_delete'),
    path('patient_details/<int:slug>/',views.patient_details,name='patient_details'),


    path('general_search/',views.general_search,name='general_search'),

    #API
    path('all_patient/',api_views.all_patient,name='patients'),
    path('all_patient/<int:pk>/',api_views.all_patient_pk,name='patient'),

    path('Show_patient/',api_views.Show_patient.as_view(),name='Show_patient'),
    path('Show_patient/<int:pk>/',api_views.Show_patient_pk.as_view(),name='Show_patient_pk'),

    path('Gener_patient/',api_views.Gener_patient.as_view(),name='Gener_patient'),
    path('Gener_patient/<int:id>/',api_views.Gener_patient_id.as_view(),name='Gener_patient_id'),

    path('View_patient/',include(router.urls))
]