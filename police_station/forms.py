from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from .models import PoliceStation, PostalCode
import phonenumbers
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class PoliceStationCreationForm(forms.ModelForm):
    class Meta:
        model = PoliceStation
        fields = ('name', 'language', 'lat', 'lng')
        labels = {
                    'name' : 'Police Station Name',
        }
        widgets = {
                    'lat':  forms.HiddenInput(),
                    'lng':  forms.HiddenInput(),
        }
    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')
        if lat is None or lng is None or lat==0.0 or lng==0.0:
            raise forms.ValidationError('Please allow ACS to acess your location!')


class PoliceStationUserCreationForm(forms.ModelForm):
    confirm_password =     forms.CharField(
                                                                label           =   'Confirm Password',
                                                                error_messages  =   {'incomplete': 'Enter Password'},
                                                                widget          =   forms.PasswordInput(attrs={'placeholder':'Retype Password','class':'text-center form-control'}),
                                        ) 
    class Meta:
        model = UserModel
        fields = ('phone_number','email','password',)
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

class PostalCodeCreationForm(forms.Form):
    postal_codes = SimpleArrayField(forms.IntegerField(
                                                                label           =   'Postal Codes',
                                                                error_messages  =   {'invalid': 'Enter a valid Postal Code (Number)'},
                    ), 
                        delimiter=','
                        # error_messages = {}
                    )
    def clean(self):
        cleaned_data = super().clean()
        postal_codes = cleaned_data.get('postal_codes')
        existing_postal_codes = []
        if postal_codes:
            for postal_code in postal_codes:
                pc_qs = PostalCode.objects.filter(postal_code=postal_code)
                if pc_qs.exists():
                    pc_obj = pc_qs.first()
                    existing_postal_codes.append(str(pc_obj.postal_code)) 
            l = len(existing_postal_codes)    
            if l>0:        
                str1 = 'These Postal Codes ' if l>1 else 'This Postal Code'
                str2 = ' are already exist!' if l>1 else ' is already exist!'
                self.add_error('postal_codes', f'{str1} {", ".join(existing_postal_codes)} {str2}')
