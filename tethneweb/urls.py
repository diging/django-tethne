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
    url('', include('social_django.urls', namespace='social')),
    url(r'^rest/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-token-auth/', auth_views.obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^check_unique/', views.check_unique, name='check-unique'),
    url(r'^$', views.home, name="home"),
]
