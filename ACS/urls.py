from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static
from acs_users import views as aviews
from django.views.generic.base import RedirectView
favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    url(r'^', include('signal_reciever.urls',namespace='reciever')),
	path('admin/', admin.site.urls),
    url(r'^registration/', include('acs_users.urls',namespace='registration')),
    url(r'^login/$', aviews.AcsUserLogin.as_view(), name='login'),
    url(r'^gsm_rf_device/', include('gsm_rf_device.urls',namespace='gsm_rf_device')),
    url(r'^police_station/', include('police_station.urls',namespace='police_station')),
    url(r'^main_user/', include('main_user.urls',namespace='main_user')),
	url(r'^notipush/', include('notipush.urls')),
	url(r'^favicon\.ico$', favicon_view),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 
