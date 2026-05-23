from django.urls import path,include
from . import views,analysis,api_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('Appointments',api_views.View_appoint)



urlpatterns =[
    path('',views.appoint_list ,name='appoint_list'),
    path('add_appoint/',views.add_appoint ,name='add_appoint'),
    path('update_appoint/<int:pk>/',views.update_appoint ,name='update_appoint'),
    path('paid_appoint/',views.paid_appoint ,name='paid_appoint'),

#analysis
    path('analysis/',analysis.analysis_appoint,name='analysis'),
    path('load_csv/',analysis.load_appoint_csv,name='load_csv'),
    path('load_excel/',analysis.load_appoint_excel,name='load_excel'),
    path('read_excel/',analysis.read_excel,name='read_excel'),
    path('save_data/',analysis.save_data,name='save_data'),


    #API
    path('get_appoint/',api_views.get_appoint,name='get_appoint'),
    path('get_appoint/<int:id>/',api_views.get_appoint_pk,name='appoint_pk'),

    path('all_appoints/',api_views.all_appoints.as_view(),name='all_appoints'),
    path('all_appoints/<int:id>/',api_views.all_appoints_Pk.as_view(),name='appoint'),

    path('Gener_app/',api_views.Gener_app.as_view(),name='Gener_app'),
    path('Gener_app/<int:pk>/',api_views.Gener_app_pk.as_view(),name='update_app'),

    path('view_appoints/',include(router.urls))

    # path('Create_app/',api_views.Create_app.as_view(),name='Create_app'),

]

