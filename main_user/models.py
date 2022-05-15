from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from gsm_rf_device.models import GsmDevice
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
UserModel = get_user_model()

class MainUserManager(models.Manager):
    def register(self, JSON_obj):
        uid             =   JSON_obj.get('uid')
        password        =   JSON_obj.get('password')
        first_name      =   JSON_obj.get('first_name')
        last_name       =   JSON_obj.get('last_name')
        phone_number    =   JSON_obj.get('phone_number')
        email           =   JSON_obj.get('email')
        em_contact      =   JSON_obj.get('emergency_contacts') or []
        device_id       =   JSON_obj.get('device_id')
        mu_qs           =   self.filter(uid=uid)
        if mu_qs.exists():
            mu_obj      =   mu_qs.first()
        else:
            mu_obj      =   self.create(uid=uid, emergency_contacts=em_contact)
        if device_id:    
            gsm_qs      =   GsmDevice.objects.filter(id=int(device_id))
            if gsm_qs.exists():                
                mu_obj.device_id    =   int(device_id)
        mu_obj.emergency_contacts   =   em_contact
        mu_obj.save()
        auth_qs                     =   UserModel.objects.get_or_create(username=f"{settings.CLIENT_GROUPS[0][0]}-{mu_obj.id}", client_id=int(mu_obj.id))          
        auth_obj                    =   auth_qs[0]
        if auth_obj:
            auth_obj.password       =   make_password(password)
            auth_obj.first_name     =   first_name
            auth_obj.last_name      =   last_name
            auth_obj.email          =   email
            auth_obj.phone_number   =   phone_number
            auth_obj.save()
            group_qs                =   Group.objects.filter(name=settings.CLIENT_GROUPS[0][0])
            if group_qs.exists():
                group_obj = group_qs.first()
                auth_obj.groups.add(group_obj)
        return auth_obj 

class MainUser(models.Model):
    uid                         =   models.CharField(unique=True, max_length=50)
    device_id                   =   models.IntegerField(null=True, blank=True)
    emergency_contacts          =   ArrayField(PhoneNumberField(null=True, blank=True), null=True, blank=True)
    created_at                  =   models.DateTimeField(auto_now_add=True)
    updated_at                  =   models.DateTimeField(auto_now=True)
    objects                     =   MainUserManager()
    class Meta:
        managed         =   True
        db_table        =   'main_user'
        unique_together =   (('uid', 'device_id'),)
        indexes         =   [
            models.Index(fields=['uid', 'device_id']),
        ]
    def __str__(self):
        return str(self.uid)