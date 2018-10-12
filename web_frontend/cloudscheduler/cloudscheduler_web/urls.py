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
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('csv2.urls')),
]

#if config.enable_profiling:
#    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]

if settings.CSV2_CONFIG.enable_glint:
    urlpatterns = [
        url(r'^images/', include('glintwebui.image_urls')),
        url(r'^keypairs/', include('glintwebui.keypair_urls')),
    ] + urlpatterns

