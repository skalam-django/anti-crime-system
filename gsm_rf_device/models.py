from django.db import models
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from acs_users.models import IpWhitelist
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class GsmDeviceManager(models.Manager):
    def register(self, JSON_obj, ip):
        radio_freq_reciever = False
        ip_qs = IpWhitelist.objects.filter(ip=ip)
        if ip_qs.exists():
            ip_obj = ip_qs.first()
            if not ip_obj.client_type in [settings.CLIENT_GROUPS[1][0], settings.CLIENT_GROUPS[2][0]]:
                return None
            radio_freq_reciever = True if ip_obj.client_type==settings.CLIENT_GROUPS[2][0] else False
        else:
            return None    
        gsm_qs               =   self.filter(ip_id=int(ip_obj.id))
        gsm_obj              =   None
        if gsm_qs.exists():
            gsm_obj          =   gsm_qs.first()
        else:           
            gsm_obj          =   self.create(ip_id=int(ip_obj.id), radio_freq_reciever=radio_freq_reciever)
        if gsm_obj and gsm_obj.radio_freq_reciever==True:
            lat_lng             =   JSON_obj.get('lat_lng')
            locality_density    =   JSON_obj.get('locality_density') or 0
            languages           =   JSON_obj.get('lang') or []
            radius              =   JSON_obj.get('radius') or 0
            rf_qs               =   RfDevice.objects.get_or_create(device_id=GsmDevice(gsm_obj.id))
            rf_obj              =   rf_qs[0]
            if rf_obj:
                rf_obj.lat              =   lat_lng[0]
                rf_obj.lng              =   lat_lng[1]
                rf_obj.locality_density =   locality_density
                rf_obj.languages        =   languages
                rf_obj.radius           =   radius
                rf_obj.host             =   f'http://{ip}:80'
                rf_obj.save()   
        auth_qs             =   UserModel.objects.get_or_create(username=f"{settings.CLIENT_GROUPS[1][0]}-{gsm_obj.id}", client_id=int(gsm_obj.id))
        auth_obj            =   auth_qs[0]
        if auth_obj:
            group_qs        =   Group.objects.filter(name=str(ip_obj.client_type))
            if group_qs.exists():
                group_obj   =   group_qs.first()
                auth_obj.groups.add(group_obj)
        return [gsm_obj.id, auth_obj]

class GsmDevice(models.Model):
    ip                          =   models.ForeignKey(IpWhitelist, to_field='id', on_delete=models.CASCADE)
    pin_number                  =   PhoneNumberField(null=True, blank=True, region='IN')
    radio_freq_reciever         =   models.BooleanField(default=False)
    created_at                  =   models.DateTimeField(auto_now_add=True)
    updated_at                  =   models.DateTimeField(auto_now=True)    
    objects                     =   GsmDeviceManager()  
    class Meta:
        managed = True
        db_table = 'gsm_device'
        indexes = [
            models.Index(fields=['ip']),
        ]
    def __str__(self):
        return str(self.id)
         
class RfDevice(models.Model):
    device_id       =   models.ForeignKey(GsmDevice, to_field='id', on_delete=models.CASCADE)
    lat             =   models.FloatField(default=0.0)
    lng             =   models.FloatField(default=0.0)
    locality_density=   models.IntegerField(default=0)
    languages       =   ArrayField(models.CharField(max_length=5, null=True, blank=True, default='en'), null=True, blank=True)
    radius          =   models.FloatField(default=0.0)
    host            =   models.URLField()
    created_at      =   models.DateTimeField(auto_now_add=True)
    updated_at      =   models.DateTimeField(auto_now=True)  
    class Meta:
        managed         =   True
        db_table        =   'rf_device'
        unique_together =   (('device_id'),)
        indexes         =   [
                                models.Index(fields=['device_id', 'lat', 'lng', 'radius']),
        ]        
    def __str__(self):
        return str(self.device_id)
