from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.models import User #to get auth_user table
from .models import user

# Returns the current authorized user from metadata
def getAuthUser(request):
    return request.META.get('REMOTE_USER')

def getcsv2User(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = user.objects.all()
    for csv2_user in csv2_user_list:
        if csv2_user.username == authorized_user or csv2_user.cert_dn == authorized_user:
            return csv2_user
    return 


def verifyUser(request):
    auth_user = getAuthUser(request)
    
    csv2_user_list = user.objects.all()
    #try to find a user that has "auth_user" as username or cert_dn
    # the uniqueness here will be forced on user creation
    for user in csv2_user_list:
        if user.username == auth_user or user.cert_dn == auth_user:
            return True

    return False

def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    return authorized_user.is_superuser



def index(request):
    if verifyUser(request):
        csv2_user = getcsv2User(request)
        return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % csv2_user.username)
