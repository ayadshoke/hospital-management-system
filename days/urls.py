from django.urls import path,include
from . import views,api_views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('Days',api_views.View_days)

urlpatterns =[
#days
    path('days_list/',views.days_list, name='days_list'),
    path('days_details/',views.days_list, name='days_details'),
    path('days_doctor/',views.days_list, name='days_doctor'),
    path('add_day/',views.add_day, name='add_day'),
    path('day_update/<int:pk>/',views.day_update, name='day_update'),
    # path('day_delete/<int:pk>/',views.day_delete, name='day_delete'),

    #API
    path('al_days/',api_views.al_days,name='al_days'),
    path('al_days/<int:id>/',api_views.al_days_id,name='day'),

    path('Api_days/',api_views.Api_days.as_view(),name='Api_days'),
    path('Api_days/<int:id>/',api_views.Api_days_id.as_view(),name='Api_days_id'),

    path('Gen_days/',api_views.Gen_days.as_view(),name='Gen_days'),
    path('Gen_days/<int:id>/',api_views.Gen_days_id.as_view(),name='Gen_days_id'),

    path('View_days/',include(router.urls))

]