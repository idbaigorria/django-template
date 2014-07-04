from __future__ import absolute_import

from django.conf import settings
from . constants import *

def _get(name, default):
    return getattr(settings, 'SMSGATE_' + name, default)

# Please use this dictionary to set authentication parameters,
# required by your backend.
CREDENTIALS = _get('CREDENTIALS', {})

# Please specify existing backend or your backend module,
# for example 'myapp.sms_backend'
BACKEND = _get('BACKEND', 'django-sms-gate.backends.mssgbox_com.http_v1')

# Send SMS (or not) on saving in database.
# You may turn it off to send messages by cron.
# Note that sending invokes only on admin page and Sms.create method.
SEND_ON_SAVE = _get('SEND_ON_SAVE', True)

# Callback URL for recieving SMS statuses from gateways.
# If you want to use this, you should include view sms_status_callback
# to urls.py of your project.
#
# EXAMPLE:
# settings.py: SMSGATE_CALLBACK_URL = "http://example.com/MY_CALLBACK_URL"
# urls.py: (r'^MY_CALLBACK_URL', 'smsgate.views.sms_status_callback'),

# See also CALLBACK_IPS if you are using gateway on remote server.
# Note, that on some gateways CALLBACK_URL is also configured on server side.
CALLBACK_URL = _get('CALLBACK_URL', False)

# Allow connection to callback view only for specified IPs.
# Set to None if you want to disable IP checking (NOT RECOMMENDED).
CALLBACK_IPS = _get('CALLBACK_IPS', ('127.0.0.1',))

# After this days count of no delivery report SMS status set to expired.
STATUS_MAX_DAYS = 60

# Default sender.
SENDER = _get('SENDER', 'django-smsgate')

# Specify proxy URL like: http://proxy_user:proxy_password@proxy_ip:proxy_port
HTTP_PROXY = _get('HTTP_PROXY', None)

# Timeout for HTTP request. Note that this works only for Python 2.6+.
HTTP_TIMEOUT = _get('HTTP_TIMEOUT', None)
# Set timeouts only for Python 2.6+
from sys import version_info
if version_info <= (2, 6):
    HTTP_TIMEOUT = None

# Administrators phone numbers (used by smsgate.sms_admins)
ADMINS_PHONES = _get('ADMINS_PHONES', ())

# Managers phone numbers (used by smsgate.sms_managers)
MANAGERS_PHONES = _get('MANAGERS_PHONES', ())

# Colors of SMS statuses.
# Used in admin page, and SmsRecipient.status_color method.
STATUS_COLORS = _get('STATUS_COLORS', {
  STATUS_QUEUED: 'blue',
  STATUS_CANCELED: 'red',
  STATUS_SENT: 'yellow',
  STATUS_UNSENT: 'red',
  STATUS_UNKNOWN: 'red',
  STATUS_REMOTE_QUEUED: 'blue',
  STATUS_DELIVERED: 'green',
  STATUS_UNDELIVERED: 'red',
  STATUS_EXPIRED: 'red',
})

# Success (not failed) statuses. Required only for statistics reason.
SUCCESS_STATUSES = (STATUS_SENT, STATUS_DELIVERED)
