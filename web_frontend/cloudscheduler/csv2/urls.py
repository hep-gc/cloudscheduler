from django.conf.urls import url

from . import views, user_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^manage_users/', user_views.manage_users, name='manage_users'),
    url(r'^create_user/', user_views.create_user, name='create_user'),
    url(r'^update_user/', user_views.update_user, name='update_user'),
    url(r'^delete_user/', user_views.delete_user, name='delete_user'),
    url(r'^user_settings/', user_views.user_settings, name='user_settings'),
]
