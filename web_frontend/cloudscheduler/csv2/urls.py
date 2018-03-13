from django.conf.urls import url

from . import views, user_views, cloud_views

urlpatterns = [
    url(r'^status/', views.index, name='index'),
    url(r'^users/', user_views.manage, name='manage'),
    url(r'^users/create', user_views.create, name='create'),
    url(r'^users/update', user_views.update, name='update'),
    url(r'^users/delete', user_views.delete, name='delete'),
    url(r'^users/settings/', user_views.settings, name='settings'),
    url(r'^status/', cloud_views.status, name='status'),
    url(r'^status/(?P<group_name>.+)/$', cloud_views.status, name='status'),
    url(r'^clouds/', cloud_views.list, name='list'),
    url(r'^clouds/update', cloud_views.add_resources, name='update'),
    url(r'^clouds/list/', cloud_views.list, name='list'),
]