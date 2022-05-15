from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.views import View
from .forms import MainUserCreationForm, MainUserUserCreationForm, GsmDeviceAttachForm, validate_device_id
from .models import MainUser
from gsm_rf_device.models import GsmDevice
from django.contrib.auth.mixins import LoginRequiredMixin
from generalize.views import Generalize
from ACS.utils import GeoLocation
import json

class MainUserRegistration(TemplateView): #IpValidationMixin, UserAgentValidationMixin, 
	user_type 		= 	'main_user'
	template_name 	= 	'main_user/registration.html'
	def get(self, request):
		mu_form 	= 	MainUserCreationForm(prefix='mu')
		user_form 	= 	MainUserUserCreationForm(prefix='user')
		gsm_form	=	GsmDeviceAttachForm(prefix='gsm')
		return render(request, self.template_name, {'mu_form':mu_form, 'user_form':user_form, 'gsm_form':gsm_form})
	def post(self, request):
		mu_form 	= 	MainUserCreationForm(request.POST, prefix='mu')
		user_form 	= 	MainUserUserCreationForm(request.POST, prefix='user')
		gsm_form	=	GsmDeviceAttachForm(request.POST, prefix='gsm')
		if mu_form.is_valid()==True and user_form.is_valid()==True:
			mu_json 	= 	mu_form.cleaned_data
			user_json 	= 	user_form.cleaned_data
			JSON_obj 	= 	dict()
			JSON_obj.update(mu_json)
			JSON_obj.update(user_json)
			if gsm_form.is_valid()==True:
				validate = validate_device_id(gsm_form.cleaned_data.get('url'))
				if len(validate)>0:
					valid = validate[0]
					if valid==True:
						gsm_json 	= 	dict()
						gsm_json['device_id'] 	= 	validate[1]
						JSON_obj.update(gsm_json)
			print(JSON_obj, 'JSON_obj')			
			auth_obj 		= 	MainUser.objects.register(JSON_obj)
			return redirect(reverse('main_user:home'))
		return render(request, self.template_name, {'mu_form':mu_form, 'user_form':user_form, 'gsm_form':gsm_form})



# class MainUserRegistration1(APIView):
# 	authentication_classes 		= 	(TokenAuthentication,)
# 	permission_classes 			= 	[IsAuthenticated,]
# 	def post(self, request):
# 		JSON_obj 	= 	json.loads(request.body)
# 		gsm_obj 	= 	GsmDevice.objects.register(JSON_obj, self.ip)
# 		auth_qs 	=	UserModel.objects.filter(client_id=gsm_obj.id)
# 		token 		=	None
# 		if auth_qs.exist():
# 			auth_obj = auth_qs.first()
# 			token_qs = Token.objects.filter(user=auth_obj)
# 			if token_qs.exists():
# 				token_obj 	= 	token_qs.first()
# 				token 		= 	token_obj.key
# 		return Response({'token' : token})  			


class VerifyDeviceId(View):
	def get(self, request):
		url = request.GET.get('url')
		error = 'Something went wrong!'
		validate = validate_device_id(url)
		if len(validate)>0:
			valid = validate[0]
			if valid==True:
				device_id = validate[1]
				if not device_id is None:
					print('success')
					return HttpResponse(json.dumps({'success':True, 'url':url}))
			else:
				error = validate[1]	
		print('success 1')	
		return HttpResponse(json.dumps({'success':False,'error':error}))	


class GetLocation(LoginRequiredMixin, TemplateView):
	template_name = 'main_user/get_location.html'
	def post(self, request):
		lat = request.POST.get('user_lat')
		lng = request.POST.get('user_lng')
		if lat is None or lng is None:
			return HttpResponse(json.dumps({'status':201}))
		gen_obj = Generalize(request=request)
		response = HttpResponse(json.dumps({'status':200, 'url':reverse('main_user:home')}))
		gen_obj.store_data(response,['lat','lng'],[lat,lng],default_storage='both')
		return response

class Home(LoginRequiredMixin, GeoLocation, TemplateView):
	template_name = 'main_user/home.html'
	# def get(self, request):
		
	# 	return super().get(request)
	def get_context_data(self, *args, **kwargs):
		gen_obj = Generalize(request=self.request)
		lat = gen_obj.retrive_data('lat')
		lng = gen_obj.retrive_data('lng')
		if lat is None or lng is None:
			return redirect(reverse('main_user:get_location'))
		context = super(Home,self).get_context_data(**kwargs)
		self.get_address(f"{lat}, {lng}")
		notipush = {'group' : f'{self.request.user}_{self.postal_code}'}
		print(notipush,'notipush')
		context.update({"notipush" : notipush})
		return context

		
