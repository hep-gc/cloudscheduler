from django.conf.urls import url

from . import glint_views

urlpatterns = [
    url(r'^$', glint_views.list, name='images'),
    url(r'^transfer/$', glint_views.transfer, name='transfer'),
    url(r'^delete/$', glint_views.delete, name='delete'),
#    url(r'^$', image_views.project_details, name='project_details'),
#    url(r'^project_details/(?P<group_name>.+)/$', image_views.project_details, name='project_details'),
#    url(r'^save_images/(?P<group_name>.+)/$', image_views.save_images, name='save_images'),
#    url(r'^download_image/(?P<group_name>.+)/(?P<image_name>.+)/$',\
#        image_views.download_image, name='download_image'),
#    url(r'^download_image/(?P<image_name>.+)/$',\
#        image_views.download_image, name='download_image'),
#    url(r'^upload_image/(?P<group_name>.+)/$', image_views.upload_image, name='upload_image'),
#    url(r'^upload_image/$', image_views.upload_image, name='upload_image')    

]
