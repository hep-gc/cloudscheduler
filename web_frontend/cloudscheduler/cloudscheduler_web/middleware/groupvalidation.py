from csv2.cloudscheduler.lib.view_utils import set_user_groups, render
from django.http.response import HttpResponse as HttpResponse 
from django.http.request import HttpRequest as HttpRequest 

from django.conf import settings
config = settings.CSV2_CONFIG 

NOGROUP_ACCESSIBLE_PAGES = [
    '/settings/log-out/',
    '/settings/log-out',
    '/user/settings/',
    '/user/list',
    '/server/config/',
    '/group/list/',
    '/user/list/',
]

class GroupValidate:

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        config.db_open()
        config.refresh()

        rc, msg, active_user = set_user_groups(config, request, super_user=False)
        config.db_close()
        nogroup = (active_user.active_group == "-" or len(active_user.user_groups) < 1)
        
        # get response
        if request.method == "GET" and nogroup and request.path not in NOGROUP_ACCESSIBLE_PAGES:
            # render the error page
            context = {
                'active_user': active_user.username,
                'active_group': active_user.active_group,
                'user_groups': active_user.user_groups,
                'response_code': rc,
                'message': msg,
                'is_superuser': active_user.is_superuser,
                'version': config.get_version()
            } 
            # show error page
            response = render(request, 'csv2/nogroup.html', context)
        else: 
            # continue to view
            response = self.get_response(request)

        return response
