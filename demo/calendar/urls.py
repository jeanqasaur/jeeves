from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from django.conf import settings

from calendar import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jelf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', views.profile_view),

    url(r'^register$', views.register_account),

    url(r'^index$', views.index),
    url(r'^event$', views.event),
    url(r'^$', views.index),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
