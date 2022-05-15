from django.conf.urls import url

from .import views

app_name='police_station'

urlpatterns = [
	url(r'^registration/$', views.PoliceStationRegistration.as_view(), name='register'),
	url(r'^home/$', views.Home.as_view(), name='home'),
	url(r'^activity/$', views.Activity.as_view()),
]