from celery import shared_task
from shipments.utils import APICall
from boloo.global_constants import BASE_URL, SHIPMENT_DETAILS_END_POINT
import redis
import json
from shipments.models import Transporter, Shipment, ShipmentItem, Address, Shop
from django.db import transaction
from boloo.celery import app
from shipments.utils import CommonUtils


def get_or_create_boloo_shop():

    """
    checks if the Shop named Boloo is present.
    If not present, a new shop with name Boloo is created
    :return: Shop object
    """

    boloo_shop = Shop.objects.filter(name="Boloo").first()

    if not boloo_shop:
        boloo_shop = Shop.objects.create(
            name="Boloo",
            client_id=Shop.generate_new_client_id(),
            client_secret=Shop.generate_new_client_secret()
        )

    return boloo_shop


@shared_task
def create_db_records():

    """
    Reads data from cache and creates DB records for the same
    :return:
    """

    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    transporters = []

    shipments = []

    try:
        with transaction.atomic():

            while redis_client.llen('transporters') != 0:
                transporters.append(json.loads(redis_client.lpop('transporters').decode('utf-8')))

            while redis_client.llen('shipments') != 0:
                shipments.append(json.loads(redis_client.lpop('shipments').decode('utf-8')))

            # creating a dic of transporters to remove duplicates
            transporters_dict = {transporter['transport_id']: transporter for transporter in transporters}

            unique_transports = [Transporter(**v) for v in transporters_dict.values()]

            # bulk create Transporters
            Transporter.objects.bulk_create(unique_transports)

            shipments_to_save = []

            shipment_items_to_save = []

            boloo_shop = get_or_create_boloo_shop()

            for shipment_details in shipments:

                shipment_items = shipment_details.pop('shipment_items')

                # check if the customer_details is present a create a db record
                if 'customer_details' in shipment_details:

                    customer_address = shipment_details.pop('customer_details')

                    customer_address_obj = Address.objects.create(**customer_address)

                    # attaching customer_address_obj to shipment_details
                    shipment_details['customer_details_id'] = customer_address_obj.id

                # check if the billing_details is present a create a db record
                if 'billing_details' in shipment_details:

                    billing_address = shipment_details.pop('billing_details')

                    billing_address_obj = Address.objects.create(**billing_address)

                    # attaching billing_address_obj to shipment_details
                    shipment_details['billing_details_id'] = billing_address_obj.id

                shipment_details['shipment_date'] = CommonUtils.get_datetime_from_request(shipment_details.get('shipment_date'))
                shipment_details['shop_id'] = boloo_shop.id

                # append to shipments_to_save for bulk_create
                shipments_to_save.append(Shipment(**shipment_details))

                for shipment_item in shipment_items:
                    shipment_item['shipment_id'] = shipment_details['shipment_id']
                    shipment_item['order_date'] = CommonUtils.get_datetime_from_request(shipment_item.get('order_date'))
                    shipment_item['latest_delivery_date'] = CommonUtils.get_datetime_from_request(shipment_item.get('latest_delivery_date'))

                    # append to shipment_items_to_save for bulk_create
                    shipment_items_to_save.append(ShipmentItem(**shipment_item))

            # TODO: Use chunks
            # bulk creating Shipments
            Shipment.objects.bulk_create(shipments_to_save)

            # bulk creating ShipmentItems
            ShipmentItem.objects.bulk_create(shipment_items_to_save)

    except Exception as e:
        print(e)
        raise e

    return "Success"


@shared_task
def store_shipment_details_in_cache(shipment_ids):

    """
    Makes shipment-details API call for each shipment_id and saves in cache (redis)
    :param shipment_ids:
    :return:
    """

    # fetch access_token
    access_token = APICall.get_access_token()

    # connect to redis client
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    for shipment_id in shipment_ids:

        url = "{}{}{}".format(BASE_URL, SHIPMENT_DETAILS_END_POINT, str(shipment_id))

        access_token, response_data = APICall.get_request(access_token, url)

        shipment_details = response_data

        transporter_details = shipment_details.pop("transport")

        shipment_details["transporter_id"] = transporter_details["transport_id"]

        # storing transporter_details in a list of transporters in redis
        redis_client.lpush('transporters', json.dumps(transporter_details))

        # storing shipment_details in a list of shipments in redis
        redis_client.lpush('shipments', json.dumps(shipment_details))

    # Once the data is stored in redis, we call `create_db_records` task to fetch this data and create DB records.
    # Since all the `store_shipment_details_in_cache` tasks create `create_db_records` task,
    # we need to revoke previously created tasks so that `create_db_records` task is called only once in the end
    # To revoke earlier tasks
    while redis_client.llen('previous_task_ids') != 0:
        app.control.revoke(redis_client.lpop('previous_task_ids').decode('utf-8'))

    # calling `create_db_records` task with countdown just to make sure no more `store_shipment_details_in_cache` task is executed before it.
    create_db_records_task = create_db_records.apply_async(countdown=60*15)

    # saving task id, so that this can be revoked if this is not last task
    redis_client.lpush('previous_task_ids', create_db_records_task.id)

    return "Success"
