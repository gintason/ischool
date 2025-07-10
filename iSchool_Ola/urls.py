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

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ Use a distinct prefix for users app
    path("api/users/", include("users.urls", namespace="users")),
    path("api/school/", include("school.urls")),  # School-related endpoints
    path("api/core/", include("core.urls")),      # Core endpoints
    path('teacher/', include('teacher_dashboard.urls')),
    path("api/student/dashboard/", include("student_dashboard.urls")),
    path('parent/', include('parent_dashboard.urls')),
    path('api/payments/', include('payments.urls')),  # ⬅️ Add this line
    path('api/', include('test_app.urls')),
    path("api/teachers/", include("teachers.urls", namespace="teachers")),
    path("api/elibrary", include('elibrary.urls')),

     # React frontend fallback
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),

    
] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
