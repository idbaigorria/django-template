'''
Module for working with SMS on different gateways.
'''

from __future__ import absolute_import

from . import settings
from . constants import *
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.translation import ugettext_noop as _

backend = import_module(settings.BACKEND)
if not hasattr(backend, 'send_sms'):
    raise ImproperlyConfigured('Module %s doesn\'t implement send_sms' %
                               settings.BACKEND)


def _get_callback_url(callback):
    if callback == True:
        if settings.CALLBACK_URL:
            return settings.CALLBACK_URL
        else:
            raise ImproperlyConfigured('You didn\'t set SMSGATE_CALLBACK_URL'
                                       'in your settings')
    return callback


def send_mass_sms(datatuple, sender=settings.SENDER, callback=False,
                  fail_silently=False):
    '''
    Send SMS messages through gateway.
    Given a datatuple of (text, phones, remote_id) (remote_id is optional).
    Yields result for each SMS.

    If fail_silently is True, exception is suppressed and generation stops.
    For rest see smsgate.send_sms docstring.
    '''
    if len(datatuple) == 0:
        return
    callback_url = _get_callback_url(callback)
    try:
        if hasattr(backend, 'send_mass_sms'):
            for result in backend.send_mass_sms(datatuple, sender=sender,
                                                callback_url=callback_url):
                yield result
        else:
            # If backend doesn't have interface for mass sending - emulate it
            for args in datatuple:
                # Checking if remote_id is in datatuple
                if len(args) < 3:
                    args[2] = None
                yield backend.send_sms(args[0], args[1], args[2], sender=sender,
                                       callback_url=callback_url)
    except:
        if not fail_silently:
            raise


def send_sms(message, recipient_list, remote_id=None, sender=settings.SENDER,
             callback=False, fail_silently=False):
    '''
    Send SMS message through gateway.
    Returns tuple of (remote_id,status,status_text) for each recipient in
    recipient_list.

    recipient_list is tuple of phones in international format, without +.

    You may specify remote_id. You need this ONLY if your gateway doesn't
    support id generation by itself, AND you need to get SMS status later.
    In that case backend would generate unique id based on this value and phone
    number.

    if no sender specified, SMSGATE_SENDER is used. Note that it must be string,
    supported (or required) by your gateway.

    You may specify callback url, or set callback=True to use
    SMSGATE_CALLBACK_URL. By default callback is False.
    (Note that on some servers callback url must be set on serverside).

    If fail_silently is True, exception is suppressed and unknown status
    returned on fail.
    '''
    callback_url = _get_callback_url(callback)
    try:
        return backend.send_sms(message, recipient_list, remote_id=remote_id,
                                sender=sender, callback_url=callback_url)
    except:
        if not fail_silently:
            raise
        else:
            return (None, STATUS_UNKNOWN, _('Error occured while sending SMS'))


def get_sms_statuses(remote_ids, fail_silently=False):
    '''
    Retrieve SMS statuses from gateway.
    Yields (status, status_text), corresponding to tuple of given remote_ids.

    If fail_silently is True, exception is suppressed and generation stops.
    '''
    if not hasattr(backend, 'get_sms_statuses'):
        raise NotImplementedError('Module %s does not support retrieving SMS '
                                  'statuses' % settings.BACKEND)
    if len(remote_ids) == 0:
        return
    try:
        for result in backend.get_sms_statuses(remote_ids):
            yield result
    except:
        if not fail_silently:
            raise


def sms_admins(message, fail_silently=False):
    '''
    Send SMS message to admins, specified in SMSGATE_ADMINS_PHONES setting.
    Returns smsgate.send_sms function result.
    '''
    if settings.ADMINS_PHONES:
        return send_sms(message, settings.ADMINS_PHONES,
                        fail_silently=fail_silently)


def sms_managers(message, fail_silently=False):
    '''
    Send SMS message to managers, specified in SMSGATE_MANAGERS_PHONES setting.
    Returns smsgate.send_sms function result.
    '''
    if settings.MANAGERS_PHONES:
        return send_sms(message, settings.MANAGERS_PHONES,
                        fail_silently=fail_silently)
