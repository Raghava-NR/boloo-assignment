from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from shipments.utils import CommonUtils
from shipments.models import Shop
from rest_framework.permissions import AllowAny
from multiprocessing import cpu_count
import math
from shipments.sync_data.tasks import fetch_shipments


class ShipmentsSyncViewSet(viewsets.ViewSet):

    permission_classes = (AllowAny, )
    authentication_classes = ()

    @staticmethod
    def get_redis_key_for_shop(shop_id):

        return 'shop_{}_shipments'.format(shop_id)

    @action(detail=False, methods=["get"], url_path="initial-sync")
    def initial_sync(self, request):

        """
        For Initial Sync of data.

        :param request:
        :return:
        """

        all_active_shops_ids = list(Shop.objects.filter(is_active=True).values_list('id', flat=True))

        all_active_shops_ids_count = len(all_active_shops_ids)

        no_of_cores = cpu_count()

        min_no_of_shops_per_process = 5

        if min_no_of_shops_per_process > math.ceil(all_active_shops_ids_count / no_of_cores):
            no_of_cores = math.ceil(all_active_shops_ids_count / min_no_of_shops_per_process)

        shop_ids_chunks = list(CommonUtils.chunks(all_active_shops_ids, math.ceil(all_active_shops_ids_count / no_of_cores)))

        for shop_ids_chunk in shop_ids_chunks:
            fetch_shipments.delay(shop_ids_chunk)

        return Response({"message": "Async Tasks have been started."})


