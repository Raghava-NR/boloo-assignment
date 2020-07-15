from shipments.models import ShipmentItem, Shipment, Address, Transporter, Shop
from rest_framework.serializers import ModelSerializer, ALL_FIELDS


class ModelReadSerializerBase(ModelSerializer):

    """

    This is Base class for All the Read Serializers

    This class's additional feature includes setting different set of fields for retrieve and list (depending on request method action)

    If the view object is not passed in context of serializer (which is automatically done by default through ViewSets),
     return super class get_fields (default behaviour)
    """

    def __init__(self, *args, **kwargs):
        """over write Meta attributes depending upon view action"""
        super().__init__(*args, **kwargs)

        self.action = self.get_view_action()

        depth = getattr(self.Meta, 'depth', 0)

        if self.action:

            """
            set meta depth depending if required Meta attribute is present, else fallback to default
            """

            depth = getattr(self.Meta, '{action}_depth'.format(action=self.action), depth)
        setattr(self.Meta, 'depth', depth)

    def get_view_action(self):

        """
        This checks if either view object is passed through context or action (a string implementing any action)
        :return: action (a string)
        """
        source_context = getattr(self, 'context', {})
        view = source_context.get('view', None)
        action = getattr(view, 'action', None)

        return action or source_context.get('action', None)

    def get_field_names(self, declared_fields, info):

        """
        overrides base class's get_field_names
        This method checks for additional field params like list_fields ({action}_fields)

        :param declared_fields:
        :param info:
        :return: fields
        """

        fields = getattr(self.Meta, 'fields', None)
        exclude = getattr(self.Meta, 'exclude', None)

        self.action = self.get_view_action()

        if self.action:
            "check if self.Meta has required attributes set, if not fall back to default"
            fields = getattr(self.Meta, '{action}_fields'.format(action=self.action), fields)
            exclude = getattr(self.Meta, '{action}_exclude'.format(action=self.action), exclude)

        "The code below is copied from super().get_field_names, expect for on check which is mentioned below"
        if fields and fields != ALL_FIELDS and not isinstance(fields, (list, tuple)):
            raise TypeError(
                'The `fields` option must be a list or tuple or "__all__". '
                'Got %s.' % type(fields).__name__
            )

        if exclude and not isinstance(exclude, (list, tuple)):
            raise TypeError(
                'The `exclude` option must be a list or tuple. Got %s.' %
                type(exclude).__name__
            )

        assert not (fields and exclude), (
            "Cannot set both 'fields' and 'exclude' options on "
            "serializer {serializer_class}.".format(
                serializer_class=self.__class__.__name__
            )
        )

        assert not (fields is None and exclude is None), (
            "Creating a ModelSerializer without either the 'fields' attribute "
            "or the 'exclude' attribute has been deprecated since 3.3.0, "
            "and is now disallowed. Add an explicit fields = '__all__' to the "
            "{serializer_class} serializer.".format(
                serializer_class=self.__class__.__name__
            ),
        )

        if fields == ALL_FIELDS:
            fields = None

        if fields is not None:
            """
            super class checks if all declared fields have also been included in the Meta.{action}_fields,
            here we skip that part
            """

            return fields

        # Use the default set of field names if `Meta.fields` is not specified.
        fields = self.get_default_field_names(declared_fields, info)

        if exclude is not None:
            # If `Meta.exclude` is included, then remove those fields.
            for field_name in exclude:
                assert field_name not in self._declared_fields, (
                    "Cannot both declare the field '{field_name}' and include "
                    "it in the {serializer_class} 'exclude' option. Remove the "
                    "field or, if inherited from a parent serializer, disable "
                    "with `{field_name} = None`.".format(
                        field_name=field_name,
                        serializer_class=self.__class__.__name__
                    )
                )

                assert field_name in fields, (
                    "The field '{field_name}' was included on serializer "
                    "{serializer_class} in the 'exclude' option, but does "
                    "not match any model field.".format(
                        field_name=field_name,
                        serializer_class=self.__class__.__name__
                    )
                )
                fields.remove(field_name)

        return fields


class ShopSerializer(ModelSerializer):

    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = [
            'client_id',
            'client_secret'
        ]


class TransporterSerializer(ModelReadSerializerBase):

    class Meta:
        model = Transporter
        fields = '__all__'
        list_fields = [
            'transport_id'
        ]
        retrieve_fields = '__all__'


class AddressSerializer(ModelReadSerializerBase):

    class Meta:
        model = Address
        fields = '__all__'


class ShipmentItemSerializer(ModelReadSerializerBase):

    class Meta:
        model = ShipmentItem
        fields = '__all__'
        list_fields = [
            'order_item_id',
            'order_id'
        ]
        retrieve_fields = '__all__'


class ShipmentSerializer(ModelReadSerializerBase):

    transport = TransporterSerializer(source='transporter')
    shipment_items = ShipmentItemSerializer(many=True)
    customer_details = AddressSerializer(allow_null=True)
    billing_details = AddressSerializer(allow_null=True)

    class Meta:
        model = Shipment
        fields = '__all__'
        list_fields = [
            'shipment_id',
            'shipment_date',
            'shipment_reference',
            'transport',
            'shipment_items',
        ]
        retrieve_fields = [
            'shipment_id',
            'shipment_date',
            'shipment_reference',
            'transport',
            'shipment_items',
            'customer_details',
            'billing_details'
        ]


