from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bookmania.views.home', name='home'),
    # url(r'^bookmania/', include('bookmania.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^books/', include('books.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/ashkan/Desktop/bookmania/media',}),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)
