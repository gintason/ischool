from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.StartTestAPIView.as_view(), name="start-test"),
    path("submit/", views.SubmitTestAPIView.as_view(), name="submit-test"),
    path("tests/", views.list_tests, name="list-tests"),
    path("tests/<int:id>/", views.get_test_detail, name="test-detail"),
    path('api/subjects/', views.SubjectListAPIView.as_view(), name='subject-list'),
    path('api/topics/', views.TopicListAPIView.as_view(), name='topic-list'),
    path('api/test-options/', views.TestFilterOptionsAPIView.as_view(), name='test-options'),
    path("class-levels/", views.list_class_levels, name="list-class-levels"),
    path("subjects/", views.list_subjects, name="list-subjects"),
    path("topics/", views.list_topics, name="list-topics"),
    path("questions/", views.list_questions, name="list-questions"),
   
    # ... your other urls
]

