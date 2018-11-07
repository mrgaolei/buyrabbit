"""buyrabbit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from unionbuy import views as ub_views

admin.site.site_header = "买到兔🐰后台管理"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ub_views.home, name='home'),
    path('third_auth/', ub_views.third_auth, name='third_auth'),
    path('auth_callback/', ub_views.auth_back, name='auth_callback'),
    path('unionbuy/', include('unionbuy.urls')),
    path('code_show/<str:code>/', ub_views.code_show, name='code_show'),
    path('unicon_image/', ub_views.unicon_image, name='unicon_image'),
]
