from django.conf.urls import url

from .import views

app_name='gsm_rf_device'

urlpatterns = [
	url(r'^registration/$', views.DeviceRegistration.as_view()),
]	