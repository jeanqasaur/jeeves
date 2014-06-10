from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from django.conf import settings

from hipaa import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'conf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', views.profile_view),

    url(r'^register$', views.register_account),

    url(r'^index$', views.index),
    url(r'^$', views.index),
    url(r'^search$', views.search_view),
    url(r'^about$', views.about_view),
    url(r'^users$', views.users_view),
    url(r'^patients/(?P<patient>[0-9]+)/treatments$', views.treatments_view),
    url(r'^patients/(?P<patient>[0-9]+)/diagnoses$', views.diagnoses_view),
    url(r'^patients/(?P<patient>[0-9]+)/info$', views.info_view),
    url(r'^patients/(?P<patient>[0-9]+)/$', views.info_view, name='patient'),
    url(r'^entities/(?P<entity>\w+)/transactions$', views.transactions_view),
    url(r'^entities/(?P<entity>\w+)/associates$', views.associates_view),
    url(r'^entities/(?P<entity>\w+)/directory$', views.directory_view),
    url(r'^entities/(?P<entity>\w+)/$', views.directory_view, name='entity')
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
