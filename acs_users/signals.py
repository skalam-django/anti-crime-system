from django.conf import settings
def create_auth_token(sender, instance, created, **kwargs):
	if created==True and instance.is_superuser==False:
		try:
			from rest_framework.authtoken.models import Token
			token 	= 	Token.objects.create(user=instance)
		except Exception as e:
			print('error: ',e)

def create_groups_permissions(sender, **kwargs):
	from django.contrib.auth.models import Group, Permission
	from django.contrib.contenttypes.models import ContentType
	from .permissions import MODEL_PERMS
	for cts in settings.CLIENT_GROUPS:
		group, created = Group.objects.get_or_create(name=cts[0])
	for content_type in ContentType.objects.all():
		if MODEL_PERMS.get(content_type.model):
			for perms, groups in MODEL_PERMS.get(content_type.model).items():
				if groups:
					codename = f'{perms}_{content_type.model}'
					name = f'Can {perms} {content_type.name}'
					perm_obj, created = Permission.objects.get_or_create(content_type=content_type,codename=codename,name=name)
					for group in groups:
						group_qs = 	Group.objects.filter(name=group)
						if group_qs.exists():
							group_obj = group_qs.first()
							group_obj.permissions.add(perm_obj)