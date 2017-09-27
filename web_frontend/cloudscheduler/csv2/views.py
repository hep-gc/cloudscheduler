from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.models import User #to get auth_user table
from .models import user

# Returns the current authorized user from metadata
def getAuthUser(request):
    return request.META.get('REMOTE_USER')

def getcsv2User(request):
    authorized_user = getAuthUser(request)
    auth_user_obj = User.objects.get(username=auth_user)
    return user.objects.get(username=auth_user_obj.csv2_user)


def verifyUser(request):
    auth_user = getAuthUser(request)
    auth_user_obj = User.objects.get(username=auth_user)
    # check if the authenticated user has a csv2 username in the auth table
    if auth_user_obj.csv2_user is not null:
        username = auth_user_obj.csv2_user
        # Double check to see this is a valid user
        csv2_user_list = user.objects.all()
        for user in csv2_user_list:
            if user.username == username:
                return True

    # if they don't then they either are not a csv2 user or this is the first time logging in with a certificate
    else:
        csv2_user_list = user.objects.all()
        #try to find a user that has "auth_user" as cert_dn
        for user in csv2_user_list:
            if user.cert_dn == auth_user:
                # found a cert DN that matches the one that was used for authentication - assign csv2_user
                auth_user_obj.csv2_user = user.username
                auth_user_obj.save()
                return True

    return False

def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    return authorized_user.is_superuser



def index(request):
    if verifyUser(request):
        csv2_user = getcsv2User(request)
        return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % csv2_user)
