from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^manage_users/', views.manage_users, name='manage_users'),
    url(r'^create_user/', views.create_user, name='create_user'),
    url(r'^update_user/', views.update_user, name='update_user'),
]
