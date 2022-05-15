from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import login,  authenticate, logout
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import PoliceStation, PostalCode
from .forms import PoliceStationCreationForm, PoliceStationUserCreationForm, PostalCodeCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
import json

UserModel = get_user_model()


class PoliceStationRegistration(TemplateView): #IpValidationMixin, UserAgentValidationMixin, 
	user_type = 'police_station'
	template_name = 'police_station/registration.html'
	def get(self, request):
		ps_form 	= 	PoliceStationCreationForm(prefix='ps')
		user_form 	= 	PoliceStationUserCreationForm(prefix='user')
		pc_form		=	PostalCodeCreationForm(prefix='pc')
		return render(request, self.template_name, {'ps_form':ps_form, 'user_form':user_form, 'pc_form':pc_form})
	def post(self, request):
		ps_form 	= 	PoliceStationCreationForm(request.POST, prefix='ps')
		user_form 	= 	PoliceStationUserCreationForm(request.POST, prefix='user')
		pc_form		=	PostalCodeCreationForm(request.POST, prefix='pc')
		if ps_form.is_valid()==True and user_form.is_valid()==True and pc_form.is_valid()==True:
			ps_json 	= 	ps_form.cleaned_data
			user_json 	= 	user_form.cleaned_data
			pc_json 	= 	pc_form.cleaned_data			
			JSON_obj 	= 	dict()
			JSON_obj.update(ps_json)
			JSON_obj.update(user_json)
			JSON_obj.update(pc_json)
			auth_obj 	= 	PoliceStation.objects.register(JSON_obj)
			return redirect(reverse('police_station:home'))
		return render(request, self.template_name, {'ps_form':ps_form, 'user_form':user_form, 'pc_form':pc_form})

class PoliceStationRegisterApi(APIView): #IpValidationMixin, UserAgentValidationMixin,
	permission_classes 			= 	[AllowAny,]
	def post(self, request):
		JSON_obj 	= 	request.data #json.loads(request.body)
		auth_obj 	= 	PoliceStation.objects.register(JSON_obj)
		token 		=	None
		if auth_obj:
			token_qs= 	Token.objects.filter(user=auth_obj)
			if token_qs.exists():
				token_obj 	= 	token_qs.first()
				token 		= 	token_obj.key
		return Response({'token' : token}) 


class Home(LoginRequiredMixin, TemplateView):
	template_name = 'police_station/home.html'
	def get_context_data(self, *args, **kwargs):
		pc_qs = PostalCode.objects.filter(police_station=self.request.user.client_id)
		if pc_qs.exists():
			group = []
			for pc_obj in pc_qs:
				group.append(f'ps-{pc_obj.postal_code}')
			notipush 	= 	{'group': group}
			context 	= 	super(Home,self).get_context_data(**kwargs)
			context.update({"notipush" : notipush})	
			return context
		logout(self.request)
		return redirect(reverse('police_station:home'))
		
class HelpVictim(APIView):
	authentication_classes 		= 	(TokenAuthentication,)
	permission_classes 			= 	[IsAuthenticated,]
	def post(self, request):
		user 		= 	request.user
		data 		= 	request.data
		user_id 	=	data.get('user_id')
		auth_qs 	=	UserModel.objects.filter(id=int(user_id))
		if auth_qs.exists():
			auth_obj 	=	auth_qs.first()
			tokens		= 	Token.objects.filter(user=auth_obj)
			if tokens.exists():
				victim_token 	= 	str(tokens.first().key)
				event_id 		= 	data.get('eid')
				rf_qs 			=	Events.objects.gsmrft(id=int(event_id))
				for rf_obj in rf_qs:
					host 		=	rf_obj.host
					device_id 	=	rf_obj.device_id
					if host:
						auth_qs =	UserModel.objects.filter(client_id=RfDevice(device_id_id=device_id), groups__name=settings.CLIENT_GROUPS[2][0])
						if auth_qs.exists():
							auth_obj 	=	auth_qs.first()
							tokens		= 	Token.objects.filter(user=auth_obj)
							if tokens.exists():
								token 	= 	str(tokens.first().key)
								header 	= 	{
													'Authorization'		:	f"token {token}",
													'Accept-Language' 	: 	'en_US',
													'Content-Type'		:	'application/json',
								}
								instruction =	data.get('instruction')
								response 	= 	requests.post(url=f"{host}/{device_id}/{settings.GSMRFT_VIA_URL}", data 	=	{
																																	'instruction' 	: 	instruction,
																																	'victim_token'	:	victim_token,
																																}, 
																																headers=header)
				return Response(200)
		return Response(404)		

class Activity(TemplateView):
	template_name = 'police_station/activity.html'

