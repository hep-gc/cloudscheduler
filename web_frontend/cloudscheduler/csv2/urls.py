from django.conf.urls import url

from . import views, user_views, cloud_views, group_views
#from . import views, cloud_views, user_views

urlpatterns = [

    url(r'^$',                         cloud_views.status,          name='status'),

    url(r'^cloud/list/(?P<cloud>)',    cloud_views.list,            name='list'),
    url(r'^cloud/modify',              cloud_views.modify,          name='modify'),
    url(r'^cloud/prepare',             cloud_views.prepare,         name='prepare'),
    url(r'^cloud/status',              cloud_views.status,          name='status'),

#   url(r'^cloud_yaml/fetch',          cloud_yaml_views.fetch,      name='list'),
#   url(r'^cloud_yaml/modify',         cloud_yaml_views.modify,     name='modify'),
#   url(r'^cloud_yaml/prepare',        cloud_yaml_views.prepare,    name='prepare'),
    
    url(r'^group/list',                group_views.list,            name='list'),
    url(r'^group/modify',              group_views.modify,          name='modify'),
    url(r'^group/prepare',             group_views.prepare,         name='prepare'),

#   url(r'^group_yaml/fetch',          group_yaml_views.fetch,      name='list'),
#   url(r'^group_yaml/modify',         group_yaml_views.modify,     name='modify'),
#   url(r'^group_yaml/prepare',        group_yaml_views.prepare,    name='prepare'),

#   url(r'^job/list',                  job_views.list,              name='list'),
#   url(r'^job/modify',                job_views.modify,            name='list'),

    url(r'^user/create',               user_views.create,           name='create'),
    url(r'^user/delete',               user_views.delete,           name='delete'),
    url(r'^user/list',                 user_views.manage,           name='manage'),
    url(r'^user/update',               user_views.update,           name='update'),

#   url(r'^vm/list',                   vm_views.list,               name='list'),
#   url(r'^vm/modify',                 vm_views.modify,             name='list'),

]
