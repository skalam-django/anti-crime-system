from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.core.validators import validate_ipv46_address
from django.contrib.auth.models import Group
import ipaddress
from .models import IpWhitelist
from django.conf import settings
import re
from acs_users import sms_gateway_config as sgc
from collections import OrderedDict 
import time
from ACS.utils import MemCache

def is_valid_ip(ip_address):
	try:
		ip = ipaddress.ip_address(u'' + ip_address)
		return True
	except ValueError as e:
		return False

def is_local_ip(ip_address):
	try:
		ip = ipaddress.ip_address(u'' + ip_address)
		return ip.is_loopback
	except ValueError as e:
		return None

def get_ip_address_from_request(request):
	PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', '127.')
	ip_address = ''
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
	if x_forwarded_for and ',' not in x_forwarded_for:
		if not x_forwarded_for.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(x_forwarded_for):
			ip_address = x_forwarded_for.strip()
	else:
		ips = [ip.strip() for ip in x_forwarded_for.split(',')]
		for ip in ips:
			if ip.startswith(PRIVATE_IPS_PREFIX):
				continue
			elif not is_valid_ip(ip):
				continue
			else:
				ip_address = ip
				break
	if not ip_address:
		x_real_ip = request.META.get('HTTP_X_REAL_IP', '')
		if x_real_ip:
			if not x_real_ip.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(x_real_ip):
				ip_address = x_real_ip.strip()
	if not ip_address:
		remote_addr = request.META.get('REMOTE_ADDR', '')
		if remote_addr:
			if not remote_addr.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(remote_addr):
				ip_address = remote_addr.strip()
	if not ip_address:
		ip_address = '127.0.0.1'
	print('acs_users.utils.get_ip_address_from_request() ip_address: ',ip_address)	
	return ip_address 

class IpValidationMixin(object):
	def dispatch(self, request, *args, **kwargs):
		self.ip = get_ip_address_from_request(request)
		try:
			validate_ipv46_address(self.ip)
			ipwhlst_qs = IpWhitelist.objects.filter(ip=self.ip)
			if ipwhlst_qs.exists():
				ipwhlst_obj = ipwhlst_qs.first()
				self.client_type = ipwhlst_obj.client_type
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

def cross_check_user_ip(user, client_type):
	group_qs = Group.objects.filter(user=user)
	if group_qs.exists():
		group_obj = group_qs.first()
		if client_type == group_obj.name:
			return True
	raise ValidationError('NON_AUTHORITATIVE_INFORMATION', code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

class BruteForcePreventMixin(MemCache):
	DEFAULT_THROTTLE_RATES 	= 	settings.DEFAULT_THROTTLE_RATES
	anonymous_limit 		= 	DEFAULT_THROTTLE_RATES['anonymous']
	user_limit	 			= 	DEFAULT_THROTTLE_RATES['auth_user']
	def dispatch(self, request, *args, **kwargs):
		self.context =	{'login_attempt_error':False}		
		if request.method=='POST':
			self.key 			= 	request.POST.get('username')
			otp_timeout 		=	0
			timestamp 			=	time.time()
			login_attempts_arr  = 	self.get_cache_data()
			lock 				=	(login_attempts_arr[0] or False) if login_attempts_arr else False
			login_attempts 		=	(login_attempts_arr[1] or 0) if login_attempts_arr else 0
			login_timestamp		=	(login_attempts_arr[2] or 0) if login_attempts_arr else 0
			otp_attempts 		=	(login_attempts_arr[3] or 0) if login_attempts_arr else 0
			otp_timestamp 		=	(login_attempts_arr[4] or 0) if login_attempts_arr else 0
			login_btn 			= 	self.request.COOKIES.get('login_btn')
			if login_btn=='LOG IN' or login_btn=='ENTER OTP':
				login_attempts 		+=	1	
				durations 			=	timestamp - login_timestamp
				login_timestamp		=	timestamp
				login_attempt_rate 	= 	login_attempts/durations
				if request.user.is_anonymous:
					attempt_rate_limit = self.anonymous_limit[0]/self.anonymous_limit[1]
				else:
					attempt_rate_limit = self.user_limit[0]/self.user_limit[1]
				if login_attempt_rate > attempt_rate_limit:
					lock = True
					self.context['login_attempt_error'] = True
					self.context['login_attempts'] = int(login_attempts)
				else:
					self.context['login_attempt_error'] = False
					if request.user.is_anonymous:
						if login_attempts > self.anonymous_limit[2] and durations < self.anonymous_limit[3]:
							lock = True
						else:
							lock = False
					else:		
						lock = False

				if login_attempts > self.anonymous_limit[4]:
					lock 	= 	True
					self.set_cache([lock, login_attempts, login_timestamp, otp_attempts , otp_timestamp])
					block_ip(request)
			else:
				if request.COOKIES.get('login_type') =='otp' and login_btn =='CONTINUE':
					otp_timeout 		= 	timestamp - otp_timestamp - (settings.OTP['SENDING_CONST'] * otp_attempts)
					otp_attempts 		+=	1
					otp_timestamp		=	timestamp
					if otp_timeout < settings.OTP['TIMEOUT']:
						lock 								= 	True
						self.context['login_attempt_error'] = 	True
						otp_timeout 						= 	2*settings.OTP['TIMEOUT'] - otp_timeout
						# otp_timestamp 						=	timestamp + otp_timeout
						self.context['otp_timeout'] 		= 	f'{time.strftime("%M", time.gmtime(round(otp_timeout)))} mins'
					else:
						lock = False
			#print('lock: ',lock)			
			self.set_cache([lock, login_attempts, login_timestamp, otp_attempts , otp_timestamp])
			self.get_cache_data()
		return super(BruteForcePreventMixin,self).dispatch(request, *args, **kwargs)


class InitSmsProvider(MemCache):
	def __init__(self, *args, **kwargs):
		self.key = 'SMS_SERVICE'
		prv_dict = OrderedDict()
		timestamp= time.time()
		for prv in sgc.PROVIDER_PRIORITY:
			prv_dict[prv] =  {'start':timestamp,'end':timestamp,'block':False,'block_timestamp':timestamp,'nos_block':0}
		print(prv_dict)	
		self.set_cache(prv_dict)
		return super(InitSmsProvider,self).__init__(*args, **kwargs)

class FilteredSmsService(MemCache):
	key = 'SMS_SERVICE'
	# def __init__(self):
	# 	self.key = 'SMS_SERVICE'
	def controller(self, *args, **kwargs):
		self.provider = None
		self.sms_service 	= self.get_cache_data()


		if not self.sms_service is None and len(self.sms_service):
			for provider,ss in self.sms_service.items():	
				start 			= 	ss['start']
				end 			= 	ss['end']
				block			= 	ss['block'] 
				self.time_out 	= 	end - start
				if self.time_out >= sgc.PROVIDER_PRIORITY[provider]['CRITICAL_TIMEOUT'] and block==False:
					self.block(provider)
				elif block==False:
					self.provider = provider
					nos_block = self.sms_service[self.provider]['nos_block'] or 1
					self.sms_service[self.provider]['nos_block']= ( nos_block if nos_block > 0 else 1 ) - 1
					break
			if self.provider is None:
				self.unblock()
		else:
			InitSmsProvider()
			self.controller()
			
	def block(self,provider):
		self.sms_service[provider]['block'] 	=  True
		self.sms_service[provider]['block_timestamp'] = time.time()
		self.sms_service[provider]['nos_block'] = ( self.sms_service[provider]['nos_block'] or 0 ) + 1
		self.set_cache(self.sms_service)

	def unblock(self,force=False):
		dur_arr = []
		for provider,ss in self.sms_service.items():
			block_timestamp	= 	ss['block_timestamp']
			nos_block		=	ss['nos_block']
			time_diff 		=	time.time() - block_timestamp
			FAILURE_CONST 	=	sgc.PROVIDER_PRIORITY[provider]['FAILURE_CONST']
			CRITICAL_TIMEOUT= 	sgc.PROVIDER_PRIORITY[provider]['CRITICAL_TIMEOUT']
			dur_arr.append(((time_diff*FAILURE_CONST*CRITICAL_TIMEOUT)/((nos_block+1)*self.time_out),provider))
		dur_arr.sort()
		if len(dur_arr) and len(dur_arr[-1])>1:
			self.provider = dur_arr[-1][1]
			self.sms_service[self.provider]['block']=False

class SmsService(FilteredSmsService):
	def __init__(self,*args,**kwargs):
		self.mobile_num = 	''
		self.msg_body 	=	''
	def send(self):
		self.controller()
		self.sms_service[self.provider]['start'] = time.time()
		self.send_to_provider()
		self.sms_service[self.provider]['end'] = time.time()
		self.set_cache(self.sms_service)
	def send_to_provider(self):
		from generalize.views import loggerf
		loggerf('sending sms using provider: ',self.provider)
		if self.provider=='sngsms':
			self.sngsms()
		elif self.provider=='twilio':
			self.twilio()
	def sngsms(self):
		import requests
		from django.http import HttpResponse
		key 		=	sgc.PROVIDER_PRIORITY[self.provider]['key']
		campaign 	=	sgc.PROVIDER_PRIORITY[self.provider]['campaign']
		routeid 	=	sgc.PROVIDER_PRIORITY[self.provider]['routeid']
		url 		= 	f'http://sngsms.xyz/app/smsapi/index.php?key={key}&campaign={campaign}&routeid={routeid}&type=text&contacts={self.mobile_num}&senderid=SIMPLY&msg={self.msg_body}'
		r 			= 	requests.post(url)
		return HttpResponse(r)		
	def twilio(self):
		from twilio.rest import Client
		account_sid =	sgc.PROVIDER_PRIORITY[self.provider]['account_sid']
		auth_token 	=	sgc.PROVIDER_PRIORITY[self.provider]['auth_token']
		client 		= 	Client(account_sid, auth_token)
		message 	= 	client.messages.create	(
													body 	=	self.msg_body,
													from_ 	=	'+19372109920',
													to 		=	self.mobile_num
												)    			

def block_ip(request):
	ip = get_ip_address_from_request(request)
	blocked_ip = mem_cache.get('blocked_ip') or []
	blocked_ip.append(ip)
	mem_cache.set('blocked_ip', blocked_ip, CACHE_TTL)
	return redirect('error-500')		