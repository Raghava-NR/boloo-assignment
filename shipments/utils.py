import requests
import time
from datetime import datetime
from djangorestframework_camel_case.util import underscoreize
import string
import random

from boloo.global_constants import BOLOO_CLIENT_ID, BOLOO_CLIENT_SECRET_KEY, ACCESS_TOKEN_URL


class APICall:

    """
    Utils class used for making API calls
    """

    @staticmethod
    def get_headers(access_token):

        """
        construct headers required
        :param access_token:
        :return: headers <dict>
        """

        headers = {
            "Authorization": "Bearer " + access_token,
            "Accept": "application/vnd.retailer.v3+json"
        }

        return headers

    @staticmethod
    def get_access_token():

        """
        Fetches access_token from client_id and client_secret
        :return: access_token <str>
        """

        r = requests.post(ACCESS_TOKEN_URL, data={"client_id": BOLOO_CLIENT_ID,
                                                  "client_secret": BOLOO_CLIENT_SECRET_KEY,
                                                  "grant_type": "client_credentials"})

        response_data = r.json()

        return response_data["access_token"]

    @staticmethod
    def get_request(access_token, url):

        """
        To make an API call
        Handles if the token is expired and if rate-limit is reached.
        :param access_token:
        :param url:
        :return:
        """

        r = requests.get(url, headers=APICall.get_headers(access_token))

        if r.status_code == 200:

            # Camel to snake case converter
            response_data = underscoreize(r.json())

            return access_token, response_data

        elif r.status_code == 401:
            # Token is expired
            # Get a new access_token and try again
            new_access_token = APICall.get_access_token()

            return APICall.get_request(new_access_token, url)

        elif r.status_code == 429:
            # rate-limit reached
            retry_after = r.headers['retry-after']

            # wait for `retry_after` seconds and try again
            time.sleep(int(retry_after))

            return APICall.get_request(access_token, url)

        else:
            # unknown status_code, raise exception
            print(r.status_code)
            raise Exception


class CommonUtils:

    @staticmethod
    def get_datetime_from_request(request_date):

        # TODO: check for better alternative
        """
        string to datetime converter
        :param request_date:
        :return:
        """

        return datetime.strptime(request_date[:19] + request_date[19:22] + request_date[23:26], '%Y-%m-%dT%H:%M:%S%z') if request_date else None

    @staticmethod
    def random_alpha_numeric_lower(length):

        """
        Generates random string considering lowercase alphabets and digits of given length
        :param length:
        :return: random string of given length
        """

        random_choices = string.ascii_lowercase + string.digits

        return ''.join((random.choice(random_choices) for _ in range(length)))

    @staticmethod
    def random_alpha_numeric_symbol(length):

        """
        Generates random string considering lowercase & uppercase alphabets, digits and (_,-) symbols of given length
        :param length:
        :return: random string of given length
        """

        random_choices = string.ascii_letters + string.digits + '_-'

        return ''.join((random.choice(random_choices) for _ in range(length)))
