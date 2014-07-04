from smsgate import settings
import urllib
import urllib2


def _urlencode(data):
    '''
    Small workaround for urlencode to recieve dict and nested tuples.
    '''
    post_encode = []
    items = data.items() if hasattr(data, 'items') else data
    for key, value in items:
        if hasattr(value, '__iter__'):
            for subvalue in value:
                post_encode.append((key, subvalue))
        else:
            post_encode.append((key, value))
    return urllib.urlencode(post_encode)


def http_request(url, params, method='POST', extra_handlers=[]):
    '''
    Helper function for HTTP requests.
    Returns httplib.HTTPResponse object.
    '''
    if method != 'POST':
        raise NotImplementedError
    handlers = [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), ] + extra_handlers
    opener = urllib2.build_opener(*handlers)
    if settings.HTTP_PROXY:
        opener.add_handler(urllib2.ProxyHandler(settings.HTTP_PROXY))
    request = urllib2.Request(url, _urlencode(params))

    kwargs = {}
    if settings.HTTP_TIMEOUT:
        kwargs['timeout'] = settings.HTTP_TIMEOUT
    page = opener.open(request, **kwargs)
    return page
