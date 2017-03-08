from django.conf.urls import url
from . import views

app_name = 'menus'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^heatmap$', views.heatmap_display, name="heatmap_display"),
    url(r'^compare$', views.heatmap_comp_menu, name="heatmap_comp_menu"),
    url(r'^heatmapcompare$', views.heatmap_display_comp, name="heatmap_display_comp"),
    url(r'^info$', views.info, name="info")
]
