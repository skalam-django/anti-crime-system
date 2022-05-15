import json
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views import View
from .forms import NotiPushForm, SubscriptionForm
from signal_reciever.models import Events


class SaveSubscription(View):
    def post(self, request):
        try:
            post_data1 = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponse(status=400)
        groups   = post_data1.get('group')
        status_type = None
        for group in groups:
            post_data = post_data1.copy()
            post_data['group'] = group
            subscription_data = self.process_subscription_data(post_data)
            subscription_form = SubscriptionForm(subscription_data)
            notipush_form = NotiPushForm(post_data)
            if subscription_form.is_valid() and notipush_form.is_valid():
                web_push_data = notipush_form.cleaned_data
                status_type = web_push_data.pop("status_type")
                group_name = web_push_data.pop("group")
                if request.user.is_authenticated or group_name:
                    subscription = subscription_form.get_or_save()
                    notipush_form.save_or_delete(subscription=subscription, user=request.user, status_type=status_type, group_name=group_name)

        if status_type == 'subscribe':
            return HttpResponse(status=201)
        elif "unsubscribe":
            return HttpResponse(status=202)
        return HttpResponse(status=400)     

    def process_subscription_data(self, post_data):
        subscription_data = post_data.pop("subscription", {})
        keys = subscription_data.pop("keys", {})
        subscription_data.update(keys)
        subscription_data["browser"] = post_data.pop("browser")
        return subscription_data


class ClickedUsers(TemplateView):
    template_name = 'clicked_users.html'
    def dispatch(self, request, *args, **kwargs):
        response = super(ClickedUsers, self).dispatch(request, *args, **kwargs)
        print('Clicked Username : ', request.user)
        return response

class UserToVictimPath(View):
    def get(self, request):
        event_id    =   request.GET.get('eid')
        timestamp   =   request.GET.get('timestamp')
        user_lat    =   request.GET.get('user_lat') or 0.0
        user_lng    =   request.GET.get('user_lng') or 0.0
        evt_qs      =   Events.objects.filter(id=int(event_id), active=True)
        if evt_qs.exists():
            evt_obj = evt_qs.first()
            victim_lat  =   evt_obj.lat
            victim_lng  =   evt_obj.lng
            return HttpResponse(json.dumps({'url':f'https://www.google.com/maps?saddr=Current+Location&daddr={victim_lat},{victim_lng}'}))
        return HttpResponse(status=404)    

        # , created_at=datetime.fromtimestamp(float(timestamp))

        # {user_lat},{user_lng}