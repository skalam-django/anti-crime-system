from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from acs_users.utils import IpValidationMixin, UserAgentValidationMixin, cross_check_user_ip
from .models import Events
from ACS.workers import AlertQueue 
import json
from django.core import serializers
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EventFromGSMRF(IpValidationMixin, UserAgentValidationMixin, APIView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[IsAuthenticated,]
	def post(self, request):
		cross_check_user_ip(request.user, self.client_type)
		device_id 	=	request.user.client_id
		JSON_obj 	= 	json.loads(request.body)
		log_qs 		= 	Events.objects.log(device_id, JSON_obj)
		event_id 	= 	log_qs[0]
		rf_qs		=	log_qs[1]
		task 		=	AlertQueue.delay(event_id, serializers.serialize('json',rf_qs))
		return Response({'event_id':event_id})


class EventFromMobile(APIView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[IsAuthenticated,]
	def post(self, request):
		cross_check_user_ip(request.user, settings.CLIENT_GROUPS[0][0])
		device_id 	=	request.user.client_id
		JSON_obj 	= 	json.loads(request.body)
		log_qs 		= 	Events.objects.log(device_id, JSON_obj)
		event_id 	= 	log_qs[0]
		rf_qs		=	log_qs[1]
		task 		=	AlertQueue.delay(event_id, serializers.serialize('json',rf_qs))
		return Response({'event_id':event_id})