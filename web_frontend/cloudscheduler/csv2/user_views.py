from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from django.contrib.auth.models import User #to get auth_user table
from .models import user as csv2_user

from .view_utils import getAuthUser, getcsv2User, verifyUser, getSuperUserStatus

import bcrypt



'''
USER RELATED WEB REQUEST VIEWS
'''

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
        cert_cn = request.POST.get('common_name')

        # Need to perform several checks
        # 1. Check that the username is valid (ie no username or cert_cn by that name)
        # 2. Check that the cert_cn is not equal to any username or other cert_cn
        # 3. Check that password isn't empty or less than 4 chars
        # 4. Check that both passwords are the same

        csv2_user_list = csv2_user.objects.all()
        for registered_user in csv2_user_list:
            #check #1
            if user == registered_user.username or user == registered_user.cert_cn:
                #render manage users page with error message
                return manage_users(request, err_message="Username unavailable")
            #check #2
            if cert_cn is not None and (cert_cn == registered_user.username or cert_cn == registered_user.cert_cn):
                return manage_users(request, err_message="Username unavailable or conflicts with a registered Distinguished Name")
        #check #3 part 1
        if pass1 is None or pass2 is None:
            return manage_users(request, err_message="Password is empty")
        if len(pass1)<4:
            return manage_users(request, err_message="Password must be at least 4 characters")
        #check #4
        if pass1 != pass2:
            return manage_users(request, err_message="Passwords do not match")

        # After checks are made use bcrypt to encrypt password.
        hashed_pw = bcrypt.hashpw(pass1.encode(), bcrypt.gensalt(prefix=b"2a"))

        #if all the checks passed and the hashed password has been generated create a new user object and save import
        new_usr = csv2_user(username=user, password=hashed_pw, cert_cn=cert_cn, is_superuser=False)
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
        cert_cn = request.POST.get('common_name')
        su_status = request.POST.get('is_superuser')
        if not su_status:
            su_status=False
        else:
            su_status=True

        # Need to perform two checks
        # 1. Check that the new username is valid (ie no username or cert_cn by that name)
        #   if the username hasn't changed we can skip this check since it would have been done on creation.
        # 2. Check that the cert_cn is not equal to any username or other cert_cn

        for registered_user in csv2_user_list:
            #check #1
            if not new_username == user_to_update.username:
                if user == registered_user.username or user == registered_user.cert_cn:
                    #render manage users page with error message
                    return manage_users(request, err_message="Unable to update user: new username unavailable")
            #check #2
            if cert_cn is not None and registered_user.username != user_to_update.username and (cert_cn == registered_user.username or cert_cn == registered_user.cert_cn):
                return manage_users(request, err_message="Unable to update user: Username unavailable or conflicts with a registered Distinguished Name")
        user_to_update.username = new_username
        user_to_update.cert_cn = cert_cn
        user_to_update.is_superuser = su_status
        user_to_update.save()
        return manage_users(request, message="User updated")

    else:
        #not a post, return to manage users page
        return manage_users(request)

def delete_user(request):
    if not verifyUser(request):
        raise PermissionDenied
    if not getSuperUserStatus(request):
        raise PermissionDenied

    if request.method == 'POST':
        user = request.POST.get('username')
        user_obj = csv2_user.objects.filter(username=user)
        user_obj.delete()
        return manage_users(request, message="User deleted")
    return False

def user_settings(request):
    if not verifyUser(request):
        raise PermissionDenied

    if request.method == 'POST':
        # proccess update

        csv2_user_list = csv2_user.objects.all()
        user_to_update = getcsv2User(request)
        new_username = request.POST.get('username')
        cert_cn = request.POST.get('common_name')
        new_pass1 = request.POST.get('password1')
        new_pass2 = request.POST.get('password2')
        
        # Need to perform three checks
        # 1. Check that the new username is valid (ie no username or cert_cn by that name)
        #   if the username hasn't changed we can skip this check since it would have been done on creation.
        # 2. Check that the cert_cn is not equal to any username or other cert_cn
        # 3. If the passwords aren't 0-3 chars and check if they are the same.
        for registered_user in csv2_user_list:
            #check #1
            if not new_username == user_to_update.username:
                if new_username == registered_user.username or new_username == registered_user.cert_cn:
                    context = {
                        'user_obj':user_to_update,
                        'err_message': "Unable to update user: new username unavailable"
                    }
                    return render(request, 'csv2/user_settings.html', context)
            #check #2
            if cert_cn is not None and registered_user.username != user_to_update.username and (cert_cn == registered_user.username or cert_cn == registered_user.cert_cn):
                context = {
                    'user_obj':user_to_update,
                    'err_message': "Unable to update user: Username or DN unavailable or conflicts with a registered Distinguished Name"
                }
                return render(request, 'csv2/user_settings.html', context)

        #check #3 part 1
        if new_pass1 is None or new_pass2 is None:
            context = {
                'user_obj':user_to_update,
                'err_message': "Password is empty"
            }
            return render(request, 'csv2/user_settings.html', context)
        #check #3 part 2
        if len(new_pass1)<4:
            context = {
                'user_obj':user_to_update,
                'err_message': "Password must be at least 4 characters"
            }
            return render(request, 'csv2/user_settings.html', context)
        #check #3 part 3
        if new_pass1 != new_pass2:
            context = {
                'user_obj':user_to_update,
                'err_message': "Passwords do not match"
            }
            return render(request, 'csv2/user_settings.html', context)

        #if we get here all the checks have passed and we can safely update the user data
        user_to_update.username=new_username
        if new_pass1:
            user_to_update.password = bcrypt.hashpw(new_pass1.encode(), bcrypt.gensalt(prefix=b"2a"))
        user_to_update.cert_cn=cert_cn
        user_to_update.save()
        context = {
                'user_obj':user_to_update,
                'message': "Update Successful"
            }
        return render(request, 'csv2/user_settings.html', context)

    else:
        #render user_settings template
        user_obj=getcsv2User(request)

        context = {
            'user_obj': user_obj,
        }
        return render(request, 'csv2/user_settings.html', context)
