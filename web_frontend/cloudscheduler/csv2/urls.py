from django.conf.urls import url

from . import views, user_views, group_views

urlpatterns = [
    url(r'^status/', views.index, name='index'),
    url(r'^users/', user_views.manage_users, name='manage'),
    url(r'^user/create', user_views.create_user, name='create'),
    url(r'^user/update', user_views.update_user, name='update'),
    url(r'^user/delete', user_views.delete_user, name='delete'),
    url(r'^user/settings/', user_views.user_settings, name='user_settings'),
    url(r'^status/', group_views.system_status, name='system_status'),
    url(r'^status/(?P<group_name>.+)/$', group_views.system_status, name='system_status'),
    url(r'^clouds/', group_views.manage_clouds, name='manage_clouds'),
    url(r'^cloud/update', group_views.add_cloud_resources, name='update_cloud'),
    url(r'^cloud/list/', group_views.manage_clouds, name='cloud_list'),
]
