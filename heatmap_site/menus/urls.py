from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^heatmap$', views.heatmap_display, name="heatmap_display"),
    url(r'^compare$', views.heatmap_display_comp, name="heatmap_display_comp")
]
