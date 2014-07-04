from smsgate.utils import http_request
from smsgate.exceptions import SmsGateError, SmsGateUnknownResponse
from smsgate.settings import *
from smsgate.constants import *
from smsgate.backends.mssgbox_com.constants import *
from django.core.exceptions import ImproperlyConfigured
import re

# Setting default parameters, checking for required variables
COMMAND_URL = 'http://api.mssgbox.com/http/v1/%s.do'
_CREDENTIALS = {
    'api_id': CREDENTIALS.get('api_id', None),
    'login': CREDENTIALS.get('login', None),
    'password': CREDENTIALS.get('password', None),
}
if None in _CREDENTIALS.values():
    raise ImproperlyConfigured('You must set api_id,login,password in '
                               'SMSGATE_CREDENTIALS dictionary to work with '
                               'backend %s' % BACKEND)


def send_command(command, authenticate=True, **params):
    if authenticate and not params.get('session_id', None):
        params.update(_CREDENTIALS)
    page = http_request(COMMAND_URL % command, params)
    return page.code, page.read()


def parse(response, regexp, exception_on_fail=True):
    '''
    Helper function for raising SmsGateUnknownResponse on failed searches.
    '''
    result = re.findall(regexp, response[1])
    if not result:
        raise SmsGateUnknownResponse(response)
    return result


def auth():
    '''
    Returns session_id for mass sms sending.
    '''
    match = parse(send_command('auth'), '(OK|ERR): ([0-9a-f]+)')[0]
    if match[0] == 'ERR':
        code = match[1]
        raise SmsGateError(code, ERROR_CODES.get(code,
                                                 'Unknown code: %s' % code))
    return match[1]


def sendMsg(message, recipient_list, sender, **options):
    options.update({'to': recipient_list, 'text': message, 'from': sender, })

    # Commented out - because not working as documented
    # if len(recipient_list) > 1:
    #     regexp = '(ERR|ID): ([0-9a-f]+) To: (\d+)'
    # else:
    #     regexp = '(ERR|ID): ([0-9a-f]+)'
    regexp = '(ERR|ID): ([0-9a-f]+)'
    match_all = parse(send_command('sendMsg', **options), regexp)

    result = []
    for match in match_all:
        if match[0] == 'ERR':
            result.append((None, STATUS_UNSENT,
                           ERROR_CODES.get(match[1], u'Unknown code: %s' % match[1])))
        else:
            result.append((match[1], STATUS_SENT, None))
    return tuple(result)


def queryMsg(remote_id, **options):
    response = send_command('queryMsg', uid=remote_id, **options)
    match = parse(response, '(Status|ERR): (\d+)')[0]
    if match[0] == 'ERR':
        return STATUS_UNKNOWN, \
               ERROR_CODES.get(match[1], u'Unknown error code: %s' % match[1])
    return STATUS_CODES.get(match[1],
                            (STATUS_UNKNOWN, u'Unknown status: %s' % match[1]))


def get_sms_statuses(remote_ids):
    kwargs = {}
    if len(remote_ids) > 1:
        kwargs['session_id'] = auth()
    for remote_id in remote_ids:
        yield queryMsg(remote_id, **kwargs)


def send_sms(message, recipient_list, remote_id, sender, callback_url):
    return sendMsg(message, recipient_list, sender, msg_callback=bool(callback_url))


def send_mass_sms(datatuple, sender, callback_url):
    session_id = auth()
    for message, recipient_list, remote_id in datatuple:
        yield sendMsg(message, recipient_list, sender,
                      msg_callback=bool(callback_url), session_id=session_id)


def sms_status_callback(request):
    if request.method == 'GET':
        data = request.GET
    elif request.method == 'POST':
        data = request.POST

    remote_id, remote_status = data['uid'], data['status']
    status, status_text = \
    STATUS_CODES.get(remote_status,
                     (STATUS_UNKNOWN, u'Unknown status: %s' % remote_status))

    return ((remote_id, status, status_text),)
