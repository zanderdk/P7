from django.conf.urls import url

from . import views

app_name = 'catagories'
urlpatterns = [
    # ex: /catagories/
    url(r'^$', views.index, name='index'),
]