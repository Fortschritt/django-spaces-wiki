from django.urls import re_path

from . import views

app_name="wiki"
urlpatterns = [
    re_path('^notes/(?P<path>.+/|)$', views.SpaceArticleView.as_view(), name='get'),
    re_path('^notes/(?P<path>.+/|)_create/$', views.SpaceCreate.as_view(), name='create'),
    re_path('^notes/(?P<path>.+/|)_deleted/$', views.SpaceDeleted.as_view(), name='deleted'),
]
