from django.urls import path,include
import doctors.api_views
import days.api_views
import patient.api_views
from . import views
from . import api_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('Departments',api_views.ViewSet_Depart) # ده اسم الموديل
router.register('Doctors',doctors.api_views.ViewSet_doc)
router.register('Patients',patient.api_views.View_patient)
router.register('Days',days.api_views.View_days)


urlpatterns =[
    #department
    path('depart_list/',views.show_depart , name='depart'),
    path('depart_search/',views.show_depart , name='depart_search'),
    path('depart_doctor/<int:slug>/',views.view_doctor , name='view_doctor'),
    path('add_depart/',views.show_depart , name='add_depart'),
    path('update/<int:slug>/',views.update_depart , name='update_depart'),
    path('delete/<int:slug>/',views.delete_depart , name='delete_depart'),

    path('part_no_work/',views.part_no_work , name='part_no_work'),
    path('part_cases/<int:slug>/',views.part_cases , name='part_cases'),




    # Api
    #FBV
    path('show_departs/',api_views.show_departs,name='show_departs'),
    path('show_departs/<int:pk>/',api_views.show_depart_pk,name='show_depart'),

    #APIview
    path('View_parts/',api_views.View_parts.as_view(),name='View_parts'),
    path('View_parts/<int:id>/',api_views.View_parts_pk.as_view(),name='View_parts'),

    #Generic views
    path('api_department/',api_views.api_depart.as_view(),name='api_depart'),
    path('api/department/<int:pk>/',api_views.api_dep_update.as_view(),name='api_dep_update'),

    #ViewSet
    path('ViewSet_Depart/',include(router.urls)),

    path('find_dep/',api_views.find_dep,name='find_dep'),






    # path('dep/doc/<int:pk>/',api_views.dep_doc,name='dep_doc'),
    # path('api/depart/<int:pk>/',api_views.doc_by_dep.as_view(),name='doc_by_dep'),


    # path('depart/list/',api_views.depart_list,name='depart_list'),
    # path('depart/list/<int:pk>/',api_views.depart_list,name='depart_list'),




]