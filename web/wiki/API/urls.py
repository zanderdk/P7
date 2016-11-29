from django.conf.urls import url

from . import views

app_name = 'API'
urlpatterns = [
    # ex: /missing/
    url(r'^missing/$', views.full_pool, name='fullPool'),
]