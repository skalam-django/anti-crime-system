from __future__ import absolute_import
from ACS.celery import app
from celery import Task
from celery.decorators import task
from celery.utils.log import get_task_logger
from django.conf import settings
import datetime
import time
import requests, json
from .utils import MemCache, GeoLocation, Narrative, Translate, TextToAudio, TriggerAlarm, InformPolice, MobileAppNotify
from signal_reciever.models import Events
from acs_users.utils import SmsService
import logging
logger = logging.getLogger(__name__)


#mem_cache.get_cache_data()    ---> wait_tigger_alarm_1 : [True/False, tstmp]

class TaskGrant():
	def grant(self, exe_obj):
		mem_cache = MemCache()
		mem_cache.key = f'wait_{self.key}'
		st_time = time.time()
		self.data.append([self.task_id, st_time])   # tigger_alarm_1 : [[task_id1, tstmp1], [task_id2, tstmp2]]
		self.set_cache(self.data)
		while [True if [d==True for d in (mem_cache.get_cache_data() or [False])][0] else False][0]:
			if int(time.time()-st_time)>(self.CACHE_TTL/3):
				mem_cache.set_cache([False, [d for d in (mem_cache.get_cache_data() or [False, st_time])][1]])  
				break
			time.sleep(2)	
			continue	
		mem_cache.set_cache([True, [d for d in (mem_cache.get_cache_data() or [False, st_time])][1]])
		logger.info(f'{self.data}   self.data     1')
		logger.info(f'{self.task_id}   self.task_id   1 ')
		if self.data:
			self.data.sort(key=lambda d: d[1], reverse=True)
			if self.data[0][0]==self.task_id and self.data[0][1]>=mem_cache.get_cache_data()[1]:
				exe_obj()
				logger.info(f'{self.data}   self.data1   2')
				logger.info(f'{self.task_id}   self.task_id    2 ')
				data1 = self.get_cache_data().sort(key=lambda d: d[1], reverse=True)
				if data1:
					for i,d in enumerate(self.data):
						del data1[i]
					self.set_cache(data1)
				mem_cache.set_cache([False, self.data[0][1] if self.data else time.time()])
			# else:
			# 	mem_cache.set_cache([False, [d for d in (mem_cache.get_cache_data() or [False, st_time])][1]])	
			
class BaseTask(MemCache, TaskGrant, Task):
	CACHE_TTL = 30 #15 secs
	def __call__(self, *args, **kwargs):
		if kwargs.get('event_id'):
			evt_qs = Events.objects.filter(id=int(kwargs.get('event_id')))
			if evt_qs.exists():	
				self.evt_obj	=	evt_qs.first()
				self.rf_qs 		=	kwargs.get('rf_qs')
				self.lat 		=	kwargs.get('lat')
				self.lng 		=	kwargs.get('lng')
				self.address 	=	kwargs.get('address')
				self.postal_code= 	kwargs.get('postal_code')
				self.key 		+=	f'_{self.evt_obj.id}'
				self.data 		= 	self.get_cache_data() or []  #tigger_alarm_1 : [[task_id1, tstmp1], [task_id2, tstmp2]]
				return self.run(*args, **kwargs)
		return
	def after_return(self, status, retval, task_id, args, kwargs, einfo):
		pass	

class TriggerAlarmQueue(TriggerAlarm, BaseTask):
	key = 'trigger_alarm'
	def run(self, *args, **kwargs):
		self.task_id	=	TriggerAlarmQueue.request.id
		self.grant(self.trigger)
TriggerAlarmQueue = app.register_task(TriggerAlarmQueue())

class InformPoliceQueue(InformPolice, BaseTask):
	key = 'inform_police'
	def run(self, *args, **kwargs):
		self.task_id 	=	InformPoliceQueue.request.id
		self.grant(self.infrom)
InformPoliceQueue = app.register_task(InformPoliceQueue())
	
class MobileAppNotifyQueue(MobileAppNotify, BaseTask):
	key = 'mobile_app'
	def run(self, *args, **kwargs):
		self.task_id 	=	MobileAppNotifyQueue.request.id
		self.grant(self.notify)
MobileAppNotifyQueue = app.register_task(MobileAppNotifyQueue())

class AlertQueue(GeoLocation, Task):
	def run(self, event_id, rf_qs):
		try:
			evt_qs = Events.objects.filter(id=int(event_id))
			if evt_qs.exists():
				evt_obj 	= 	evt_qs.first()
				lat 		=	evt_obj.lat
				lng 		=	evt_obj.lng
				address 	= 	self.get_address(f"{lat}, {lng}")
				if len(rf_qs)>0:
					TriggerAlarmQueue.delay(event_id=event_id, rf_qs=rf_qs, lat=lat, lng=lng, address=address, postal_code=self.postal_code)
					# InformPoliceQueue.delay(event_id=event_id, rf_qs=rf_qs, lat=lat, lng=lng, address=address, postal_code=self.postal_code)
				# MobileAppNotifyQueue.delay(event_id, rf_qs, lat, lng, address)
		except Exception as e:
			error = f'{datetime.datetime.now()} [ERROR] AlertQueue().run() : {e}'
			if settings.DEBUG:
				print(error)
			else:	
				logger.debug(error)	
AlertQueue = app.register_task(AlertQueue())


class SmsQueue(SmsService,Task):
	def run(self,mobile_num,msg_body):
		try:
			self.mobile_num = mobile_num
			self.msg_body 	= msg_body
			self.send()
		except Exception as e:
			error = f'{datetime.datetime.now()} [ERROR] SmsQueue().run() : {e}'
			if settings.DEBUG:
				print(error)
			else:	
				logger.debug(error)	
SmsQueue = app.register_task(SmsQueue())