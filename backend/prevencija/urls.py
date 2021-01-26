from django.conf import settings
from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

from prevencija.admin import admin_site


router = DefaultRouter()

urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/docs/', include_docs_urls(title='prevencija API'))
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    