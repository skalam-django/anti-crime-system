from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from .signals import create_auth_token, create_groups_permissions
from django.db.models.signals import post_migrate

class AcsUsersConfig(AppConfig):
	name = 'acs_users'
	verbose_name = _('ACS_Users')
	def ready(self):
		post_migrate.connect(create_groups_permissions, sender=self)
		UserModel = get_user_model()
		post_save.connect(create_auth_token, sender=UserModel)


		