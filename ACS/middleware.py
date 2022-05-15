from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import render
import datetime
from generalize.views import loggerf


class ACSPreMiddleware(MiddlewareMixin):
	def __init__(self, get_response, *args, **kwargs):
		return super(ACSPreMiddleware,self).__init__(get_response, *args, **kwargs)
	def process_request(self, request, *args, **kwargs):
		pass

	def process_response(self, request, response):
		return response

	def process_view(self, request, view_func, view_args, view_kwargs):
		self.func_name 		=	view_func.__name__
		self.func_module 	= 	view_func.__module__

	def process_exception(self, request, exception):
		error = f'{datetime.datetime.now()}  [ERROR] {self.func_module}.{self.func_name}(): {exception}'
		loggerf(error)
		if not settings.DEBUG:
			return render(request,'error_page.html',{'error1':'Something seems to have gone wrong','error2':None})
		return None	


class ACSPostMiddleware(MiddlewareMixin):
	def __init__(self, get_response, *args, **kwargs):
		return super(ACSPostMiddleware,self).__init__(get_response, *args, **kwargs)
	def process_request(self, request, *args, **kwargs):
		request.META['static_version']=settings.STATIC_VERSION

	def process_response(self, request, response):
		response.set_cookie('inactive_minutes',settings.SESSION_COOKIE_AGE)
		return response

	def process_view(self, request, view_func, view_args, view_kwargs):
		self.func_name 		=	view_func.__name__
		self.func_module 	= 	view_func.__module__

	def process_exception(self, request, exception):
		error = f'{datetime.datetime.now()}  [ERROR] {self.func_module}.{self.func_name}(): {exception}'
		loggerf(error)
		if not settings.DEBUG:
			return render(request,'error_page.html',{'error1':'Something seems to have gone wrong','error2':None})
		return None

