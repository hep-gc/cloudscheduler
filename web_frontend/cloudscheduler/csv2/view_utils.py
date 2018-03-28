from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

'''
UTILITY FUNCTIONS
'''

# Returns the current authorized user from metadata
def getAuthUser(request):
    return request.META.get('REMOTE_USER')

# returns the csv2 user object matching the authorized user from header metadata
def getcsv2User(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_cn == authorized_user:
            return user
    raise PermissionDenied


def verifyUser(request):
    auth_user = getAuthUser(request)

    csv2_user_list = csv2_user.objects.all()
    #try to find a user that has "auth_user" as username or cert_cn
    # the uniqueness here will be forced on user creation
    for user in csv2_user_list:
        if user.username == auth_user or user.cert_cn == auth_user:
            return True

    return False


def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_cn == authorized_user:
            return user.is_superuser
    return False


def _render(request, template, context):
    """
    If the "Accept" HTTP header contains "application/json", return a json string. Otherwise,
    return an HTML string.
    """

    from django.shortcuts import render
    from django.http import HttpResponse
    from django.core import serializers
    from django.db.models.query import QuerySet
    from sqlalchemy.engine import result as sql_result
    import decimal
    import json

    class csv2Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)

            return json.JSONEncoder.default(self, obj)

    if request.META['HTTP_ACCEPT'] == 'application/json':
        serialized_context = {}
        for item in context:
            if isinstance(context[item], int):
                serialized_context[item] = context[item]
            elif isinstance(context[item], QuerySet):
                serialized_context[item] = serializers.serialize("json", context[item])
            elif isinstance(context[item], sql_result.ResultProxy):
                serialized_context[item] = json.dumps([dict(r) for r in context[item]], cls=csv2Encoder)
            elif isinstance(context[item], dict) and 'ResultProxy' in context[item]:
                serialized_context[item] = json.dumps(context[item]['ResultProxy'], cls=csv2Encoder)
            else:
                serialized_context[item] = str(context[item])
                if serialized_context[item] == 'None':
                  serialized_context[item] = None
        response = HttpResponse(json.dumps(serialized_context, cls=csv2Encoder), content_type='application/json')
    else:
        response = render(request, template, context)
    return response
