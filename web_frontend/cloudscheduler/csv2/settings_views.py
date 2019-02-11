from django.conf import settings
config = settings.CSV2_CONFIG

from django.views.decorators.csrf import requires_csrf_token
from .view_utils import render, set_user_groups
from cloudscheduler.lib.schema import *
from django.contrib.auth import get_user, logout

import time


# lno: SV - error code identifier.

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
    rc, msg, active_user, user_groups = set_user_groups(config, request, False)
    if rc != 0:
        config.db_close()
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    

    context = {
            'active_user': active_user.username,
            'active_group': active_user.active_group,
            'super_user': active_user.is_superuser,
            'user_groups': user_groups,
            'response_code': 0,
            'message': None,
            'version': config.get_version() 
    }
    config.db_close()
    print("Prepare time: %f.5" % time.time())


    return render(request, 'csv2/settings.html', context)

#-------------------------------------------------------------------------------
