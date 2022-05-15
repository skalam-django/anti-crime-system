from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from gsm_rf_device.models import GsmDevice, RfDevice
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class EventsManager(models.Manager):
    def log(self, device_id, JSON_obj):
        event_id    =   1 #JSON_obj.get('event_id')
        user_id     =   1 #JSON_obj.get('user_id')
        lat         =   JSON_obj.get('lat')
        lng         =   JSON_obj.get('lng')
        evt_qs      =   self.filter(id=event_id, active=True)
        evt_obj     =   None
        if not evt_qs.exists():
            evt_obj      =   self.create(device_id=GsmDevice(id=device_id), user_id=UserModel(user_id))
        else:    
            evt_obj = evt_qs[0] 
        if evt_obj:
            evt_obj.lat = lat
            evt_obj.lng = lng
            evt_obj.save()
        rf_qs =   self.get_gsmfrt(lat, lng)
        return [evt_obj.id, rf_qs] 

    def gsmrft(self, event_id):
        evt_qs  =   self.filter(id=int(event_id), active=True)
        rf_qs   =   None
        if evt_qs.exists():
            evt_obj =   evt_qs.first()
            lat     =   evt_obj.lat
            lng     =   evt_obj.lng
            rf_qs =  self.get_gsmfrt(lat, lng)
        return rf_qs
        
    def get_gsmfrt(self, lat, lng):
        query_sql = "SELECT * FROM rf_device WHERE earth_box(ll_to_earth(%s,%s), rf_device.radius) @> ll_to_earth(rf_device.lat, rf_device.lng) ORDER BY earth_distance(ll_to_earth(%s,%s),ll_to_earth(rf_device.lat,rf_device.lng))" %(lat, lng, lat, lng)
        rf_qs = RfDevice.objects.raw(query_sql)
        return rf_qs  

class Events(models.Model):
    device_id       =   models.ForeignKey(GsmDevice, on_delete=models.CASCADE, null=True)
    user_id         =   models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)
    lat             =   models.FloatField(default=0.0)
    lng             =   models.FloatField(default=0.0)    
    active          =   models.BooleanField(default=True)
    created_at      =   models.DateTimeField(auto_now_add=True)
    updated_at      =   models.DateTimeField(auto_now=True)  
    objects         =   EventsManager()
    class Meta:
        managed = True
        db_table = 'events'
        indexes = [
            models.Index(fields=['device_id','user_id']),
        ]        
    def __str__(self):
        return str(self.id)    


class EventHistory(models.Model):
    event_id            =   models.ForeignKey(Events, on_delete=models.CASCADE, null=True)
    lat                 =   models.FloatField(default=0.0)
    lng                 =   models.FloatField(default=0.0)
    created_at          =   models.DateTimeField(auto_now_add=True)
    updated_at          =   models.DateTimeField(auto_now=True)  
    class Meta:
        managed = True
        db_table = 'event_history'
        indexes = [
            models.Index(fields=['event_id']), 
        ]        
    def __str__(self):
        return str(self.id)

class RequestCancellationManager(models.Manager):
    def cancel(self):
        pass

class RequestCancellation(models.Model):
    event_id            =   models.ForeignKey(Events, on_delete=models.CASCADE, null=True)
    canceled_by         =   models.CharField(max_length=20)
    cancellation_reason =   models.CharField(max_length=20, null=True, blank=True)
    created_at          =   models.DateTimeField(auto_now_add=True)
    updated_at          =   models.DateTimeField(auto_now=True)  
    objects             =   RequestCancellationManager()    
    class Meta:
        managed = True
        db_table = 'request_cancellation'
        indexes = [
            models.Index(fields=['event_id','canceled_by']),
        ]        

    def __str__(self):
        return str(self.id)    
