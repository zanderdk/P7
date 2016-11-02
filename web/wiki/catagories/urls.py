from django.conf.urls import url

from . import views

app_name = 'catagories'
urlpatterns = [
    # ex: /catagories/
    url(r'^$', views.index, name='index'),
    # ex: /search
    url(r'^search/$', views.search, name='search'),
    # ex: /catagories/biology
    url(r'^(?P<catagory_name>[a-z]+)/$', views.catagory, name='catagory'),
]