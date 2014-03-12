from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from django.conf import settings

from conf import views

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
    url(r'^submit$', views.submit_view),
    url(r'^paper$', views.paper_view),
    url(r'^submit_review$', views.submit_review_view),
    url(r'^submit_comment$', views.submit_comment_view),
    url(r'^assign_reviews$', views.assign_reviews_view),
    url(r'^search$', views.search_view),
    url(r'^about$', views.about_view),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
