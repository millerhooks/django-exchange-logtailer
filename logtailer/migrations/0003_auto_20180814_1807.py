# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import logtailer.fields
import logtailer.utils


class Migration(migrations.Migration):

    dependencies = [
        ('logtailer', '0002_auto_20180518_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logfile',
            name='path',
            field=logtailer.fields.DynamicFilePathField(
                path=logtailer.utils.log_directory,
                max_length=500,
                verbose_name='path',
                match=logtailer.utils.log_file_extensions,
                blank=True),
        ),
    ]
