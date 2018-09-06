from logging import getLogger
from time import sleep
from urllib import request, parse

logger = getLogger()


def http_get(url, params=None, max_retry=5):
    req_url = '{}?{}'.format(url, parse.urlencode(params))
    logger.debug(f"GET {req_url}")
    body = None
    last_error = None
    for i in range(max_retry):
        try:
            req = request.Request(req_url)
            with request.urlopen(req) as res:
                body = res.read()
        except Exception as e:
            sleep(i * 2)
            last_error = e

    if body is None:
        raise last_error
    return body
