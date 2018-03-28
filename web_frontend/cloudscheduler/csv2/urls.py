from django.conf.urls import url

from . import views, user_views, cloud_views, group_views

urlpatterns = [
    url(r'^$',             cloud_views.status,  name='satus'),

    url(r'^cloud/list',    cloud_views.list,    name='list'),
    url(r'^cloud/prepare', cloud_views.prepare, name='prepare'),
    url(r'^cloud/status',  cloud_views.status,  name='status'),
    url(r'^cloud/update',  cloud_views.update,  name='update'),

    url(r'^group/list',    group_views.list,    name='list'),
    url(r'^group/update',  group_views.update,  name='update'),

    url(r'^user/create',   user_views.create,   name='create'),
    url(r'^user/delete',   user_views.delete,   name='delete'),
    url(r'^user/list',     user_views.manage,   name='manage'),
    url(r'^user/update',   user_views.update,   name='update'),

]
