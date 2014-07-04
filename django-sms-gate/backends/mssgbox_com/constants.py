from smsgate.constants import *
from django.utils.translation import ugettext_noop as _

ERROR_CODES = {
  '1': _('Authentication failed'),
  '2': _('Unknown username'),
  '3': _('Invalid password'),
  '4': _('Invalid or missing API ID'),
  '5': _('Invalid or expired session ID'),
  '6': _('Account locked'),
  '7': _('IP Lockdown violation'),
  '101': _('Invalid or missing parameters'),
  '102': _('Unknown message UID'),
  '103': _('Missing message UID'),
  '104': _('Invalid destination address'),
  '105': _('Invalid source address'),
  '106': _('Empty message'),
  '107': _('Invalid sender id'),
  '108': _('Invalid delivery time'),
  '120': _('Cannot route message'),
  '121': _('Destination mobile number blocked'),
  '201': _('No credit left'),
  '202': _('Max allowed credit'),
  '301': _('Internal error'),
}

STATUS_CODES = {
  '1': (STATUS_UNSENT, _('Message unknown')),
  '2': (STATUS_REMOTE_QUEUED, _('Message queued')),
  '3': (STATUS_DELIVERED, _('Delivered to gateway')),
  '4': (STATUS_DELIVERED, _('Recieved by recipient')),
  '5': (STATUS_UNDELIVERED, _('Error with message')),
  '6': (STATUS_CANCELED, _('User cancelled message delivery')),
  '7': (STATUS_UNDELIVERED, _('Error delivering message')),
  '8': (STATUS_SENT, _('OK')),
  '9': (STATUS_UNDELIVERED, _('Routing error')),
  '10': (STATUS_EXPIRED, _('Message expired')),
  '11': (STATUS_REMOTE_QUEUED, _('Message queued for later delivery')),
  '12': (STATUS_UNSENT, _('Out of credit')),
}
