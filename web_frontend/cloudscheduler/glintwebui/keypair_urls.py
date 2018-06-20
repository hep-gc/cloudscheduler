from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^/(?P<group_name>.+)/$', views.manage_keys, name='manage_keys'),
    url(r'^/$', views.manage_keys, name='manage_keys'),
    url(r'^save_keypairs/(?P<group_name>.+)/$', views.save_keypairs, name='save_keypairs'),
    url(r'^add_key/$', views.upload_keypair, name='upload_keypair'),
    url(r'^new_key/$', views.new_keypair, name='new_keypair')
]