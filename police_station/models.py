from django.db import models
from django.contrib.auth.models import Group
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
UserModel = get_user_model()


class PoliceStationManager(models.Manager):
    def register(self, JSON_obj):
        name                =   JSON_obj.get('name')
        lat                 =   JSON_obj.get('lat')
        lng                 =   JSON_obj.get('lng')
        language            =   JSON_obj.get('language')
        phone_number        =   JSON_obj.get('phone_number')
        postal_codes        =   JSON_obj.get('postal_codes')
        password            =   JSON_obj.get('password')
        ps_qs               =   self.get_or_create(name=name)
        ps_obj              =   ps_qs[0]
        auth_obj            =   None
        if ps_obj:
            auth_qs         =   UserModel.objects.get_or_create(username=f"{settings.CLIENT_GROUPS[3][0]}-{ps_obj.id}", client_id=int(ps_obj.id))
            auth_obj        =   auth_qs[0]
            if auth_obj:
                auth_obj.phone_number   =   phone_number
                auth_obj.first_name, auth_obj.last_name  =  settings.CLIENT_GROUPS[3][1].split(' ')
                if not password is None:
                    auth_obj.password = make_password(password)
                auth_obj.save()
                group_qs            =   Group.objects.filter(name=settings.CLIENT_GROUPS[3][0])
                if group_qs.exists():
                    group_obj = group_qs.first()
                    auth_obj.groups.add(group_obj)
            ps_obj.lat          =   lat
            ps_obj.lng          =   lng
            ps_obj.language     =   language or 'en'
            ps_obj.save()
            postal_codes        =   [postal_codes] if type(postal_codes)!=list else postal_codes
            for postal_code in postal_codes:
                from police_station.models import PostalCode, PoliceStation
                pc_qs               =   PostalCode.objects.get_or_create(postal_code=postal_code, police_station=PoliceStation(ps_obj.id))
        return auth_obj

class PoliceStation(models.Model):
    name            =   models.CharField(unique=True, max_length=300)
    lat             =   models.FloatField(default=0.0)
    lng             =   models.FloatField(default=0.0)
    language        =   models.CharField(max_length=5, null=True, blank=True, default='en')
    created_at      =   models.DateTimeField(auto_now_add=True)
    updated_at      =   models.DateTimeField(auto_now=True)
    objects         =   PoliceStationManager()
    class Meta:
        managed         =   True
        db_table        =   'police_station'
        indexes         =   [
                                models.Index(fields=['lat', 'lng', 'name']),
        ]        
    def __str__(self):
        return str(self.name)

class PostalCode(models.Model):
    postal_code     =   models.CharField(unique=True, max_length=300)
    police_station  =   models.ForeignKey(PoliceStation, to_field='id', on_delete=models.CASCADE)
    created_at      =   models.DateTimeField(auto_now_add=True)
    updated_at      =   models.DateTimeField(auto_now=True)
    class Meta:
        managed         =   True
        db_table        =   'postal_code'
        unique_together =   (('postal_code', 'police_station'),)
        indexes         =   [
                                models.Index(fields=['postal_code', 'police_station']),
        ]        
    def __str__(self):
        return str(self.postal_code)