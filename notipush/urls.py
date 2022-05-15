from django.conf.urls import url
from . import views
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_control

# app_name='notipush'

urlpatterns = [
    url(r'^save_information', views.SaveSubscription.as_view(), name='save_notipush_info'),
    url(r'^clicked_users', views.ClickedUsers.as_view(), name='clicked_users'),
    url(r'^redirect_to_map', views.UserToVictimPath.as_view(), name='redirect_to_map'),
    url(r'^service-worker.js', cache_control(max_age=2592000)(TemplateView.as_view(template_name="notipush_serviceworker.js",content_type='application/javascript',)), name='service_worker'),
]




	