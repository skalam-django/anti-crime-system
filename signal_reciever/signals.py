def create_event_history(sender, instance, created, **kwargs):
		try:
			from .models import EventHistory
			event_hist_obj	= 	EventHistory.objects.create(event_id=instance, lat=float(instance.lat), lng=float(instance.lng))
		except Exception as e:
			print('error: ',e)
	