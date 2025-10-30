"""
URL configuration for iSchool_Ola project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponseNotFound

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/users/", include("users.urls", namespace="users")),
    path("api/school/", include("school.urls")),
    path("api/core/", include("core.urls")),
    path("teacher/", include("teacher_dashboard.urls")),
    path("api/student/dashboard/", include("student_dashboard.urls")),
    path("parent/", include("parent_dashboard.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/", include("test_app.urls")),
    path("api/teachers/", include("teachers.urls", namespace="teachers")),
    path("api/elibrary/", include("elibrary.urls")),  # ✅ Fixed
]

# ✅ Only serve React index.html for frontend routes (not admin, not API)
urlpatterns += [
    re_path(r'^(?!admin/|api/|teacher/|parent/).*$', TemplateView.as_view(template_name='index.html')),
]


# ✅ Safety: custom 404 fallback for anything unexpected
def not_found_view(request, exception=None):
    return HttpResponseNotFound("404 - Page not found")

handler404 = not_found_view

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

