from django.conf.urls import url

from . import keypair_views

urlpatterns = [
    url(r'^(?P<group_name>.+)/$', keypair_views.manage_keys, name='manage_keys'),
    url(r'^', views.manage_keys, name='manage_keys'),
    url(r'^save_keypairs/(?P<group_name>.+)/$', keypair_views.save_keypairs, name='save_keypairs'),
    url(r'^add_key/$', keypair_views.upload_keypair, name='upload_keypair'),
    url(r'^new_key/$', keypair_views.new_keypair, name='new_keypair')
]