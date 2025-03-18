from django.urls import path
from . import views

urlpatterns = [
    # Main Pages
    path('', views.index, name="home"),
    path('courses/', views.courses, name="courses"),
    path('courses/search/', views.search_courses, name="search-courses"),
    path('courses/enrolled-courses/', views.enrolled_courses, name="enrolled-courses"),
    
    # Topic Related
    path('courses/<slug:topic_slug>/', views.topic_courses, name="topic-courses"),
    
    # Course and Lecture Related
    path('course/<slug:course_slug>/', views.course_detail, name="course-detail"),
    path('course/<slug:course_slug>/learn/', views.lecture, name="lecture"),  # Changed from lecture/ to learn/
    path('course/<slug:course_slug>/learn/<slug:lecture_slug>/', views.lecture_selected, name="lecture-selected"),
    path('course/enroll/<int:course_id>/', views.enroll, name="enroll"),
    
    # Instructor Related
    path('instructor/<str:username>/', views.instructor_profile, name='instructor-profile'),
    
    # Q&A Related
    path('lecture/<int:lecture_id>/ask/', views.ask_question, name='ask_question'),
    path('question/<int:question_id>/answer/', views.add_answer, name='add_answer'),

    # Question Edit & Delete
path('lecture/<int:lecture_id>/rate/', views.rate_lecture, name='rate_lecture'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),

    # Rate an Answer
    path('answer/<int:answer_id>/rate/', views.rate_answer, name='rate_answer'),
    path('answer/<int:answer_id>/edit/', views.edit_answer, name='edit_answer'),
    path('answer/<int:answer_id>/delete/', views.delete_answer, name='delete_answer'),

    path('course/<int:course_id>/rate/', views.rate_course, name='rate_course'),
]
