from django.conf.urls import url

from . import views, user_views, cloud_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^user/create', user_views.create, name='create'),
    url(r'^user/delete', user_views.delete, name='delete'),
    url(r'^user/list', user_views.manage, name='manage'),
    url(r'^user/update', user_views.update, name='update'),
    url(r'^status/', cloud_views.status, name='status'),
    url(r'^clouds/', cloud_views.list, name='list'),
    url(r'^cloud/update', cloud_views.add_resources, name='update'),
]
