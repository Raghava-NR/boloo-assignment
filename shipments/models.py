from django.db import models
from datetime import datetime, timedelta
import jwt

from shipments.utils import CommonUtils
from django.conf import settings


class Shop(models.Model):

    """
    Model class representing Shop
    """

    name = models.CharField(max_length=64, unique=True)
    client_id = models.CharField(max_length=128)
    client_secret = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('client_id', 'client_secret')

    @staticmethod
    def generate_new_client_id():
        """
        Generates a new client id with a fixed format.
        :return:
        """
        return '-'.join(CommonUtils.random_alpha_numeric_lower(i) for i in [8, 4, 4, 12])

    @staticmethod
    def generate_new_client_secret():
        """
        Generates a new client secret with a fixed format.
        :return:
        """
        return CommonUtils.random_alpha_numeric_symbol(86)

    def generate_jwt_token(self):

        """
        Generates a JSON Web Token that stores this shop's client_id, client_secret and has an expiry
        date set to 300 seconds into the future.
        """

        dt = datetime.now() + timedelta(seconds=300)

        token = jwt.encode(
            {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "exp": int(dt.strftime("%s"))
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return token.decode("utf-8")

    @property
    def is_authenticated(self):

        """
        for validating is_authenticated permission
        :return: True
        """
        return True


class Address(models.Model):

    """
    Model class representing address information (both customer and billing)
    """

    pick_up_point_name = models.CharField(max_length=64, default='')
    salutation_code = models.CharField(max_length=8, default='')
    first_name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32, default='')
    street_name = models.CharField(max_length=32, default='')
    house_number = models.CharField(max_length=8, default='')
    house_number_extended = models.CharField(max_length=8, default='')
    address_supplement = models.CharField(max_length=32, default='')
    extra_address_information = models.CharField(max_length=64, default='')
    zip_code = models.CharField(max_length=16, default='')
    city = models.CharField(max_length=32, default='')
    country_code = models.CharField(max_length=8, default='')
    email = models.CharField(max_length=128)
    company = models.CharField(max_length=64, default='')
    vat_number = models.CharField(max_length=32, default='')
    chamber_of_commerce_number = models.CharField(max_length=32, default='')
    order_reference = models.CharField(max_length=32, default='')
    delivery_phone_number = models.CharField(max_length=32, default='')


class Transporter(models.Model):

    """
    Model class representing transporter
    """

    transport_id = models.IntegerField(primary_key=True)
    transporter_code = models.CharField(max_length=32)
    track_and_trace = models.CharField(max_length=32)
    shipping_label_id = models.IntegerField(null=True)
    shipping_label_code = models.CharField(max_length=32, default="")


class Shipment(models.Model):

    """
    Model class representing shipments
    """

    shop = models.ForeignKey(Shop, default=None, null=True, on_delete=models.PROTECT)

    shipment_id = models.IntegerField(primary_key=True)
    pick_up_point = models.BooleanField(default=False)
    shipment_date = models.DateTimeField(null=True)
    shipment_reference = models.CharField(max_length=32)

    customer_details = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='customer_shipments', null=True)
    billing_details = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='billing_address_shipments', null=True)

    transporter = models.ForeignKey(Transporter, on_delete=models.PROTECT, related_name='shipments')

    def __str__(self):
        return str(self.shipment_id)


class ShipmentItem(models.Model):

    """
    Model class representing shipment items
    """

    # choices for fulfilment_method
    FULFILMENT_CHOICES = ((1, "FBR"), (2, "FBB"))

    shipment = models.ForeignKey(Shipment, on_delete=models.PROTECT, related_name='shipment_items')
    order_item_id = models.CharField(max_length=32)
    order_id = models.CharField(max_length=32)
    order_date = models.DateTimeField(null=True)
    latest_delivery_date = models.DateTimeField(null=True)
    ean = models.CharField(max_length=32, default='')
    title = models.CharField(max_length=512)
    quantity = models.IntegerField(default=0)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    offer_condition = models.CharField(max_length=32, default='')
    offer_reference = models.CharField(max_length=32, default='')
    fulfilment_method = models.CharField(max_length=4, choices=FULFILMENT_CHOICES, default=FULFILMENT_CHOICES[0][1])

    def __str__(self):
        return str(self.shipment_id)
