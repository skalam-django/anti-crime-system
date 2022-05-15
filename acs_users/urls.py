from django.conf.urls import url

from .import views

app_name='acs_users'

urlpatterns = [
	url(r'^home/$', views.Home.as_view(),name='home'),
	url(r'^mobile-app/$', views.MobileAppRegistration.as_view()),
]	


