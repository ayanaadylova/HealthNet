"""HealthNet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from healthnet import views
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.homepage_redirect, name='homepage_redirect'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^h_admin_homepage/', include('h_admin_homepage.urls')),
    url(r'^doctor_homepage/', include('doctor_homepage.urls')),
    url(r'^patient_homepage/', include('patient_homepage.urls')),
    url(r'^nurse_homepage/', include('nurse_homepage.urls')),
    url(r'^prescriptions/', include('prescription.urls')),
    url(r'^appointments/', include('appointment.urls')),
    url(r'^test_results/', include('test_result.urls')),
    url(r'^message/', include('message.urls'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)