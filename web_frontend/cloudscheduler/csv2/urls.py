from django.conf.urls import url
from django.urls import path

from . import accounting_views, \
    alias_views, \
    cloud_views, \
    ec2_views, \
    group_views, \
    job_views, \
    server_views, \
    settings_views, \
    user_views, \
    vm_views

urlpatterns = [

    path('',                                       cloud_views.status),


    path('accounting/apel/',                       accounting_views.apel),

    path('alias/add/',                             alias_views.add),
    path('alias/list/',                            alias_views.alias_list),
    path('alias/update/',                          alias_views.update),

    path('cloud/add/',                             cloud_views.add),
    path('cloud/delete/',                          cloud_views.delete),
    path('cloud/list/',                            cloud_views.cloud_list),
    path('cloud/status/',                          cloud_views.status),
    path('cloud/status/plot',                      cloud_views.request_ts_data),
    path('cloud/update/',                          cloud_views.update),
    path('cloud/metadata-add/',                    cloud_views.metadata_add),
    path('cloud/metadata-collation/',              cloud_views.metadata_collation),
    path('cloud/metadata-delete/',                 cloud_views.metadata_delete),
    path('cloud/metadata-fetch/',                  cloud_views.metadata_fetch),
    path('cloud/metadata-list/',                   cloud_views.metadata_list),
    path('cloud/metadata-new/',                    cloud_views.metadata_new),
    path('cloud/metadata-query/',                  cloud_views.metadata_query),
    path('cloud/metadata-update/',                 cloud_views.metadata_update),

    path('ec2/images/',                            ec2_views.images),
    path('ec2/instance-types/',                    ec2_views.instance_types),

    path('group/add/',                             group_views.add),
    path('group/defaults/',                        group_views.defaults),
    path('group/delete/',                          group_views.delete),
    path('group/list/',                            group_views.group_list),
    path('group/update/',                          group_views.update),
    path('group/metadata-add/',                    group_views.metadata_add),
    path('group/metadata-delete/',                 group_views.metadata_delete),
    path('group/metadata-fetch/',                  group_views.metadata_fetch),
    path('group/metadata-list/',                   group_views.metadata_list),
    path('group/metadata-new/',                    group_views.metadata_new),
    path('group/metadata-query/',                  group_views.metadata_query),
    path('group/metadata-update/',                 group_views.metadata_update),

    path('job/list/',                              job_views.job_list),
##  path('job/modify/',                            job_views.modify),

    path('server/config/',                         server_views.configuration),

##  path('settings/preferences/',                  settings_views.preferences),
    path('settings/prepare/',                      settings_views.prepare),
    path('settings/log-out/',                      settings_views.log_out),

    path('user/add/',                              user_views.add),
    path('user/delete/',                           user_views.delete),
    path('user/list/',                             user_views.user_list),
    path('user/settings/',                         user_views.settings),
    path('user/update/',                           user_views.update),

    path('vm/foreign/',                            vm_views.foreign),
    path('vm/list/',                               vm_views.vm_list),
    path('vm/update/',                             vm_views.update),

]
