# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import logtailer.fields
import logtailer.utils


class Migration(migrations.Migration):

    dependencies = [
        ('logtailer', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logfile',
            options={
                'verbose_name': 'Log file',
                'verbose_name_plural': 'Log files'
            },
        ),
        migrations.AlterModelOptions(
            name='logsclipboard',
            options={
                'verbose_name': 'logs clipboard',
                'verbose_name_plural': 'logs clipboard'
            },
        ),
        migrations.AlterField(
            model_name='logfile',
            name='path',
            field=logtailer.fields.DynamicFilePathField(
                path=logtailer.utils.log_directory,
                max_length=500,
                verbose_name='path',
                match=b'.*\\.(log)$',
                blank=True
            ),
        ),
        migrations.AlterField(
            model_name='logsclipboard',
            name='log_file',
            field=models.ForeignKey(
                verbose_name='log file',
                to='logtailer.LogFile'
            ),
        ),
    ]
