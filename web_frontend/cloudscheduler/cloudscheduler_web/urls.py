"""cloudscheduler_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import include
from django.urls import re_path
from django.contrib import admin

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('csv2.urls')),
    re_path(r'^images/', include('glintwebui.image_urls')),
    re_path(r'^keypairs/', include('glintwebui.keypair_urls')),
]

if settings.CSV2_CONFIG.categories["web_frontend"]["enable_profiling"]:
    urlpatterns += [re_path(r'^silk/', include('silk.urls', namespace='silk'))]

