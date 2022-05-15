from django.conf import settings
from django.core.cache import cache as mem_cache
from django.contrib.auth import get_user_model
import requests
from googletrans import Translator
from gtts import gTTS
from io import BytesIO
from gsm_rf_device.models import RfDevice 
from police_station.models import PostalCode, PoliceStation
from notipush.utils import send_notification_to_group, send_notification_to_user, send_to_subscription
from rest_framework.authtoken.models import Token
import ast
import json
import base64
from django.urls import reverse
import time

CACHE_TTL 	= 	getattr(settings, 'CACHE_TTL', 24*60*60)
UserModel 	= 	get_user_model()

class MemCache:
	key 		= 	None
	data 		=	None
	CACHE_TTL 	= 	CACHE_TTL
	def get_cache_data(self, key=None):
		self.data = mem_cache.get(key or self.key) or []
		return self.data 
	def set_cache(self, data, key=None):
		mem_cache.set(key or self.key, data, self.CACHE_TTL)
	def del_cache(self, key=None):
		mem_cache.delete(key or self.key)

class GeoLocation:
	def get_address(self, latlng):
		url 		= 	'https://maps.googleapis.com/maps/api/geocode/json?'
		api_key 	=	'AIzaSyB21sBmOdyzBnTUELwgbZ5gbJ6fbfc4PgY'
		res_ob  	= 	requests.get(f"{url}latlng={latlng}&location_type=ROOFTOP&result_type=street_address&key={api_key}")
		res_json 	= 	res_ob.json()
		address 	= 	""
		for addr in res_json.get('results')[0].get('address_components'):
			self.postal_code = None
			if 'postal_code' in addr['types']:
				self.postal_code = addr['long_name']
			elif 'locality' in addr['types']:
				self.locality = addr['long_name']		
			if 'locality' in addr['types'] or 'administrative_area_level_2' in addr['types'] or 'administrative_area_level_1' in addr['types'] or 'country' in addr['types'] or 'postal_code' in addr['types']:
				continue
			address+=(" " if address!="" else "") +  addr['long_name']
		return address	

class Narrative(object):
	def get_sentences(self, index):
		sentences_tp = 	(
							'Alert. There is a suspecious activity in the street following as ',
						)
		return sentences_tp[index]

class Translate(object):
	def trans(self, text, lang):
		translator = Translator()
		t = translator.translate(text, src='en', dest=lang)
		return str(t.text)

class TextToAudio:
	def convert(self, text, lang):
		filename		=	f'event_{self.evt_obj.id}.mp3'
		self.audio_url 	=	f'{settings.MEDIA_URL}{filename}'
		self.alert_data = 	BytesIO()
		tts 			= 	gTTS(text=text, lang=lang, slow=False)
		tts.write_to_fp(self.alert_data)
		tts.save(f'{settings.MEDIA_ROOT}/{filename}')
		return self.alert_data

class TriggerAlarm():
	def trigger(self):
		if self.rf_qs and len(self.rf_qs)>0 and type(self.rf_qs)==str:
			self.rf_qs = ast.literal_eval(self.rf_qs)
			for rf_obj in self.rf_qs:
				token 		=	None
				device_id 	=	rf_obj['fields']['device_id']
				auth_qs 	=	UserModel.objects.filter(client_id=RfDevice(device_id_id=device_id), groups__name=settings.CLIENT_GROUPS[2][0])
				if auth_qs.exists():
					auth_obj 	=	auth_qs.first()
					tokens		= 	Token.objects.filter(user=auth_obj)
					if tokens.exists():
						token 	= 	str(tokens.first().key)
				header = 	{
									'Authorization'		:	f"token {token}",
									'Accept-Language' 	: 	'en_US',
									'Content-Type'		:	'application/json',
				}

				if rf_obj['fields']['host']:
					response 	= 	requests.post(url=f"{rf_obj['fields']['host']}/{device_id}/{settings.GSMRFT_ALARM_URL}", headers=header)
					print(response,'response')
		# time.sleep(3)		

class InformPolice(Narrative, Translate, TextToAudio):
	def infrom(self):
		if self.postal_code:
			pc_qs = PostalCode.objects.filter(postal_code=self.postal_code)
			if pc_qs.exists():
				pc_obj = pc_qs.first()
				ps_qs = PoliceStation.objects.filter(id=int(pc_obj.police_station_id))
				if ps_qs.exists():
					ps_obj = ps_qs.first()
					send_notification_to_group(group_name=f'ps-{self.postal_code}', payload=json.dumps({
																											'head' 		: 	'Alert!', 
																											'body' 		: 	'Something wrong happened.',
																											'vibrate' 	: 	[200, 100, 200, 100, 200, 100, 200],
																											'tag'		:	f'event_{self.evt_obj.id}',
																											'icon'		:	'/media/icons/alert.png',
																											'data' 		:	{
																																'narrative' :	f"{self.trans(self.get_sentences(0), ps_obj.language)} {self.address}",
																																'lang' 		:	ps_obj.language,
																															},
																											'url'		:	f'/notipush/clicked_users?eid={self.evt_obj.id}&t={self.evt_obj.created_at}',	
																											}), 
																											ttl=1000) #, 'alert_data' : self.alert_data
				# self.alert_data.close()

class MobileAppNotify(Narrative, Translate, TextToAudio):
	def notify(self, log_qs):
		mau_qs 	=	MobileAppUsers.objects.filter(app_id=app_id, lat=self.lat, lng=self.lng)
		if mau_qs.exists():
			for mau_obj in mau_qs:
				user_id = mau_obj.user_id
				# push_notification(user_id)
				#
		pass		
