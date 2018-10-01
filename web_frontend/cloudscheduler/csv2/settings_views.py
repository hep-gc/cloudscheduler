from django.views.decorators.csrf import requires_csrf_token
from .view_utils import db_open, getSuperUserStatus, render, set_user_groups
from cloudscheduler.lib.schema import *
from django.contrib.auth import get_user, logout

import time

from .view_utils import \
    db_close

# lno: SV - error code identifier.

#-------------------------------------------------------------------------------

@requires_csrf_token
def log_out(request):
    """
    Stub for user log out.
    """

    logout(request)




    context = {
            'response_code': 0,
            'message': None
    }

    return render(request, 'csv2/status.html', context)

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

    # open the database.

    db_engine, db_session, db_connection, db_map = db_ctl = db_open()

    # Retrieve the active user, associated group list and optionally set the active group.
    rc, msg, active_user, user_groups = set_user_groups(request, db_ctl)
    if rc != 0:
        db_close(db_ctl)
        return render(request, 'csv2/clouds.html', {'response_code': 1, 'message': msg})

    db_close(db_ctl)

    context = {
            'active_user': active_user,
            'active_group': active_user.active_group,
            'super_user': getSuperUserStatus(request),
            'user_groups': user_groups,
            'response_code': 0,
            'message': None
    }
    print("Prepare time: %f.5" % time.time())


    return render(request, 'csv2/settings.html', context)

