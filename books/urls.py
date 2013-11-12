from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from books import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<auc_id>\d+)/bid/$', views.bid, name='bid'),
    url(r'^(?P<auc_id>\d+)/close/$', views.close, name='close'),
    url(r'^create/$', views.create, name='create'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^search/$', views.search, name='search'),
    url(r'^(?P<user_id>\w+@\w+(\.\w+)+)/profile/$', views.profile, name='profile'),

)

