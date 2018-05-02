from django.conf.urls import url

from . import views, user_views, cloud_views, group_views
#from . import views, cloud_views, user_views

urlpatterns = [

    url(r'^$',                                 cloud_views.status,          name='cloud-status'),


    url(r'^cloud/add',                         cloud_views.add,             name='cloud-add'),
    url(r'^cloud/delete',                      cloud_views.delete,          name='cloud-delete'),
    url(r'^cloud/list/(?P<selector>)',         cloud_views.list,            name='cloud-list'),
    url(r'^cloud/prepare',                     cloud_views.prepare,         name='cloud-prepare'),
    url(r'^cloud/status',                      cloud_views.status,          name='cloud-status'),
    url(r'^cloud/update',                      cloud_views.update,          name='cloud-update'),
    url(r'^cloud/yaml_add',                    cloud_views.yaml_add,        name='yaml-add'),
    url(r'^cloud/yaml_delete',                 cloud_views.yaml_delete,     name='yaml-delete'),
    url(r'^cloud/yaml_fetch',                  cloud_views.yaml_fetch,      name='yaml-fetch'),
    url(r'^cloud/yaml_update',                 cloud_views.yaml_update,     name='yaml-update'),

    url(r'^group/list',                        group_views.list,            name='group-list'),
    url(r'^group/modify',                      group_views.modify,          name='group-modify'),
    url(r'^group/prepare',                     group_views.prepare,         name='group-prepare'),
#   url(r'^group/yaml_fetch',                  group_views.yaml_fetch,      name='group-list'),
#   url(r'^group/yaml_modify',                 group_views.yaml_modify,     name='group-modify'),

#   url(r'^job/list',                          job_views.list,              name='list'),
#   url(r'^job/modify',                        job_views.modify,            name='list'),

    url(r'^user/add',                          user_views.add,              name='add'),
    url(r'^user/delete',                       user_views.delete,           name='delete'),
#    url(r'^user/list',                         user_views.manage,           name='manage'),
    url(r'^user/list',                         user_views.list,             name='list'),
    url(r'^user/update',                       user_views.update,           name='update'),

#   url(r'^vm/list',                           vm_views.list,               name='list'),
#   url(r'^vm/modify',                         vm_views.modify,             name='list'),

]
