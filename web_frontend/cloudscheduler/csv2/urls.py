from django.conf.urls import url

from . import views, user_views, group_views

urlpatterns = [
    url(r'^status/', views.index, name='index'),
    url(r'^users/', user_views.manage_users, name='manage'),
    url(r'^users/create', user_views.create_user, name='create'),
    url(r'^users/update', user_views.update_user, name='update'),
    url(r'^users/delete', user_views.delete_user, name='delete'),
    url(r'^users/settings/', user_views.user_settings, name='settings'),
    url(r'^status/', group_views.system_status, name='status'),
    url(r'^status/(?P<group_name>.+)/$', group_views.system_status, name='status'),
    url(r'^clouds/', group_views.manage_clouds, name='list'),
    url(r'^clouds/update', group_views.add_cloud_resources, name='update'),
    url(r'^clouds/list/', group_views.manage_clouds, name='list'),
]
