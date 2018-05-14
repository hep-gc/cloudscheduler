from django.conf.urls import url

from . import views, cloud_views, group_views, settings_views, user_views

urlpatterns = [

    url(r'^$',                                 cloud_views.status,          name='cloud-status'),


    url(r'^cloud/add',                         cloud_views.add,             name='cloud-add'),
    url(r'^cloud/delete',                      cloud_views.delete,          name='cloud-delete'),
    url(r'^cloud/list/(?P<selector>)',         cloud_views.list,            name='cloud-list'),
    url(r'^cloud/status',                      cloud_views.status,          name='cloud-status'),
    url(r'^cloud/update',                      cloud_views.update,          name='cloud-update'),
    url(r'^cloud/yaml-add',                    cloud_views.yaml_add,        name='cloud-yaml-add'),
    url(r'^cloud/yaml-delete',                 cloud_views.yaml_delete,     name='cloud-yaml-delete'),
    url(r'^cloud/yaml-fetch/(?P<selector>)',   cloud_views.yaml_fetch,      name='cloud-yaml-fetch'),
    url(r'^cloud/yaml-update',                 cloud_views.yaml_update,     name='cloud-yaml-update'),

    url(r'^group/add',                         group_views.add,             name='group-add'),
    url(r'^group/defaults',                    group_views.defaults,        name='group-defaults'),
    url(r'^group/delete',                      group_views.delete,          name='group-delete'),
    url(r'^group/list/(?P<selector>)',         group_views.list,            name='group-list'),
    url(r'^group/update',                      group_views.update,          name='group-update'),
    url(r'^group/yaml-add',                    group_views.yaml_add,        name='group-yaml-add'),
    url(r'^group/yaml-delete',                 group_views.yaml_delete,     name='group-yaml-delete'),
    url(r'^group/yaml-fetch/(?P<selector>)',   group_views.yaml_fetch,      name='group-yaml-fetch'),
    url(r'^group/yaml-update',                 group_views.yaml_update,     name='group-yaml-update'),

#   url(r'^job/list',                          job_views.list,              name='job-list'),
#   url(r'^job/modify',                        job_views.modify,            name='job-list'),

#    url(r'^settings/preferences',              settings_views.preferences,  name='settings-preferences'),
     url(r'^settings/prepare',                  settings_views.prepare,      name='settings-prepare'),
#    url(r'^settings/log-out',                  settings_views.log_out,      name='settings-log_out'),

    url(r'^user/add',                          user_views.add,              name='user-add'),
    url(r'^user/delete',                       user_views.delete,           name='user-delete'),
    url(r'^user/group-add',                    user_views.group_add,        name='user-group-add'),
    url(r'^user/group-delete',                 user_views.group_delete,     name='user-group-delete'),
    url(r'^user/list',                         user_views.list,             name='user-list'),
    url(r'^user/update',                       user_views.update,           name='user-update'),

#   url(r'^vm/list',                           vm_views.list,               name='vm-list'),
#   url(r'^vm/modify',                         vm_views.modify,             name='vm-list'),

]
