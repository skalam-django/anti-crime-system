# Generated by Django 3.0 on 2020-02-17 20:32

import django.contrib.postgres.fields
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MainUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=50, unique=True)),
                ('device_id', models.IntegerField(blank=True, null=True)),
                ('emergency_contacts', django.contrib.postgres.fields.ArrayField(base_field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None), blank=True, null=True, size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'main_user',
                'managed': True,
            },
        ),
        migrations.AddIndex(
            model_name='mainuser',
            index=models.Index(fields=['uid', 'device_id'], name='main_user_uid_8eb8ae_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='mainuser',
            unique_together={('uid', 'device_id')},
        ),
    ]
