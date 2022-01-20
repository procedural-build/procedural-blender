"""
Utilities for API Access.  Specifically a User class which gets or refreshes the
access token and
"""

from urllib import request as Req
from urllib.error import HTTPError
from urllib.parse import urlencode
import requests
from datetime import datetime
import base64
import json
import logging
import ssl

logger = logging.getLogger(__name__)

# Disable SSL verification - TO FIX THIS
ssl_context = ssl._create_unverified_context()

# Common function for pretty-print JSON data
def printJSON(pyObj):
    json_str = json.dumps(pyObj, indent=4)
    logger.info(json_str)
    return json_str

def data_to_dict(data):
    try:
        return json.loads(data)
    except:
        pass

    try:
        return data.decode() if type(data) == bytes else data
    except:
        pass

    return data

# Store each user in a class with their access token and a method
# "request" to GET, POST, PUT, DELETE to the API urls
class User():

    content_header = {"content-type": "application/json"}

    def __init__(self, username, password, host="https://compute.procedural.build"):
        self.host_url = host[:-1] if host[-1] == "/" else host
        self.username   = username
        self.password   = password
        self._access_token   = ""
        self._refresh_token  = ""
        self.request_log = []

    @property
    def token(self):
        return self._access_token

    @property
    def jwt_payload(self):
        """ Get the payload from the JWT
        """
        if not self._access_token:
            return None
        payload_bytes = self._access_token.split('.')[1].encode('utf8')
        missing_padding = len(payload_bytes) % 4
        if missing_padding:
            payload_bytes += b'=' * (4 - missing_padding)
        payload = json.loads(base64.b64decode(payload_bytes))
        return payload

    @property
    def token_exp_time(self):
        """ Seconds remaining until token expiry
        """
        payload = self.jwt_payload
        if payload is None:
            return None
        exp_timestamp = payload.get('exp', None)
        if not exp_timestamp:
            raise Exception('Could not get expiry timestamp from JWT token')
        now = datetime.utcnow()
        expiry = datetime.utcfromtimestamp(exp_timestamp)
        return (expiry - now).total_seconds()

    def headers(self, extra_headers={}):
        header = self.content_header.copy()
        if self.token:
            header.update({'Authorization': 'JWT %s'%(self.token)})
        if extra_headers:
            header.update(extra_headers)
        return header

    def clear_tokens(self):
        self._access_token = ""
        self._refresh_token = ""

    def get_token(self):
        self.clear_tokens()
        response_dict = self.request('POST', '/auth-jwt/get/', {'username': self.username, 'password': self.password})
        self._access_token = response_dict.get('access', None)
        self._refresh_token = response_dict.get('refresh', None)
        for token_type in ['access', 'refresh']:
            if response_dict.get(token_type, None) is None:
                raise Exception("Error getting token: %s", self.printJSON(response_dict))
        logger.info(f"Got new token. Will expire in: {self.token_exp_time}")
        return self.token

    def refresh_token(self, time_remaining = 20):
        # Check that we have a refresh token first
        if not self._refresh_token:
            return None
        # Check if the current access token is valid
        exp_time = self.token_exp_time
        if exp_time and exp_time > time_remaining:
            #logger.info(f"No refresh required. Token will expire in {exp_time}")
            return self.token
        # Do the refresh
        response_dict = self.request('POST', '/auth-jwt/refresh/', {'refresh': self._refresh_token})
        self._access_token = response_dict['access']
        logger.info("Refreshed token. Will expire in", self.token_exp_time)
        return self.token

    def verify_token(self):
        response_dict = self.request('POST', '/auth-jwt/verify/', {'token': self.token})
        self._access_token = response_dict['access']
        return self.token

    def get_full_url(self, url, query_params):
        # Append query parameters to the url
        url = self.host_url + url
        url_params = urlencode(query_params) if query_params else None
        return '%s?%s'%(url, url_params) if url_params else url

    def decode_response(self):
        """ Try to parse the response as JSON, otherwise just return the raw response
        """
        decoded_response = self.last_response
        content = ""
        try:
            content = self.last_response.read().decode('utf8')
            decoded_response = json.loads(content)
            return decoded_response
        except (TypeError, json.JSONDecodeError):
            # Attach the read content onto the response object (for future use)
            decoded_response.read_content = content
            return decoded_response
        # Should not get here
        return decoded_response

    def show_log(self, n=1, ids=[], methods=["POST", "PUT", "PATCH"]):
        methods = set(methods)
        ids = set(ids)

        def _include(i):
            return (i.get("method") in methods) and (i.get('id') in ids if ids else True)
       
        _requests = [i for i in self.request_log if _include(i)]
        _requests = _requests[-1*n:] if len(_requests) >= n else _requests

        printJSON(_requests)

        return _requests

    def request(self, method, url, data=None, query_params=None, extra_headers={}, raw=False):
        # Check if the access token needs refreshing unless we are calling an auth-jwt endpoint
        if not url.startswith('/auth-jwt/'):
            self.refresh_token()

        # Get the full url
        url = self.get_full_url(url, query_params)

        # Set the data that should be sent
        if method in ['POST', 'PUT', 'PATCH'] and not raw:
            # Send POST requst with JSON encoded data
            data = json.dumps(data).encode('utf8')

        _extra_headers = extra_headers.copy()
        if raw and (not "content-type" in extra_headers):
            logger.info("Setting raw body content-type to application/octet-stream")
            _extra_headers.update({"content-type": "application/octet-stream"})

        # Remove data from GET requests (otherwise urllib will conver this to a POST automatically)
        if method == "GET":
            data = None

        # Get the headers to use
        headers = self.headers(_extra_headers)

        # Log the request data (for debugging later)
        _id = len(self.request_log) + 1
        logger.info(f"Sending Request #{_id}: [{method}] {url}")  # {headers} {data}
        self.request_log.append({
            "method": method,
            "headers": headers,
            "id": _id,
            "url": url,
            "time": datetime.now().isoformat(),
            "data": data_to_dict(data)
        })

        # Get the actual request object
        request = Req.Request(url, method=method, data=data, headers=headers)

        try:
            self.last_response = Req.urlopen(request, context=ssl_context)
        except HTTPError as err:
            msg = err.read().decode('utf8')
            logger.info(msg)
            self.last_response = None
            raise Exception("Request failed due to: %s"%(msg))

        return self.decode_response()


USER = [User('', '')]


def get_current_user():
    return USER[0]


def login_user(username, password, host):
    USER[0] = User(username, password, host = host)
    logger.info(f"Getting token for user {username} from {host}")
    USER[0].get_token()
    return USER[0]
