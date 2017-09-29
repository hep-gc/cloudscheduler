from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

import bcrypt

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
        if user.username == authorized_user or user.cert_dn == authorized_user:
            return user
    return None


def verifyUser(request):
    auth_user = getAuthUser(request)
    
    csv2_user_list = csv2_user.objects.all()
    #try to find a user that has "auth_user" as username or cert_dn
    # the uniqueness here will be forced on user creation
    for user in csv2_user_list:
        if user.username == auth_user or user.cert_dn == auth_user:
            return True

    return False

def getSuperUserStatus(request):
    authorized_user = getAuthUser(request)
    csv2_user_list = csv2_user.objects.all()
    for user in csv2_user_list:
        if user.username == authorized_user or user.cert_dn == authorized_user:
            return user.is_superuser
    return False



'''
WEB REQUEST VIEWS
'''

def index(request):
    if verifyUser(request):
        csv2_user = getcsv2User(request)
        return HttpResponse("Hello, %s. You're at the cloudscheduler v2 index." % csv2_user.username)

def manage_users(request, message=None, err_message=None):
    if not verifyUser(request):
        raise PermissionDenied

    if not getSuperUserStatus(request):
        raise PermissionDenied

    user_list = csv2_user.objects.all()
    context = {
            'user_list': user_list,
            'message': message,
            'err_message': err_message

    }
    return render(request, 'csv2/manage_users.html', context)


def create_user(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    if request.method == 'POST':
        user = request.POST.get('username')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        cert_dn = request.POST.get('distinguished_name')

        # Need to perform several checks
        # 1. Check that the username is valid (ie no username or cert_dn by that name)
        # 2. Check that the cert_dn is not equal to any username or other cert_dn
        # 3. Check that both passwords are the same

        csv2_user_list = csv2_user.objects.all()
        for registered_user in csv2_user_list:
            #check #1
            if user == registered_user.username or user == registered_user.cert_dn:
                #render manage users page with error message
                return manage_users(request, err_message="Username unavailable")
            #check #2
            if cert_dn is not None and (cert_dn == registered_user.username or cert_dn == registered_user.cert_dn):
                return manage_users(request, err_message="Username unavailable or conflicts with a registered Distinguished Name")

        #check #3
        if pass1 != pass2:
            return manage_users(request, err_message="Passwords do not match")

        # After checks are made use bcrypt to encrypt password.
        hashed_pw = bcrypt.hashpw(pass1.encode(), bcrypt.gensalt(prefix=b"2a"))

        #if all the checks passed and the hashed password has been generated create a new user object and save import
        new_usr = csv2_user(username=user, password=hashed_pw, cert_dn=cert_dn, is_superuser=False)
        new_usr.save()
        return manage_users(request, message="User added")
    else:
        #not a post, return to manage users page
        return manage_users(request)

def update_user(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied


    if request.method == 'POST':
        csv2_user_list = csv2_user.objects.all()
        user_to_update = csv2_user.objects.filter(username=request.POST.get('old_usr'))[0]
        new_username = request.POST.get('username')
        cert_dn = request.POST.get('distinguished_name')
        su_status = request.POST.get('is_superuser')
        if not su_status:
            su_status=False
        else:
            su_status=True

        # Need to perform two checks
        # 1. Check that the new username is valid (ie no username or cert_dn by that name)
        #   if the username hasn't changed we can skip this check since it would have been done on creation.
        # 2. Check that the cert_dn is not equal to any username or other cert_dn

        for registered_user in csv2_user_list:
            #check #1
            if not new_username == user_to_update.username:
                if user == registered_user.username or user == registered_user.cert_dn:
                    #render manage users page with error message
                    return manage_users(request, err_message="Unable to update user: new username unavailable")
            #check #2
            if cert_dn is not None and registered_user.username != user_to_update.username and (cert_dn == registered_user.username or cert_dn == registered_user.cert_dn):
                return manage_users(request, err_message="Unable to update user: Username unavailable or conflicts with a registered Distinguished Name")
        user_to_update.username = new_username
        user_to_update.cert_dn = cert_dn
        user_to_update.is_superuser = su_status
        user_to_update.save()
        return manage_users(request, message="User updated")

    else:
        #not a post, return to manage users page
        return manage_users(request)
