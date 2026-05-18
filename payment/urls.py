from django.urls import path
from . import views

urlpatterns =[
    # المدفوعات
    path('cash_view/',views.cash_view ,name='cash_view'),
    path('payment_appoint/<int:pk>/',views.payment_appoint ,name='payment_appoint'),
    path('payments/',views.payments ,name='payments'),
    path('total_day/',views.total_day ,name='total_day'),
    path('paid/<str:date>/',views.paid ,name='paid'),
    path('day_details/<str:date>/',views.day_details ,name='day_details'),

]
