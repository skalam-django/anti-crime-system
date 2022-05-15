from __future__ import absolute_import
from django.conf import settings
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import IpWhitelist
from gsm_rf_device.models import GsmDevice, RfDevice
from police_station.models import PostalCode, PoliceStation

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.generic.base import TemplateResponseMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model,_clean_credentials
from django.contrib.auth.signals import user_login_failed
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import HiddenInput
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.forms import MultiValueField
from django import forms
import datetime
import time
import json
from ACS.workers import SmsQueue
from .utils import BruteForcePreventMixin, MemCache
from .models import OTP
from generalize.views import printf, loggerf, Generalize

from django.contrib.auth import get_user_model

UserModel = get_user_model()


class MobileAppRegistration(APIView):
	permission_classes 			= 	[AllowAny,]
	def post(self, request):
		JSON_obj 	= 	json.loads(request.body)
		auth_obj 	= 	MobileApp.objects.register(JSON_obj)
		token 		=	None
		if auth_obj:
			token_qs = Token.objects.filter(user=auth_obj)
			if token_qs.exists():
				token_obj 	= 	token_qs.first()
				token 		= 	token_obj.key
		return Response({'token' : token}) 



class AuthMixin(object):
	def dispatch(self,request,*args,**kwargs):
		if self.request.method in ('POST', 'PUT'):
			username 			= 	request.POST.get('username')
			password 			= 	request.POST.get('password')
			if self.data and self.data[0]==True:
				user_login_failed.send(sender=__name__, credentials=_clean_credentials({'username':username,'password':password}), request=request)
				modify_request_params(request,['password'],[None])
			else:
				user_qs 	= 	UserModel.objects.filter((Q(username__iexact=username) | Q(phone_number__iexact=username) | Q(email__iexact=username)))
				if user_qs.exists():
					if user_qs.count()==1 and user_qs.first().check_password(password):
						modify_request_params(request,['username'],[user_qs.first().username])
					else:
						user_login_failed.send(sender=__name__, credentials=_clean_credentials({'username':username,'password':password}), request=request)
						modify_request_params(request,['password'],[None])

		return super(AuthMixin,self).dispatch(request,*args,**kwargs)	



def modify_request_params(request,key_arr,val_arr):
	if request.method=='POST':
		mutable 				= 	request.POST._mutable
		request.POST._mutable 	= 	True
		for i,key in enumerate(key_arr):
			request.POST[key] 		= 	val_arr[i]
		request.POST._mutable 	= 	mutable
	elif request.method=='GET':	
		mutable 				= 	request.GET._mutable
		request.GET._mutable 	= 	True
		for i,key in enumerate(key_arr):
			request.GET[key] 		= 	val_arr[i]
		request.GET._mutable 	= 	mutable


class OtpManager:
	def __init__(self,phone_number):
		self.phone_number = phone_number	
	def create_otp(self):
		otp = OTP.objects.otp(self.phone_number)
		loggerf(f'****************** Phone No: {self.phone_number} ******** | ******** OTP: {otp} ****************** ')
		msg_body = f'Hi Simply user, Use This OTP: {otp}'
		SmsQueue.delay(self.phone_number,msg_body)
	def used(self):
		used_flag = OTP.objects.used(self.phone_number)
		printf('used_flag :',used_flag)


class AcsUserLogin(BruteForcePreventMixin, AuthMixin, LoginView):
	template_name 				= 	'acs_users/acs_users_login.html'
	redirect_authenticated_user = 	False
	USERNAME_LABEL				=	'Username/Phone No/Email '
	PASSWORD_LABEL 				=	'Password '
	SITE_HEADER 				=	'ACS - User Login'
	login_btn 					=	'LOG IN'
	error_messages 				=	{}
	context 					=	{}
	app_path 					=	''
	def get_context_data(self, *args, **kwargs):
		self.context.update(super(AcsUserLogin,self).get_context_data(**kwargs))
		self.context['title']			=	'Login'
		self.context['site_title']		=	'ACS'
		self.context['site_header']		=	self.SITE_HEADER
		self.context['app_path']		=	self.app_path
		self.context['login_btn'] 		=	self.login_btn
		return self.context
	def get_form(self, **kwargs):
		form_class = super(AcsUserLogin,self).get_form()
		form_class.fields['username'].label 	=	self.USERNAME_LABEL
		form_class.fields['password'].label 	=	self.PASSWORD_LABEL
		return form_class

class PhoneVerificationRequiredMixin(UserPassesTestMixin):
	login_url  				=	'acs_users:phone-verification'
	redirect_field_name 	=	'next'	
	LOGIN_REDIRECT_URL 		= 	'/acs_users/home/'
	def test_func(self):
		try:
			user_qs = UserModel.objects.filter(username=self.request.user).order_by('-date_joined')
			if user_qs.exists():
				user_obj = user_qs.first()
				return user_obj.is_verified and user_obj.is_authenticated and (True if user_obj.phone_number else False)
			return False
		except Exception as e:
			loggerf('PhoneVerificationRequiredMixin().test_func() Error: ',e)	

def resend_otp(request):
	if request.method=='GET':
		try:
			otp_manager = OtpManager(request.GET.get('username'))
			created 	= otp_manager.create_otp()
			success 	= True
			second_to_count = int(request.GET.get('second_to_count'))+2*settings.OTP['RESEND_TIMEOUT']
		except:
			success = False	
			second_to_count = int(request.GET.get('second_to_count'))
		return JsonResponse({'success':success,'second_to_count':second_to_count})



class Home(LoginRequiredMixin, TemplateView):
	template_name 		= 	'acs_users/home.html'
