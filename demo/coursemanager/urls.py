from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from django.conf import settings

from coursemanager import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'coursemanager.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),

    url(r'^register$', views.register_account),

    url(r'^index$', views.index),
    url(r'^courses$', views.courses_view), #TODO
    url(r'^profile$', views.profile_view),
    url(r'^submissions$', views.submissions_view),
    url(r'^$', views.index),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
