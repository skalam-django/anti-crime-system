from django import forms
import phonenumbers
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from gsm_rf_device.models import GsmDevice
from .models import MainUser
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MainUserCreationForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class': f'form-control field {self.prefix}'})
	class Meta:
		model 	= MainUser
		fields 	= ('uid', 'emergency_contacts')
		labels 	= {
			'uid' : 'Aadhaar Id / Voter Id',
		}
		error_messages = {
			'uid': {
				'unique': 'This Aadhaar Id / Voter Id already exists!',
			},
		}


class MainUserUserCreationForm(forms.ModelForm):
	confirm_password =     forms.CharField(
                                                            label           =   'Confirm Password',
                                                            error_messages  =   {'incomplete': 'Enter Password'},
                                                            widget          =   forms.PasswordInput(attrs={'placeholder':'Retype Password','class':'text-center form-control'}),
                                    ) 

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class': f'form-control field {self.prefix}'})	

	class Meta:
		model = UserModel
		fields = ('first_name', 'last_name', 'phone_number', 'email', 'password',)
		labels = {
		            'phone_number' : 'Contact Number',
		}
		widgets = {
		            'password'          :   forms.PasswordInput(),
		}

	def clean(self):
		super().clean()
		password_field          =   self.fields.get('password')
		password                =   password_field.widget.value_from_datadict(self.data, self.files, self.add_prefix('password'))
		confirm_password_field  =   self.fields.get('confirm_password')
		confirm_password        =   confirm_password_field.widget.value_from_datadict(self.data, self.files, self.add_prefix('confirm_password'))
		if password!=confirm_password:
			self.add_error('confirm_password', 'Passwords mismatch!')

class GsmDeviceAttachForm(forms.Form):
	url = forms.URLField(
							required=	False, 
							widget 	= 	forms.HiddenInput(),
						)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for field in iter(self.fields):
			self.fields[field].widget.attrs.update({'class': f'form-control field {self.prefix}'})

	def clean(self):
		cleaned_data = super().clean()
		url = cleaned_data.get('url')
		if not url is None and len(url)>0:
			validate = validate_device_id(url)
			if len(validate)>0:
				valid = validate[0]
				if valid==False:
					error = validate[1]
					raise ValidationError(error)
			else:		
				raise ValidationError('Something went wrong with the QR code!')

def validate_device_id(url):
	device_id = extract_device_id(url)
	if device_id:
		gsm_qs = GsmDevice.objects.filter(id=int(device_id), radio_freq_reciever=False)
		if gsm_qs.exists():
			user_qs = MainUser.objects.filter(device_id=int(device_id))
			if user_qs.exists():
				return [False, 'This QR code has already been used!']
			return [True, device_id]
		else:
			return [False, 'Invalid QR code!']
	else:
		return [False, 'Invalid QR code!']

def extract_device_id(url):
	device_id = None
	if url:
		url_obj 	=	urlparse(url)
		scheme 		=	url_obj.scheme
		netloc		=	url_obj.netloc
		path 		=	url_obj.path
		query 		=	url_obj.query
		if scheme and scheme=='https':
			if netloc and netloc=='1fe28566.ngrok.io':
				if path and path=='/main_user/complete_registration/':
					if query and 'did=' in query:
						device_id = query.split('did=')[1]			
	return device_id        
