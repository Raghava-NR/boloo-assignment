# Generated by Django 2.2 on 2020-07-15 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0002_auto_20200715_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='chamber_of_commerce_number',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='address',
            name='delivery_phone_number',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='address',
            name='first_name',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='address',
            name='order_reference',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='address',
            name='surname',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='address',
            name='vat_number',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='shipment_reference',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='shipmentitem',
            name='ean',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='shipmentitem',
            name='offer_condition',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='shipmentitem',
            name='offer_reference',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='shipmentitem',
            name='order_id',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='shipmentitem',
            name='order_item_id',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name='transporter',
            name='shipping_label_code',
            field=models.CharField(default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='transporter',
            name='transporter_code',
            field=models.CharField(max_length=32),
        ),
    ]
