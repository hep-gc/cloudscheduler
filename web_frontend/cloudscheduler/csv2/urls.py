from django.conf.urls import url

from . import views, user_views, group_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^manage_users/', user_views.manage_users, name='manage_users'),
    url(r'^create_user/', user_views.create_user, name='create_user'),
    url(r'^update_user/', user_views.update_user, name='update_user'),
    url(r'^delete_user/', user_views.delete_user, name='delete_user'),
    url(r'^user_settings/', user_views.user_settings, name='user_settings'),
    url(r'^system_status/', group_views.system_status, name='system_status'),
    url(r'^system_status/(?P<group_name>.+)/$', group_views.system_status, name='system_status'),
    url(r'^manage_clouds/', group_views.manage_clouds, name='manage_clouds'),
    url(r'^update_cloud/', group_views.add_cloud_resources, name='update_cloud'),
]
