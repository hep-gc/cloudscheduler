from django.conf.urls import url
from django.urls import path

from . import views, cloud_views, group_views, job_views, settings_views, user_views, vm_views

urlpatterns = [

    url(r'^$',                                     cloud_views.status,              name='cloud-status'),


    url(r'^cloud/add',                             cloud_views.add,                 name='cloud-add'),
    url(r'^cloud/delete',                          cloud_views.delete,              name='cloud-delete'),
    url(r'^cloud/list/(?P<selector>)',             cloud_views.list,                name='cloud-list'),
    url(r'^cloud/status',                          cloud_views.status,              name='cloud-status'),
    url(r'^cloud/update',                          cloud_views.update,              name='cloud-update'),
    url(r'^cloud/metadata',                        cloud_views.metadata_list,       name='cloud-metadata-list'),
    url(r'^cloud/meta-add',                    cloud_views.metadata_add,        name='cloud-metadata-add'),
    url(r'^cloud/meta-collation',              cloud_views.metadata_collation,  name='cloud-metadata-collation'),
    url(r'^cloud/meta-delete',                 cloud_views.metadata_delete,     name='cloud-metadata-delete'),
    url(r'^cloud/meta-fetch/(?P<selector>)',   cloud_views.metadata_fetch,      name='cloud-metadata-fetch'),
    url(r'^cloud/meta-update',                 cloud_views.metadata_update,     name='cloud-metadata-update'),

    url(r'^group/add',                             group_views.add,                 name='group-add'),
    url(r'^group/defaults',                        group_views.defaults,            name='group-defaults'),
    url(r'^group/delete',                          group_views.delete,              name='group-delete'),
    url(r'^group/list/(?P<selector>)',             group_views.list,                name='group-list'),
    url(r'^group/update',                          group_views.update,              name='group-update'),
    url(r'^group/metadata-add',                    group_views.metadata_add,        name='group-metadata-add'),
    url(r'^group/metadata-delete',                 group_views.metadata_delete,     name='group-metadata-delete'),
    url(r'^group/metadata-fetch/(?P<selector>)',   group_views.metadata_fetch,      name='group-metadata-fetch'),
    url(r'^group/metadata-list',                   group_views.metadata_list,       name='group-metadata-list'),
    url(r'^group/metadata-update',                 group_views.metadata_update,     name='group-metadata-update'),

    url(r'^job/list',                              job_views.list,                  name='job-list'),
#   url(r'^job/modify',                            job_views.modify,                name='job-list'),

#    url(r'^settings/preferences',                 settings_views.preferences,      name='settings-preferences'),
     url(r'^settings/prepare',                     settings_views.prepare,          name='settings-prepare'),
#    url(r'^settings/log-out',                     settings_views.log_out,          name='settings-log_out'),

    url(r'^user/add',                              user_views.add,                  name='user-add'),
    url(r'^user/delete',                           user_views.delete,               name='user-delete'),
    url(r'^user/list',                             user_views.list,                 name='user-list'),
    url(r'^user/settings',                         user_views.settings,             name='user-settings'),
    url(r'^user/update',                           user_views.update,               name='user-update'),

    path('vm/list/',                               vm_views.list),
    path('vm/list/<path:selector>/',               vm_views.list),
    path('vm/update/',                             vm_views.update),

]
