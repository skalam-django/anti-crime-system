from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from .signals import create_event_history
from django.conf import settings

class SignalRecieverConfig(AppConfig):
	name = 'signal_reciever'
	verbose_name = _('signal_reciever')
	def ready(self):
		from .models import Events
		post_save.connect(create_event_history, sender=Events)		

