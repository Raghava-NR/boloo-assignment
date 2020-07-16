# core imports
from celery import shared_task
from django.db import transaction
from itertools import cycle
from collections import defaultdict

# project imports
from shipments.utils import APICall
from boloo.global_constants import BASE_URL, SHIPMENT_DETAILS_END_POINT, SHIPMENTS_LIST_END_POINT
from shipments.models import Transporter, Shipment, ShipmentItem, Address, Shop
from shipments.utils import CommonUtils


@shared_task
def store_data_in_db(shop_id, shipment_details_list):

    # Since many shipments can be linked to same transport/customer_details/billing_details
    transporters_map = {}

    customer_details_map = {}

    billing_details_map = {}

    # saving shipments for further processing
    shipments_map = {}

    # dict representing shipment_id: email for updating shipment_details with Address pks
    shipments_to_customer_details_map = {}
    shipments_to_billing_details_map = {}

    shipment_items_to_save = []

    for shipment_details in shipment_details_list:

        transporter_details = shipment_details.pop("transport")

        transporters_map[transporter_details["transport_id"]] = transporter_details

        shipment_details["transporter_id"] = transporter_details["transport_id"]

        # check if the customer_details is present a create a db record
        if 'customer_details' in shipment_details:
            customer_address = shipment_details.pop('customer_details')

            customer_address['type'] = 'Customer'

            # email (unique identifier) is not present in few records
            if customer_address.get('email'):
                customer_details_map[customer_address['email']] = customer_address
                shipments_to_customer_details_map[shipment_details['shipment_id']] = customer_address['email']

        # check if the billing_details is present a create a db record
        if 'billing_details' in shipment_details:
            billing_address = shipment_details.pop('billing_details')

            billing_address['type'] = 'Billing'

            # email (unique identifier) is not present in few records
            if billing_details_map.get('email'):
                billing_details_map[billing_address['email']] = billing_address
                shipments_to_billing_details_map[shipment_details['shipment_id']] = billing_address['email']

        shipment_details['shipment_date'] = CommonUtils.get_datetime_from_request(shipment_details.get('shipment_date'))
        shipment_details['shop_id'] = shop_id

        shipment_items = shipment_details.pop('shipment_items')

        for shipment_item in shipment_items:
            shipment_item['shipment_id'] = shipment_details['shipment_id']
            shipment_item['order_date'] = CommonUtils.get_datetime_from_request(shipment_item.get('order_date'))
            shipment_item['latest_delivery_date'] = CommonUtils.get_datetime_from_request(shipment_item.get('latest_delivery_date'))

            # append to shipment_items_to_save for bulk_create
            shipment_items_to_save.append(ShipmentItem(**shipment_item))

        shipments_map[shipment_details['shipment_id']] = shipment_details

    try:

        with transaction.atomic():

            # fetch unique transporters wrt transporter_id
            unique_transports = [Transporter(**v) for v in transporters_map.values()]

            # bulk create Transporters
            Transporter.objects.bulk_create(unique_transports)

            # fetch unique customer_details wrt email
            unique_customer_details = [Address(**v) for v in customer_details_map.values()]

            # bulk create Address (Customer Details)
            Address.objects.bulk_create(unique_customer_details)

            # fetch unique billing_details wrt email
            unique_billing_details = [Address(**v) for v in billing_details_map.values()]

            # bulk create Address (Billing Details)
            Address.objects.bulk_create(unique_billing_details)

            # creating a dict of email: id of Address
            customer_details_created_objects_map = {v['email']: v['id'] for v in Address.objects.filter(type='Customer').values('email', 'id')}
            billing_details_created_objects_map = {v['email']: v['id'] for v in Address.objects.filter(type='Billing').values('email', 'id')}

            # update customer_details_id of shipments wrt customer_details_created_objects_map
            for k, v in shipments_to_customer_details_map.items():
                shipments_map[k] = {**shipments_map[k], **{'customer_details_id': customer_details_created_objects_map.get(v)}}

            # update billing_details_id of shipments wrt shipments_to_billing_details_map
            for k, v in shipments_to_billing_details_map.items():
                shipments_map[k] = {**shipments_map[k], **{'billing_details_id': billing_details_created_objects_map.get(v)}}

            shipments_to_save = [Shipment(**v) for v in shipments_map.values()]

            # bulk create Shipments
            Shipment.objects.bulk_create(shipments_to_save)

            # bulk create ShipmentItems
            ShipmentItem.objects.bulk_create(shipment_items_to_save)

    except Exception as e:
        print(e)
        raise e

    return "Success"


@shared_task
def fetch_shipment_details(shop_to_shipments_ids_map):

    # dict representing shop_id <pk>: Shop obj
    shops_objs_dict = Shop.objects.filter(is_active=True).in_bulk()

    shops_ids = set(shops_objs_dict.keys())

    shops_cycle = cycle(shops_ids)

    # will be helpful if token is not expired
    shop_id_to_access_token_details_map = {

    }

    shop_id = next(shops_cycle)

    # dict representing shop_id: shipment_details <list>
    shop_to_shipment_details_map = defaultdict(list)

    while shops_ids:

        shop_obj = shops_objs_dict[shop_id]

        shipment_id = shop_to_shipments_ids_map[str(shop_id)].pop()

        url = "{}{}{}".format(BASE_URL, SHIPMENT_DETAILS_END_POINT, str(shipment_id))

        # check if token is already present, if not call an api to fetch token again
        if shop_id_to_access_token_details_map.get(shop_id):
            access_token = shop_id_to_access_token_details_map.get(shop_id)

        else:
            access_token = APICall.get_access_token(shop_obj.client_id, shop_obj.client_secret)

            shop_id_to_access_token_details_map[shop_id] = access_token

        # making api call, send wait_for_retry flag as true if only one shop is present
        access_token, response_data, wait_time = APICall.get_request(access_token,
                                                                     url,
                                                                     shop_obj.client_id,
                                                                     shop_obj.client_secret,
                                                                     len(shops_ids) == 1)

        # Handling retry-logic
        if response_data is None and wait_time:
            # change current_shop with next in cycle
            shop_id = next(shops_cycle)
            shop_to_shipments_ids_map[str(shop_id)].append(shipment_id)

            continue

        shop_to_shipment_details_map[shop_id].append(response_data)

        # remove shop from shops_ids if all the shipment_details are obtained
        if not shop_to_shipments_ids_map[str(shop_id)]:
            shops_ids = shops_ids - {shop_id}
            if not shops_ids:
                # breaking here as next(shops_cycle) will raise StopIteration error
                break

            # update shops_cycle, shop_id
            shops_cycle = cycle(shops_ids)
            shop_id = next(shops_cycle)

    # calling store_data_in_db task for each store
    for k, v in shop_to_shipment_details_map.items():
        store_data_in_db.delay(k, v)

    return "Success"


@shared_task
def fetch_shipments(shop_ids):

    # dict representing shop_id <pk>: Shop obj
    shops_objs_dict = Shop.objects.filter(is_active=True, id__in=shop_ids).in_bulk()

    shops_ids = set(shops_objs_dict.keys())

    shops_cycle = cycle(shops_ids)

    # will be helpful if token is not expired
    shop_id_to_access_token_details_map = {

    }

    # maintaining current page of each_store
    shop_id_to_current_page_no_map = {
        i: 1 for i in shops_ids
    }

    # dict representing shop_id: shipments_ids <list>
    shop_to_shipments_ids_map = defaultdict(list)

    fulfilment_methods = ("FBR", )

    # current shop_id
    shop_id = next(shops_cycle)

    # current page of current_shop
    page = shop_id_to_current_page_no_map[shop_id]

    for fulfilment_method in fulfilment_methods:

        while shops_ids:

            shop_obj = shops_objs_dict[shop_id]

            url = "{}{}?page={}&fulfilment-method={}".format(BASE_URL, SHIPMENTS_LIST_END_POINT, str(page), fulfilment_method)

            # check if token is already present, if not call an api to fetch token again
            if shop_id_to_access_token_details_map.get(shop_id):
                access_token = shop_id_to_access_token_details_map.get(shop_id)

            else:
                access_token = APICall.get_access_token(shop_obj.client_id, shop_obj.client_secret)

                shop_id_to_access_token_details_map[shop_id] = access_token

            # making api call, send wait_for_retry flag as true if only one shop is present
            access_token, response_data, wait_time = APICall.get_request(access_token, url,
                                                                         shop_obj.client_id,
                                                                         shop_obj.client_secret,
                                                                         len(shops_ids) == 1)

            # Handling retry-logic
            if response_data is None and wait_time:
                # change current_shop with next in cycle
                shop_id = next(shops_cycle)
                # set page value to current shop's page
                page = shop_id_to_current_page_no_map[shop_id]

                continue

            # If no response is returned i.e all the shipments are obtained
            if not response_data:
                # remove current_shop from shops_ids
                shops_ids = shops_ids - {shop_id}
                if not shops_ids:
                    # breaking here as next(shops_cycle) will raise StopIteration error
                    break

                # update shops_cycle, shop_id, page
                shops_cycle = cycle(shops_ids)
                shop_id = next(shops_cycle)
                page = shop_id_to_current_page_no_map.get(shop_id, 1)

                continue

            shipment_ids = [shipment['shipment_id'] for shipment in response_data['shipments']]

            shop_to_shipments_ids_map[shop_id].extend(shipment_ids[:5])

            # increment page of current_shop
            shop_id_to_current_page_no_map[shop_id] += 1

            # update page value to current_shop's page
            page = shop_id_to_current_page_no_map[shop_id]

    fetch_shipment_details.delay(shop_to_shipments_ids_map)

    return "Success "
