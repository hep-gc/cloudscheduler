from django.conf.urls import url
from django.urls import path

from . import cloud_views

urlpatterns = [
    path('cloud/status/plot',                      cloud_views.request_public_ts_data),
]
