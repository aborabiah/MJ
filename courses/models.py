from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Custom Choices
IS_ACTIVE = (
    ('Yes', 'Yes'),
    ('No', 'No')
)

class Topic(models.Model):
    topic_title = models.CharField(max_length=50, verbose_name="Topic Title")
    topic_slug = models.SlugField(max_length=55, verbose_name="Topic Slug")
    topic_description = models.TextField(blank=True, null=True, verbose_name="Topic Description")
    topic_image = models.ImageField(upload_to="topics/", blank=True, null=True)
    topic_is_active = models.CharField(
        choices=IS_ACTIVE,
        default='Yes',
        max_length=10,
        verbose_name="Is Active?"
    )
    topic_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    topic_updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")
    meta_topic_title = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Topic Title (60 Characters Long)")
    meta_topic_keywords = models.TextField(blank=True, null=True, verbose_name="SEO Topic Keywords, Separated by Commas")
    meta_topic_description = models.TextField(blank=True, null=True, verbose_name="SEO Topic Description (160 characters long)")

    def __str__(self):
        return self.topic_title

class Course(models.Model):
    course_title = models.CharField(max_length=200, verbose_name="Course Title")
    course_slug = models.SlugField(verbose_name="Course Slug")
    course_description = models.TextField(blank=True, null=True, verbose_name="Course Description")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', verbose_name="Instructor", null=True, blank=True)
    course_topic = models.ManyToManyField(Topic, verbose_name="Course Topic")
    course_image = models.ImageField(upload_to="courses/", blank=True, null=True)
    course_is_active = models.CharField(choices=IS_ACTIVE, default='Yes', max_length=50, verbose_name="Is Active?")
    course_is_featured = models.CharField(choices=IS_ACTIVE, default='Yes', max_length=50, verbose_name="Is Featured?")
    course_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    course_updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    seo_course_title = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Course Title (60 Characters Long)")
    seo_course_keywords = models.TextField(blank=True, null=True, verbose_name="SEO for Course Keywords, Separated by Commas")
    seo_course_description = models.TextField(blank=True, null=True, verbose_name="SEO Course Description (160 Characters Long)")

    class Meta:
        ordering = ('-course_created_at',)

    def __str__(self):
        return self.course_title

class Lecture(models.Model):
    lecture_title = models.CharField(max_length=255, verbose_name="Lecture Title")
    lecture_slug = models.SlugField(verbose_name="Lecture Slug")
    lecture_description = models.TextField(blank=True, null=True, verbose_name="Lecture Description")
    course = models.ForeignKey(Course, verbose_name="Course", on_delete=models.CASCADE)
    lecture_file = models.FileField(upload_to="files/", blank=True, null=True)
    lecture_video = models.CharField(max_length=150, blank=True, null=True, verbose_name="Video ID")
    lecture_previewable = models.CharField(choices=IS_ACTIVE, default='Yes', max_length=50, verbose_name="Is Previewable?")
    lecture_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    lecture_updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")
    seo_lecture_title = models.CharField(max_length=60, blank=True, null=True, verbose_name="SEO Lecture Title (60 Characters Long)")
    seo_lecture_keyword = models.TextField(blank=True, null=True, verbose_name="SEO Lecture Keywords, Separated by Comma")
    seo_lecture_description = models.TextField(blank=True, null=True, verbose_name="SEO Lecture Description (160 Characters Long)")

    def __str__(self):
        return self.lecture_title

class Enroll(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name="Course", on_delete=models.CASCADE)
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name="Enrolled Date")

    def __str__(self):
        return self.course.course_title

class Question(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_timestamp = models.IntegerField(null=True, blank=True, help_text="Timestamp in seconds")

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer to {self.question.title}"

class LectureRating(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['lecture', 'user']

    def __str__(self):
        return f"{self.user.username} rated {self.lecture.lecture_title}"

class LectureView(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        unique_together = ['lecture', 'user']

    def __str__(self):
        return f"{self.user.username} viewed {self.lecture.lecture_title}"
    
class AnswerRating(models.Model):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('answer', 'user')  # One rating per user per answer

    def __str__(self):
        return f"{self.user.username} rated answer {self.answer.id} with {self.rating}"
    

class CourseRating(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="course_ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'user')  # so each user can only rate a course once

    def __str__(self):
        return f"{self.user.username} rated {self.course.course_title} {self.rating}"