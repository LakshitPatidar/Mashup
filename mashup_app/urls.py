from django.urls import path
from . import views

app_name = 'mashup'

urlpatterns = [
    path('', views.main, name='main')
]
