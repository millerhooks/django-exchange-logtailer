from django.contrib import admin
from django.conf.urls import url
from django.conf import settings

from logtailer.models import LogFile, Filter, LogsClipboard
from logtailer.views import enable_log, disable_log, clear_log, export_log
from logtailer.utils import logging_timer_expired, logging_timeout


class LogFileAdmin(admin.ModelAdmin):
    # list_display = ('__unicode__', 'path')
    list_display = ('__unicode__',)  # don't show full path to log
    # TODO: Figure out how to strip the log directory from path

    # noinspection PyClassHasNoInit
    class Media:
        js = (settings.STATIC_URL + 'logtailer/js/jquery.colorbox.js',)
        css = {
            'all': (settings.STATIC_URL + 'logtailer/css/colorbox.css',)
        }

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['log_enabled'] = not logging_timer_expired()
        extra_context['log_timeout'] = int(logging_timeout()) / 60
        return super(LogFileAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    def get_urls(self):
        cur_urls = super(LogFileAdmin, self).get_urls()
        urlpatterns = [
            url(r'^enable-log/$',
                self.admin_site.admin_view(enable_log),
                name="enable_log"
                ),
            url(r'^disable-log/$',
                self.admin_site.admin_view(disable_log),
                name="disable_log"
                ),
            url(r'^clear-log/$',
                self.admin_site.admin_view(clear_log),
                name="clear_log"),
            url(r'^export-log/$',
                self.admin_site.admin_view(export_log),
                name="export_log"),
        ]
        return urlpatterns + cur_urls


class FilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'regex')   


class LogsClipboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'notes', 'log_file')
    readonly_fields = ('name', 'notes', 'logs', 'log_file')


admin.site.register(LogFile, LogFileAdmin)
admin.site.register(Filter, FilterAdmin)
admin.site.register(LogsClipboard, LogsClipboardAdmin)
