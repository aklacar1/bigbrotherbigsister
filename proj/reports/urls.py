from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('reports/', include('reports.urls')),
    path('admin/', admin.site.urls),
]