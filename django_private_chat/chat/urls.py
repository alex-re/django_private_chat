from django.urls import path
from .views import index,  room


urlpatterns = [
    path('<str:room_name>/', room, name='room'),
    path('', index, name='index'),
]
