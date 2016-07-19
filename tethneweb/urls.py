"""django_tethne URL Configuration

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
from rest_framework import routers
from rest_framework.authtoken import views as auth_views
from tethneweb import views

router = routers.DefaultRouter()
router.register(r'corpus', views.CorpusViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'paper_instance', views.PaperInstanceViewSet)
router.register(r'author_instance', views.AuthorInstanceViewSet)
router.register(r'institution_instance', views.InstitutionInstanceViewSet)
router.register(r'affiliation_instance', views.AffiliationInstanceViewSet)
router.register(r'instance_metadatum', views.InstanceMetadatumViewSet)
router.register(r'instance_identifier', views.InstanceIdentifierViewSet)


urlpatterns = [
    url(r'^rest/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-token-auth/', auth_views.obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^$', views.home, name="home"),
]
