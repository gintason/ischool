from .views import ELibraryChapterListView
from django.urls import path

urlpatterns = [
    path('chapters/', ELibraryChapterListView.as_view(), name='elibrary-chapters'),
]