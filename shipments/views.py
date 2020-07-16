# core imports
from rest_framework import viewsets
from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# project imports
from shipments.models import Shipment, ShipmentItem, Shop
from shipments.serializers import ShipmentSerializer, ShopSerializer


class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):

    """
    API endpoint that allows Shipments to be viewed wrt request.user i.e shop requested.
    """

    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer

    @staticmethod
    def prefetch_shipment_items(query):

        # Pre-fetching shipment_items to avoid multiple DB calls
        shipment_items_q = ShipmentItem.objects.all()

        prefetch_obj = Prefetch('shipment_items', queryset=shipment_items_q)

        query = query.prefetch_related(
            prefetch_obj
        )

        return query

    def get_queryset(self):

        """
        Overriding the default get_queryset to reduce unnecessary data fetches.

        :return: queryset
        """

        queryset = Shipment.objects.filter(shop_id=self.request.user.id).select_related('transporter')

        if self.action == 'list':

            """
            If the action is list
            """

            query = self.prefetch_shipment_items(queryset)

            return query.order_by('-shipment_date')

        elif self.action == 'retrieve':

            """
            If the action is retrieve
            """

            query = self.prefetch_shipment_items(queryset)

            query = query.select_related('customer_details', 'billing_details')

            return query

        return


class ShopViewSet(viewsets.ModelViewSet):

    """
    CRUD API for Shop
    """

    authentication_classes = ()
    permission_classes = (AllowAny,)

    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer

    def perform_destroy(self, instance):

        """
        Set `is_active` False instead of hard delete
        :param instance:
        :return:
        """

        instance.is_active = False
        instance.save(update_fields=['is_active'])


class LoginViewSet(viewsets.ViewSet):

    """
    API for fetching token
    """

    authentication_classes = ()
    permission_classes = (AllowAny, )

    @action(detail=False, methods=["post"], url_path="token")
    def token(self, request):

        """
        To get access_token.
        :param request:
        :return: Response
        """

        request_data = request.data

        client_id = request_data['client_id']
        client_secret = request_data['client_secret']

        shop = Shop.objects.get(client_id=client_id, client_secret=client_secret)

        return Response({'access_token': shop.generate_jwt_token(), "token_type": "Bearer"})









