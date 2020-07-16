import requests
import time
from datetime import datetime
from djangorestframework_camel_case.util import underscoreize
import string
import random

from boloo.global_constants import ACCESS_TOKEN_URL


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
    def get_access_token(client_id, client_secret):

        """
        Fetches access_token from client_id and client_secret

        :param client_id:
        :param client_secret:
        :return: access_token <str>
        """

        r = requests.post(ACCESS_TOKEN_URL, data={"client_id": client_id,
                                                  "client_secret": client_secret,
                                                  "grant_type": "client_credentials"})

        response_data = r.json()

        return response_data["access_token"]

    @staticmethod
    def get_request(access_token, url, client_id, client_secret, wait_for_retry=False):

        """
        To make an API call
        Handles if the token is expired.
        :param access_token:
        :param url:
        :param client_id:
        :param client_secret:
        :param wait_for_retry:
        :return:
        """

        r = requests.get(url, headers=APICall.get_headers(access_token))

        if r.status_code == 200:

            # Camel to snake case converter
            response_data = underscoreize(r.json())

            return access_token, response_data, 0

        elif r.status_code == 401:
            # Token is expired
            # Get a new access_token and try again
            new_access_token = APICall.get_access_token(client_id, client_secret)

            return APICall.get_request(new_access_token, url, client_id, client_secret)

        elif r.status_code == 429:

            if wait_for_retry:

                # sleep if wait_for_retry is explicitly specified
                time.sleep(int(r.headers['retry-after']))

                return APICall.get_request(access_token, url, client_id, client_secret)

            return access_token, None, int(r.headers['retry-after'])

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

    @staticmethod
    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]
