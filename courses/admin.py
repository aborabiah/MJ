from django.contrib import admin
from django.db.models import Avg, Count
from .models import (
    Topic, Course, Lecture, Enroll,
    Question, Answer, LectureView, LectureRating, CourseRating
)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('topic_title', 'topic_slug', 'topic_is_active')
    list_editable = ('topic_slug', 'topic_is_active')
    list_filter = ('topic_is_active', 'topic_created_at')
    list_per_page = 10
    search_fields = ('topic_title', 'topic_description')
    prepopulated_fields = {"topic_slug": ("topic_title",)}

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_title', 'course_slug', 'course_is_active', 'get_rating_count', 'get_average_rating')
    list_editable = ('course_slug', 'course_is_active')
    list_filter = ('course_is_active', 'course_created_at')
    list_per_page = 10
    search_fields = ('course_title', 'course_description')
    prepopulated_fields = {"course_slug": ("course_title",)}

    def get_rating_count(self, obj):
        return obj.course_ratings.count()
    get_rating_count.short_description = 'Number of Ratings'

    def get_average_rating(self, obj):
        avg = obj.course_ratings.aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            return round(avg, 2)
        return 0
    get_average_rating.short_description = 'Average Rating'

class LectureAdmin(admin.ModelAdmin):
    list_display = ('lecture_title', 'course', 'lecture_slug', 'lecture_previewable', 'get_rating_count', 'get_average_rating')
    list_editable = ('lecture_slug', 'lecture_previewable')
    list_filter = ('lecture_previewable', 'lecture_created_at')
    list_per_page = 10
    search_fields = ('lecture_title', 'lecture_description')
    prepopulated_fields = {"lecture_slug": ("lecture_title",)}

    def get_rating_count(self, obj):
        return obj.ratings.count()
    get_rating_count.short_description = 'Number of Ratings'

    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            return round(avg, 2)
        return 0
    get_average_rating.short_description = 'Average Rating'

class EnrollAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_date')
    list_filter = ('user', 'course', 'enrolled_date')
    list_per_page = 10
    search_fields = ('user', 'course', 'enrolled_date')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'lecture', 'user', 'created_at')
    list_filter = ('lecture', 'created_at')
    search_fields = ('title', 'content')
    inlines = [AnswerInline]

class LectureViewAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'user', 'viewed_at')
    list_filter = ('lecture', 'viewed_at')
    search_fields = ('lecture__lecture_title', 'user__username')

class LectureRatingAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('lecture__lecture_title', 'user__username')

class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('course__course_title', 'user__username')

# Register your models here
admin.site.register(Course, CourseAdmin)
admin.site.register(Lecture, LectureAdmin)
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(LectureView, LectureViewAdmin)
admin.site.register(LectureRating, LectureRatingAdmin)
admin.site.register(CourseRating, CourseRatingAdmin)
admin.site.register(Topic, TopicAdmin)
