from __future__ import absolute_import
from django.conf import settings
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .utils import IpValidationMixin, UserAgentValidationMixin 
from .models import IpWhitelist
from gsm_rf_device.models import GsmDevice, RfDevice
from police_station.models import PostalCode, PoliceStation
import json
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class DeviceRegistration(IpValidationMixin, UserAgentValidationMixin, APIView):
	permission_classes 			= 	[AllowAny,]
	def post(self, request):
		JSON_obj 	= 	json.loads(request.body)
		gsm_arr 	=	GsmDevice.objects.register(JSON_obj, self.ip)
		device_id 	=	gsm_arr[0]
		auth_obj 	= 	gsm_arr[1]
		context 	=	{}
		if auth_obj:
			token_qs = Token.objects.filter(user=auth_obj)
			if token_qs.exists():
				token_obj 	= 	token_qs.first()
				token 		= 	token_obj.key
				context 	=	{'aes128_cpin' : settings.AES128_CPIN, 'device_id' : device_id, 'token' : token}
		return Response(context) 