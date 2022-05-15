from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.core.validators import validate_ipv46_address
from acs_users.models import IpWhitelist
from acs_users.utils import get_ip_address_from_request


class IpValidationMixin(object):
	def dispatch(self, request, *args, **kwargs):
		self.ip = get_ip_address_from_request(request)
		try:
			validate_ipv46_address(self.ip)
			ipwhlst_qs = IpWhitelist.objects.filter(ip=self.ip)
			if ipwhlst_qs.exists():
				return super(IpValidationMixin, self).dispatch(request, *args, **kwargs)
			raise ValidationError('NON_AUTHORITATIVE_INFORMATION', code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
		except Exception as e:
			print(e,'e')
			raise ValidationError('NON_AUTHORITATIVE_INFORMATION', code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)		

class UserAgentValidationMixin(object):
	def dispatch(self, request, *args, **kwargs):
		user_agent = request.META.get('HTTP_USER_AGENT')
		try:
			if user_agent:
				if user_agent.split(',')[0]=='BuildFailureDetectorESP8266':
					return super(UserAgentValidationMixin, self).dispatch(request, *args, **kwargs)
			raise ValidationError('NON_AUTHORITATIVE_INFORMATION', code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
		except Exception as e:
			print(e,'e')
			raise ValidationError('NON_AUTHORITATIVE_INFORMATION', code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)	