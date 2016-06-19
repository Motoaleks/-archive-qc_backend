"""city_backend_v2 URL Configuration

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

from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from api.views import UserViewSet, QuestViewSet, GameViewSet, FileViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'quests', QuestViewSet)
router.register(r'games', GameViewSet)
router.register(r'files', FileViewSet)


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^v1/', include(router.urls)),
    url(r'^v1/auth/login/', 'rest_framework_jwt.views.obtain_jwt_token'),
]
