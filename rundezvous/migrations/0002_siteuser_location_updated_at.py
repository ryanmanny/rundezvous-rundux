# Generated by Django 2.2 on 2019-04-18 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rundezvous', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteuser',
            name='location_updated_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]