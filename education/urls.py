from django.urls import path

from . import views


app_name = "education"


urlpatterns = [

    # ============================================================
    # GENERAL
    # ============================================================

    path(
        "",
        views.education_home,
        name="home"
    ),

    path(
        "login/",
        views.education_login,
        name="login"
    ),

    path(
        "google/start/",
        views.education_google_start,
        name="google_start"
    ),

    path(
        "google/complete/",
        views.education_google_complete,
        name="google_complete"
    ),


    path(
        "register/",
        views.education_register,
        name="register"
    ),

    path(
        "logout/",
        views.education_logout,
        name="logout"
    ),


    # ============================================================
    # STUDENT - DASHBOARD
    # ============================================================

    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard"
    ),

    path(
        "student/ask-doubt/",
        views.ask_doubt,
        name="ask_doubt"
    ),

    path(
        "student/ask-doubt/api/",
        views.ask_doubt_api,
        name="ask_doubt_api"
    ),

    path(
        "student/ask-doubt/tts/",
        views.text_to_speech,
        name="text_to_speech"
    ),


    # ============================================================
    # STUDENT - TESTS
    # ============================================================

    path(
        "student/tests/",
        views.student_tests,
        name="student_tests"
    ),

    path(
        "student/tests/<int:test_id>/start/",
        views.start_test,
        name="start_test"
    ),

    path(
        "student/tests/<int:test_id>/delete/",
        views.delete_student_test,
        name="delete_student_test"
    ),

    path(
        "student/tests/<int:test_id>/anti-cheat/",
        views.test_anti_cheat_event,
        name="test_anti_cheat_event"
    ),

    path(
        "student/tests/<int:test_id>/proctoring-status/",
        views.test_proctoring_status,
        name="test_proctoring_status"
    ),

    path(
        "student/monitor-heartbeat/<int:attempt_id>/",
        views.student_monitor_heartbeat,
        name="student_monitor_heartbeat"
    ),

    path(
        "student/tests/<int:test_id>/submit/",
        views.submit_test,
        name="submit_test"
    ),

    path(
        "student/test-result/<int:result_id>/",
        views.test_result,
        name="test_result"
    ),


    # ============================================================
    # STUDENT - WEBRTC LIVE CAMERA
    # ============================================================

    path(
        "student/webrtc/offer/<int:attempt_id>/",
        views.student_webrtc_offer,
        name="student_webrtc_offer"
    ),

    path(
        "student/webrtc/answer/<int:attempt_id>/",
        views.student_webrtc_answer,
        name="student_webrtc_answer"
    ),


    # ============================================================
    # STUDENT - LEARNING
    # ============================================================

    path(
        "student/classes/",
        views.student_classes,
        name="student_classes"
    ),

    path(
        "student/class/<int:class_id>/subjects/",
        views.student_subjects,
        name="student_subjects"
    ),

    path(
        "student/subject/<int:subject_id>/chapters/",
        views.student_chapters,
        name="student_chapters"
    ),

    path(
        "student/chapter/<int:chapter_id>/",
        views.chapter_detail,
        name="chapter_detail"
    ),

    path(
        "learn/<int:chapter_id>/",
        views.learn,
        name="learn"
    ),

    path(
        "student/lesson/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail"
    ),

    path(
        "student/lesson/<int:lesson_id>/delete/",
        views.admin_delete_lesson,
        name="admin_delete_lesson"
    ),


    # ============================================================
    # TEACHER - DASHBOARD
    # ============================================================

    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard"
    ),

    path(
        "teacher/create-lesson/",
        views.teacher_create_lesson,
        name="teacher_create_lesson"
    ),

    path(
        "teacher/delete-lesson/<int:lesson_id>/",
        views.teacher_delete_lesson,
        name="teacher_delete_lesson"
    ),

    path(
        "teacher/create-test/",
        views.teacher_create_test,
        name="teacher_create_test"
    ),

    path(
        "teacher/results/",
        views.teacher_results,
        name="teacher_results"
    ),

    path(
        "teacher/results/<int:result_id>/",
        views.teacher_result_detail,
        name="teacher_result_detail"
    ),


    # ============================================================
    # TEACHER - LIVE EXAM MONITORING
    # ============================================================

    path(
        "teacher/live-monitor/",
        views.teacher_live_monitor,
        name="teacher_live_monitor"
    ),

    path(
        "teacher/live-monitor/data/",
        views.teacher_live_monitor_data,
        name="teacher_live_monitor_data"
    ),

    path(
        "teacher/terminate-test/<int:attempt_id>/",
        views.teacher_terminate_test,
        name="teacher_terminate_test"
    ),


    # ============================================================
    # TEACHER - WEBRTC LIVE CAMERA
    # ============================================================

    path(
        "teacher/webrtc/offer/<int:attempt_id>/",
        views.teacher_webrtc_offer,
        name="teacher_webrtc_offer"
    ),

    path(
        "teacher/webrtc/answer/<int:attempt_id>/",
        views.teacher_webrtc_answer,
        name="teacher_webrtc_answer"
    ),

    # ============================================================
    # STUDENT - AI EXAM PREPARATION
    # ============================================================

    path(
        "student/exam-preparation/",
        views.student_exam_strategy,
        name="student_exam_strategy"
    ),

    path(
    "student/progress/",
    views.student_progress,
    name="student_progress"
    ),
]

