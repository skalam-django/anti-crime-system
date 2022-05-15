from django.conf.urls import url

from .import views

app_name='main_user'

urlpatterns = [
	url(r'^home/$', views.Home.as_view(),name='home'),
	url(r'^registration/$', views.MainUserRegistration.as_view(), name='register'),
	url(r'^verify_device_id/$', views.VerifyDeviceId.as_view(), name='verify_device_id'),
	url(r'^get_location/$', views.GetLocation.as_view(), name='get_location'),
]	


