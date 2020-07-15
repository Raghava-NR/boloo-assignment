from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from boloo.global_constants import BASE_URL, SHIPMENTS_LIST_END_POINT
from shipments.sync_data.tasks import store_shipment_details_in_cache

from shipments.utils import APICall


class ShipmentsSyncViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["get"], url_path="initial-sync")
    def initial_sync(self, request):

        """
        For Initial Sync of data.

        :param request:
        :return:
        """

        # fetching access_token
        access_token = APICall.get_access_token()

        # options for fulfilment_methods
        fulfilment_methods = ("FBR", "FBB")

        for fulfilment_method in fulfilment_methods:

            page = 1

            while True:

                url = "{}{}?page={}&fulfilment-method={}".format(BASE_URL, SHIPMENTS_LIST_END_POINT, str(page), fulfilment_method)

                access_token, response_data = APICall.get_request(access_token, url)

                # no data for this page, then break
                if not response_data:
                    break

                shipment_ids = [shipment['shipment_id'] for shipment in response_data['shipments']]

                store_shipment_details_in_cache.delay(shipment_ids)

                page += 1

        return Response({"message": "Async Tasks have been started."})


