from django.conf.urls import url
from . import views

urlpatterns = [ 
    url(r'^$', views.Menu_Page.as_view(), name='Menu_Page'),
]