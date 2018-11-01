from django.db import models
from django.utils.translation import ugettext_lazy as _

from logtailer.fields import DynamicFilePathField
from logtailer.utils import log_directory, log_file_extensions


class LogFile(models.Model):
    name = models.CharField(_('name'), max_length=180)
    path = DynamicFilePathField(
        _('path'),
        path=log_directory,
        match=log_file_extensions,
        max_length=500,
        blank=True,
    )
    path = models.CharField(_('path'), max_length=500)

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        j
        return str(self.__unicode__())

    class Meta:
        verbose_name = _('Log file')
        verbose_name_plural = _('Log files')


class Filter(models.Model):
    name = models.CharField(_('name'), max_length=180)
    regex = models.CharField(_('regex'), max_length=500)

    def __unicode__(self):
        return '%s | %s: %s ' % (self.name, _('pattern'), self.regex)

    def __str__(self):
        return str(self.__unicode__())

    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')


class LogsClipboard(models.Model):
    name = models.CharField(_('name'), max_length=180)
    notes = models.TextField(_('notes'), blank=True, null=True)
    logs = models.TextField(_('logs'))
    log_file = models.ForeignKey(LogFile, verbose_name=_('log file'))

    def __unicode__(self):
        return "%s" % self.name

    def __str__(self):
        return str(self.__unicode__())

    class Meta:
        verbose_name = _('logs clipboard')
        verbose_name_plural = _('logs clipboard')
