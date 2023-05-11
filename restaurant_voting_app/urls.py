from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from restaurants import urls as restaurant_urls
from user_profiles import urls as user_profile_urls
from votes import urls as vote_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user_profiles/", include(user_profile_urls)),
    path("restaurants/", include(restaurant_urls)),
    path("votes/", include(vote_urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
