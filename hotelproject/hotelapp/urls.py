from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('available_rooms/', views.available_rooms, name='available_rooms'),
    path('make_reservation/', views.make_reservation, name='make_reservation'),
    path('confirm_reservation/', views.confirm_reservation, name='confirm_reservation')
]