from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password, is_password_usable, make_password



class IpWhitelist(models.Model):
    ip                  =   models.CharField(unique=True, max_length=20) #models.GenericIPAddressField(primary_key = True, unique=True, max_length=20)
    client_type         =   models.CharField(max_length=5, choices=settings.CLIENT_GROUPS, default=settings.CLIENT_GROUPS[0][0])
    created_at          =   models.DateTimeField(auto_now_add=True)
    updated_at          =   models.DateTimeField(auto_now=True)
    class Meta:
        managed         =   True
        db_table        =   'ip_white_list'
        indexes         =   [
                                models.Index(fields=['ip','client_type']),
        ]
    def __str__(self):
        return str(self.ip)


# class MobileAppManager(models.Manager):
#     def register(self, JSON_obj):
#         app_name        =   JSON_obj.get('app_name')
#         app_version     =   JSON_obj.get('app_version')
#         app_description =   JSON_obj.get('app_description')
#         app_build_by    =   JSON_obj.get('app_build_by')
#         ma_qs           =   self.get_or_create(app_name=app_name, app_version=app_version, app_build_by=app_build_by)
#         ma_obj          =   ma_qs[0]
#         auth_obj        =   None
#         if ma_obj:
#             auth_qs     =   AuthUser.objects.get_or_create(username=f"{settings.CLIENT_GROUPS[3][0]}-{ma_obj.id}", client_id=int(ma_obj.id))
#             auth_obj    =   auth_qs[0]
#             if auth_obj:
#                 auth_obj.first_name, auth_obj.last_name  =  settings.CLIENT_GROUPS[3][1].split(' ')
#                 auth_obj.save()
#                 group_qs            =   Group.objects.filter(name=settings.CLIENT_GROUPS[3][0])
#                 if group_qs.exists():
#                     group_obj = group_qs.first()
#                     auth_obj.groups.add(group_obj)
#             ma_obj.app_description = app_description
#             ma_obj.save()
#         return auth_obj



# class MobileApp(models.Model):
#     app_name        =   models.CharField(max_length=20)
#     app_version     =   models.CharField(max_length=10)
#     app_description =   models.CharField(max_length=100, default='')    
#     app_build_by    =   models.CharField(max_length=30)
#     created_at      =   models.DateTimeField(auto_now_add=True)
#     updated_at      =   models.DateTimeField(auto_now=True)
#     objects         =   MobileAppManager()  
#     class Meta:
#         managed         =   True
#         db_table        =   'mobile_app'
#         unique_together =   (('app_name', 'app_version', 'app_build_by'),)
#         indexes         =   [
#                                 models.Index(fields=['app_name', 'app_build_by']),
#         ]        
#     def __str__(self):
#         return f"{self.app_name}-{self.app_version}"


class AuthUser(AbstractUser):
    client_id                   =   models.IntegerField()
    phone_number                =   PhoneNumberField(null=True, blank=True, region='IN')
    is_verified                 =   models.BooleanField(default=False)
    class Meta:
        managed = True
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['username', 'phone_number', 'email', 'client_id']),
        ]

    def __str__(self):
        return str(self.username)
    def save(self, *args, **kwargs):
        if self.is_superuser==True:
            self.client_id=1
        super(AuthUser, self).save(*args, **kwargs)




# class MobileAppUsersManager(models.Manager):
#     def register(self, JSON_obj):
#         pass
# class MobileAppUsers(models.Model):
#     app_id          =   models.ForeignKey(MobileApp, to_field='id', on_delete=models.CASCADE)
#     user_id         =   models.ForeignKey(AuthUser, to_field='id', on_delete=models.CASCADE)
#     lat             =   models.FloatField(default=0.0)
#     lng             =   models.FloatField(default=0.0)
#     created_at      =   models.DateTimeField(auto_now_add=True)
#     updated_at      =   models.DateTimeField(auto_now=True)    
#     class Meta:
#         managed         =   True
#         db_table        =   'mobile_app_users'
#         unique_together =   (('app_id', 'user_id'),)
#         indexes         =   [
#                                 models.Index(fields=['app_id', 'user_id']),
#         ]        
#     def __str__(self):
#         return f"{self.app_id}-{self.user_id}"


class OtpManager(models.Manager):
    def otp(self,phone_number):
        otp_qs = self.filter(phone_number=str(phone_number), is_used=False, expiry_at__gte=datetime.datetime.now()).order_by('-created_at')
        if otp_qs.exists():
            otp_obj  = otp_qs.first()
        else:
            otp_obj = self.create(phone_number=phone_number, otp=get_random_string(settings.OTP['OTP_LENGTH'],'123456789'))
        return otp_obj.otp
    def used(self,phone_number):
        otp_qs = self.filter(phone_number=str(phone_number), is_used=False).order_by('-created_at')
        if otp_qs.exists():
            otp_obj         =   otp_qs.first()
            otp_obj.is_used =   True
            otp_obj.save()
            return True
        return False    

class OTP(models.Model):
    phone_number=   PhoneNumberField()
    otp         =   models.CharField(max_length=settings.OTP['OTP_LENGTH'])
    is_used     =   models.BooleanField(default=False)
    expiry_at   =   models.DateTimeField()
    created_at  =   models.DateTimeField(auto_now_add=True)
    updated_at  =   models.DateTimeField(auto_now=True)

    objects     =   OtpManager()

    class Meta:
        managed = True
        db_table = 'otpdata'
        indexes = [
            models.Index(fields=['phone_number', 'is_used', 'expiry_at']),
        ]       
    def save(self, *args, **kwargs):
        self.expiry_at = datetime.datetime.now() + datetime.timedelta(0, settings.OTP['OTP_EXPIRY'])
        return super().save(*args, **kwargs)