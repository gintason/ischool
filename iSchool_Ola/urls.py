from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # ✅ Django Admin - must come early
    path("admin/", admin.site.urls),

    # ✅ API Routes
    path("api/users/", include("users.urls", namespace="users")),
    path("api/school/", include("school.urls")),
    path("api/core/", include("core.urls")),
    path("teacher/", include("teacher_dashboard.urls")),
    path("api/student/dashboard/", include("student_dashboard.urls")),
    path("parent/", include("parent_dashboard.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/", include("test_app.urls")),
    path("api/teachers/", include("teachers.urls", namespace="teachers")),
    path("api/elibrary", include("elibrary.urls")),

    # ✅ React frontend fallback - LAST!
    re_path(r'^((?!admin).)*$', TemplateView.as_view(template_name='index.html')),
]

# ✅ Serve static/media in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
