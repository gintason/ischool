# ischool_live/teachers/urls.py

from django.urls import path
from .views import ( TeacherApplicationView, 
                    HireTeacherView, 
                    StartLiveClassView,
                    UpcomingGroupedClassesView,
                    DailyTimetableView, 
                    TeacherApplicationListView, 
                    UpdateTeacherStatusView, 
                    TeacherApplicationStatusView, 
                    TeacherLoginView,
                    LessonPlanListView,
                    SetLessonPlanView,
                    AssignChapterToSessionView,
                    LatestAttendanceLogView,
                    WeeklySummaryView,
                    MatchedStudentsView, TeacherInterviewView,
                    OleClassLevelListView, OleSubjectListView, 
                    StudentUpcomingLessonsView, LessonHistoryView, TeacherPayslipDownloadView, 
                    LiveClassSessionDetailView, MarkLessonCompletedView, ToggleLessonChatView, LeaveLessonView
                    )

app_name = "teachers"

urlpatterns = [
    
    path("apply/", TeacherApplicationView.as_view(), name="apply"),
    path('admin/hire-teacher/<int:application_id>/', HireTeacherView.as_view(), name='hire_teacher'),
    path('admin/applications/', TeacherApplicationListView.as_view(), name='list_applications'),
    path('admin/update-status/<int:application_id>/', UpdateTeacherStatusView.as_view(), name='update_status'),
    path('application-status/', TeacherApplicationStatusView.as_view(), name='application_status'),
    path('login/', TeacherLoginView.as_view(), name='teacher_login'),
    path('daily-timetable/', DailyTimetableView.as_view(), name='teacher-daily-timetable'),
    path('dashboard/upcoming-classes/', UpcomingGroupedClassesView.as_view(), name='upcoming_grouped_classes'),
    path('dashboard/start-class/<int:schedule_id>/', StartLiveClassView.as_view(), name='start_live_class'),
    path('lesson-plans/', LessonPlanListView.as_view(), name='lesson-plans'),
    path('set-lesson-plan/<int:session_id>/', SetLessonPlanView.as_view(), name='set-lesson-plan'),
    path('assign-chapter/<int:session_id>/', AssignChapterToSessionView.as_view(), name='assign-chapter'),
    path('dashboard/latest-attendance/', LatestAttendanceLogView.as_view(), name='latest-attendance'),
    path('dashboard/weekly-summary/', WeeklySummaryView.as_view(), name='weekly-summary'),
    path('matched-students/<int:schedule_id>/', MatchedStudentsView.as_view(), name='matched-students'),
    path('admin/interview/<int:application_id>/', TeacherInterviewView.as_view(), name='teacher-interview'),
    path("class-levels/", OleClassLevelListView.as_view(), name="ole-class-levels"),
    path("subjects/", OleSubjectListView.as_view(), name="ole-subjects"),
    path("ole-student/upcoming-lessons/", StudentUpcomingLessonsView.as_view(), name="upcoming-lessons"),
    path('lesson-history/', LessonHistoryView.as_view(), name='lesson-history'),
    path('download-payslip/<int:year>/<int:month>/', TeacherPayslipDownloadView.as_view(), name='download_payslip'),
    path('dashboard/session-detail/<int:pk>/', LiveClassSessionDetailView.as_view(), name='session_detail'),
    path('lesson/<int:lesson_id>/complete/', MarkLessonCompletedView.as_view(), name='mark_lesson_complete'),
    path('lesson/<int:lesson_id>/toggle-chat/', ToggleLessonChatView.as_view(), name='toggle_chat'),
    path('lesson/<int:lesson_id>/leave/', LeaveLessonView.as_view(), name='leave_lesson'),
   
]

