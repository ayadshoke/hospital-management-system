from django.urls import path
from . import views,analysis

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
]

