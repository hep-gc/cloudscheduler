from django.conf.urls import url

from . import glint_views

urlpatterns = [
    url(r'^$', glint_views.list, name='images'),
    url(r'^transfer/$', glint_views.transfer, name='transfer'),
    url(r'^delete/$', glint_views.delete, name='delete'),
    url(r'^retry/$', glint_views.retry, name='retry'),
    url(r'^clear/$', glint_views.clear, name='clear'),
    url(r'^download_image/(?P<group_name>.+)/(?P<image_key>.+)/$',\
        glint_views.download, name='download'),
    url(r'^upload_image/(?P<group_name>.+)/$', glint_views.upload, name='upload'),
    url(r'^image_list/$', glint_views.image_list, name='list_images'),
    url(r'^upload_image/$', glint_views.upload, name='upload')    
#    url(r'^$', image_views.project_details, name='project_details'),
#    url(r'^project_details/(?P<group_name>.+)/$', image_views.project_details, name='project_details'),
#    url(r'^save_images/(?P<group_name>.+)/$', image_views.save_images, name='save_images'),
#    url(r'^download_image/(?P<image_name>.+)/$',\
#        image_views.download_image, name='download_image'),

]
