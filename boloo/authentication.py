from rest_framework import authentication, exceptions
from django.conf import settings
import jwt
from shipments.models import Shop


class JWTAuthMiddlewareHTTP(authentication.BaseAuthentication):

    authentication_header_prefix = "Bearer"

    def authenticate(self, request):

        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, "Bearer") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            # No authentication header was provided so bypass the authentication mechanism
            return None

        if len(auth_header) != 2:
            # Authentication header wasn't supplied in the correct format
            msg = "Authentication header not provided in the correct format."
            raise exceptions.AuthenticationFailed(msg)

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`.
        prefix = auth_header[0].decode("utf-8")
        token = auth_header[1].decode("utf-8")

        if prefix.lower() != auth_header_prefix:
            # Authentication header prefix was not as specified
            msg = "Incorrect authentication header prefix supplied"
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):

        """
        Try to authenticate the given credentials. If authentication is
        successful, return the shop and token. If not, throw an error.
        """
        try:
            shop_decoded_jwt_data = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            msg = "The authentication token is expired."
            raise exceptions.AuthenticationFailed(msg)

        except:
            msg = "The authentication token could not be decoded."
            raise exceptions.AuthenticationFailed(msg)

        try:
            shop = Shop.objects.get(client_id=shop_decoded_jwt_data["client_id"],
                                    client_secret=shop_decoded_jwt_data["client_secret"])

        except Shop.DoesNotExist:
            msg = "No shop matching this token was found."
            raise exceptions.AuthenticationFailed(msg)

        if not Shop.is_active:
            msg = "The shop matching this token has been deactivated."
            raise exceptions.AuthenticationFailed(msg)

        # can return 2 objects, first will be set to request.user and 2nd to request.auth
        return shop, token
