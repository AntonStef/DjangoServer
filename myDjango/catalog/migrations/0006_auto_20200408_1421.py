# Generated by Django 3.0.3 on 2020-04-08 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_auto_20200331_1511'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['last_name'], 'permissions': (('can_update_create_delete_author', 'Access for update Author'),)},
        ),
    ]