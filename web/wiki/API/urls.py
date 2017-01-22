from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from . import views

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

app_name = 'API'
urlpatterns = [
    url(r'^checkpage$', views.check_page, name="check_page"),
    # ex: /links/5/
    url(r'^links/(?P<count>[0-9]+)$', views.partial_pool, name='partialPool'),
    # ex: /links/
    url(r'^links$', views.full_pool, name='fullPool'),
    url(r'^review$', views.link_checked, name='link_checked'),
    url(r'^', include(router.urls)),
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework')),
]