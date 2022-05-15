from django.conf.urls import url

from .import views

app_name='signal_reciever'

urlpatterns = [
	url(r'^event/$', views.EventFromGSMRF.as_view()),
	url(r'^event_mob/$', views.EventFromMobile.as_view()),
]