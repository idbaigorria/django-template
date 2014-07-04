from .base import *

DEBUG = True

try:
	from .local import *
except ImportError:
	pass


SMSGATE_CREDENTIALS = {
    'api_id': 99,
    'login': 'vasya',
    'password': 'pupkin',
}
SMSGATE_HTTP_TIMEOUT = 5
