from __future__ import absolute_import

from . import backend
from . import settings
from . models import SmsRecipient
from django.http import HttpResponse


def sms_status_callback(request):
    '''
    This view function process request from sms gateway with SMS statuses
    and saves them to database.
    '''
    if settings.CALLBACK_IPS and \
       request.META['REMOTE_ADDR'] not in settings.CALLBACK_IPS:
        return HttpResponse(status=403)
    if not hasattr(backend, 'sms_status_callback'):
        raise NotImplementedError('Module %s does not support sms_callback' %
                                  settings.BACKEND)
    for remote_id, status, status_text in backend.sms_status_callback(request):
        SmsRecipient.objects.get(remote_id=remote_id).set_status(status, status_text)
    return HttpResponse(status=200)
