from django.urls import re_path

from . import keypair_views

urlpatterns = [
    re_path(r'^$', keypair_views.manage_keys, name='manage_keys'),
    re_path(r'^save_keypairs/(?P<group_name>.+)/$', keypair_views.save_keypairs, name='save_keypairs'),
    re_path(r'^add_key/$', keypair_views.upload_keypair, name='upload_keypair'),
    re_path(r'^new_key/$', keypair_views.new_keypair, name='new_keypair')
]
