from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views as conf_views

urlpatterns = [
    url(r'^accounts/login/$', auth_views.login),
    url(r'^accounts/logout/$', auth_views.logout),
    url(r'^accounts/profile/$', conf_views.profile_view),

    url(r'^register$', conf_views.register_account),

    url(r'^index$', conf_views.papers_view),
    url(r'^$', conf_views.papers_view),
    url(r'^submit$', conf_views.submit_view),
    url(r'^papers$', conf_views.papers_view),
    url(r'^paper$', conf_views.paper_view),
    url(r'^submit_review$', conf_views.submit_review_view),
    url(r'^submit_comment$', conf_views.submit_comment_view),
    url(r'^assign_reviews$', conf_views.assign_reviews_view),
    url(r'^search$', conf_views.search_view),
    url(r'^about$', conf_views.about_view),
    url(r'^users$', conf_views.users_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
