from django.conf import settings
config = settings.CSV2_CONFIG

from django.views.decorators.csrf import requires_csrf_token
from cloudscheduler.lib.view_utils import lno, render, set_user_groups
from cloudscheduler.lib.schema import *
from django.contrib.auth import get_user, logout

import time


# lno: SV - error code identifier.
MODID = 'SV'

#-------------------------------------------------------------------------------

@requires_csrf_token
def log_out(request):

    context = {
            'response_code': 0,
            'message': None
    }

    return render(request, 'csv2/logout.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
def preferences(request):
    """
    Stub for user preferences (including reset password).
    """

    context = {
            'response_code': 0,
            'message': None
    }

    return render(request, 'csv2/settings.html', context)

#-------------------------------------------------------------------------------

@requires_csrf_token
def prepare(request):
    """
    This function returns a minimal response plus a CSRF.
    """
    config.db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user = set_user_groups(config, request, super_user=False)
    if rc != 0:
        if (active_user.active_group == '-' or len(active_user.user_groups) < 1) and active_user.is_superuser:
            group_recovery = True
        else:
            config.db_close()
            # if active_user.active_group == '-' or len(active_user.available_groups) < 1:
            #     return render(request, 'csv2/nogroups.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
            return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': '%s %s' % (lno(MODID), msg)})
    
    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'super_user': active_user.is_superuser,
            'user_groups': active_user.user_groups,
            'response_code': 0,
            'message': None,
            'version': config.get_version() 
    }
    if group_recovery:
        context['message'] = "The active user belongs to no groups"

    config.db_close()

    return render(request, 'csv2/settings.html', context)

#-------------------------------------------------------------------------------
