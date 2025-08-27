from django.urls import re_path

from . import glint_views

urlpatterns = [
    re_path(r'^$', glint_views.list, name='images'),
    re_path(r'^transfer/$', glint_views.transfer, name='transfer'),
    re_path(r'^delete/$', glint_views.delete, name='delete'),
    re_path(r'^retry/$', glint_views.retry, name='retry'),
    re_path(r'^clear/$', glint_views.clear, name='clear'),
    re_path(r'^download_image/(?P<group_name>.+)/(?P<image_key>.+)/$',\
        glint_views.download, name='download'),
    re_path(r'^upload_image/(?P<group_name>.+)/$', glint_views.upload, name='upload'),
    re_path(r'^image_list/$', glint_views.image_list, name='list_images'),
    re_path(r'^upload_image/$', glint_views.upload, name='upload')    
#    url(r'^$', image_views.project_details, name='project_details'),
#    url(r'^project_details/(?P<group_name>.+)/$', image_views.project_details, name='project_details'),
#    url(r'^save_images/(?P<group_name>.+)/$', image_views.save_images, name='save_images'),
#    url(r'^download_image/(?P<image_name>.+)/$',\
#        image_views.download_image, name='download_image'),

]
