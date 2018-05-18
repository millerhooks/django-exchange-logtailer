import os
import json
from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from logtailer.models import LogsClipboard, LogFile
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.html import escape
from django.utils import safestring
from django.conf import settings

from logtailer.utils import (
    remove_logging_timer,
    set_logging_timer,
    log_file,
    file_readable,
    logging_timer_exists,
)

HISTORY_LINES = getattr(settings, 'LOGTAILER_HISTORY_LINES', 0)
TIMEOUT = getattr(settings, 'LOGTAILER_TIMEOUT', 600)


@staff_member_required
def read_logs(request):
    context = {}
    return render_to_response('logtailer/log_reader.html',
                              context, 
                              RequestContext(request, {}),)


def get_history(f, lines=HISTORY_LINES):
    buffer_size = 1024
    f.seek(0, os.SEEK_END)
    tell_bytes = f.tell()
    size = lines
    block = -1
    data = []
    while size > 0 and tell_bytes > 0:
        if tell_bytes - buffer_size > 0:
            # Seek back one whole buffer_size
            f.seek(block*buffer_size, 2)
            # read buffer
            data.append(f.read(buffer_size))
        else:
            # file too small, start from beginning
            f.seek(0, 0)
            # only read what was not read
            data.append(f.read(tell_bytes))
        lines_found = data[-1].count('\n')
        size -= lines_found
        tell_bytes -= buffer_size
        block -= 1
    return ''.join(data).splitlines(True)[-lines:]


@staff_member_required
def get_log_lines(request, file_id, history=False):
    try:
        file_record = LogFile.objects.get(id=file_id)
    except LogFile.DoesNotExist:
        return HttpResponse(json.dumps([_('error_logfile_notexist')]),
                            content_type='text/html')
    content = []
    log_file = open(file_record.path, 'r')

    if history:
        content = get_history(log_file)
        content = [escape(line)
                   .replace('\t', '  ').replace('  ', '&nbsp;&nbsp;')
                   .replace('\n', '<br/>') for line in content]
    else:
        last_position = request.session.get('file_position_%s' % file_id)
        log_file.seek(0, os.SEEK_END)
        if last_position and last_position <= log_file.tell():
            log_file.seek(last_position)

        for line in log_file:
            content.append('%s' % escape(line)
                           .replace('\t', '  ').replace('  ', '&nbsp;&nbsp;')
                           .replace('\n', '<br/>'))

    request.session['file_position_%s' % file_id] = log_file.tell()
    log_file.close()
    return HttpResponse(json.dumps(content), content_type='application/json')


@staff_member_required
def save_to_clipoard(request):
    LogsClipboard(name=request.POST['name'],
                  notes=request.POST['notes'],
                  logs=request.POST['logs'],
                  log_file=LogFile.objects
                  .get(id=int(request.POST['file']))).save()
    return HttpResponse(_('loglines_saved'), content_type='text/html')


@staff_member_required
def enable_log(request):
    try:
        set_logging_timer()
        messages.warning(
            request,
            safestring.mark_safe(
                "<b>IMPORTANT</b>: Debug logging will <b>ONLY BE ENABLED "
                "FOR {0} MINUTES.</b>".format(int(TIMEOUT) / 60))
        )
    except IOError:
        messages.error(
            request,
            "Could not enable logging."
        )
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@staff_member_required
def disable_log(request):
    try:
        remove_logging_timer()
    except OSError:
        messages.error(
            request,
            "Could not disable logging."
        )
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@staff_member_required
def clear_log(request):
    if logging_timer_exists():
        with open(log_file(), 'w') as f:
            f.write('')
        messages.info(
            request,
            "Log cleared."
        )
    else:
        messages.warning(
            request,
            "Log file not writable."
        )
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@staff_member_required
def export_log(request):
    if file_readable(log_file()):
        tstamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        name, ext = os.path.splitext(os.path.basename(log_file()))
        with open(log_file(), 'r') as f:
            response = HttpResponse(
                f.read(), content_type='text/plain', charset='utf-8')
        response['Content-Disposition'] = \
            'attachment; filename={0}_{1}.{2}'.format(name, tstamp, ext)
        return response
    else:
        messages.warning(
            request,
            "Log file not readable."
        )
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
