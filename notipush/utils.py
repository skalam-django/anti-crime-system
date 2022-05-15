from django.conf import settings
from django.forms.models import model_to_dict
from django.urls import reverse

from pywebpush import WebPushException, webpush


def send_notification_to_user(user, payload, ttl=0):
    push_infos = user.notipush_info.select_related("subscription")
    for push_info in push_infos:
        _send_notification(push_info.subscription, payload, ttl)

def send_notification_to_group(group_name, payload, ttl=0):
    from .models import Group
    push_infos_qs = Group.objects.filter(name=group_name)
    if push_infos_qs.exists():
        push_infos_obj  =   push_infos_qs.first()
        push_infos      =   push_infos_obj.notipush_info.select_related("subscription")
        for push_info in push_infos:
            _send_notification(push_info.subscription, payload, ttl)


def send_to_subscription(subscription, payload, ttl=0):
    return _send_notification(subscription, payload, ttl)

def _send_notification(subscription, payload, ttl):
    subscription_data = _process_subscription_info(subscription)
    vapid_data = {}

    notipush_settings = getattr(settings, 'NOTIPUSH_SETTINGS', {})
    vapid_private_key = notipush_settings.get('VAPID_PRIVATE_KEY')
    vapid_admin_email = notipush_settings.get('VAPID_ADMIN_EMAIL')
    if vapid_private_key:
        vapid_data = {
            'vapid_private_key': vapid_private_key,
            'vapid_claims': {"sub": "mailto:{}".format(vapid_admin_email)}
        }

    try:
        req = webpush(subscription_info=subscription_data, data=payload, ttl=ttl, **vapid_data)
        return req
    except WebPushException as e:
        if e.response.status_code == 410:
            subscription.delete()
        else:
            raise e


def _process_subscription_info(subscription):
    subscription_data = model_to_dict(subscription, exclude=["browser", "id"])
    endpoint = subscription_data.pop("endpoint")
    p256dh = subscription_data.pop("p256dh")
    auth = subscription_data.pop("auth")
    return {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth}
    }

def get_templatetag_context(context):
    request = context['request']
    vapid_public_key = getattr(settings, 'NOTIPUSH_SETTINGS', {}).get('VAPID_PUBLIC_KEY', '')
    group = context.get('notipush', {}).get('group')
    data = {'group': group if (group and type(group)==list) else ([group] if group else [None]),
            'user': getattr(request, 'user', None),
            'vapid_public_key': vapid_public_key,
            'notipush_save_url': reverse('save_notipush_info')
            }   
    return data
