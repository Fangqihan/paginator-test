from django.conf.urls import url,include
from django.contrib import admin
from app01 import views as app1_view

urlpatterns = [
    url(r'^register/(\d+)/', app1_view.register,name='register'),
]