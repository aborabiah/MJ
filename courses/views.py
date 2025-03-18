from django.shortcuts import render, redirect
from .models import CourseRating, Topic, Course, Lecture, Enroll

from django.contrib import messages
from django.contrib.auth.decorators import login_required # for Access Control
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Question, Answer, AnswerRating

# Create your views here.

def index(request):
    courses = Course.objects.filter(course_is_active='Yes', course_is_featured="Yes")
    context = {
        'courses': courses,
    }
    return render(request, 'courses/index.html', context)


def courses(request):
    courses = Course.objects.filter(course_is_active='Yes')
    context = {
        'courses': courses,
    }
    return render(request, 'courses/courses.html', context)


def topic_courses(request, topic_slug):
    topic = Topic.objects.get(topic_slug=topic_slug)
    courses = Course.objects.filter(course_is_active='Yes', course_topic=topic)
    context = {
        'courses': courses,
        'topic': topic,
    }
    return render(request, 'courses/topic_courses.html', context)


def search_courses(request):
    if request.method == "GET":
        keyword = request.GET.get('q')
        courses = Course.objects.filter(course_is_active='Yes')
        searched_courses = courses.filter(course_title__icontains=keyword) | courses.filter(course_description__icontains=keyword)
        
        context = {
            'courses': searched_courses,
            'keyword': keyword,
        }
        return render(request, 'courses/search_courses.html', context)


from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Course, Lecture, Enroll, LectureView



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg
from .models import Lecture, Question, Answer, LectureRating, LectureView


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lecture, Enroll


@login_required
def lecture(request, course_slug, lecture_slug=None):
    # Get the course
    course = get_object_or_404(Course, course_slug=course_slug)
    
    # Get all lectures for this course
    lectures = course.lecture_set.all().order_by('id')
    
    # Check if user is enrolled
    is_enrolled = Enroll.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, 'Please enroll in the course first.')
        return redirect('course-detail', course_slug=course_slug)
    
    # Get specific lecture or first lecture
    if lecture_slug:
        current_lecture = get_object_or_404(Lecture, lecture_slug=lecture_slug, course=course)
    else:
        current_lecture = lectures.first()
    

    session_key = f'viewed_lecture_{current_lecture.id}'
    if not request.session.get(session_key):
        LectureView.objects.get_or_create(
        lecture=current_lecture,
        user=request.user
    )
    request.session[session_key] = True
    # Get questions for current lecture

    lecture_rating = LectureRating.objects.filter(
        lecture=current_lecture, 
        user=request.user
    ).first()
    
    lecture_rating_data = LectureRating.objects.filter(lecture=current_lecture).aggregate(
        avg_rating=Avg('rating'),
        rating_count=Count('id')
    )
    questions = []
    if current_lecture:
        questions = Question.objects.filter(lecture=current_lecture).order_by('-created_at')
    
    context = {
        'course': course,
        'lectures': lectures,
        'first_lecture': [current_lecture] if current_lecture else [],  # Keep list format for template
        'lecture_selected': current_lecture,  # Add this for direct access
        'questions': questions,
         'lecture_rating': lecture_rating.rating if lecture_rating else 0,
        'lecture_avg_rating': lecture_rating_data['avg_rating'],
        'lecture_rating_count': lecture_rating_data['rating_count'],

    }
    
    return render(request, 'courses/lecture.html', context)


from django.db.models import Prefetch

@login_required
def lecture_selected(request, course_slug, lecture_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    lecture_selected = get_object_or_404(Lecture, lecture_slug=lecture_slug, course=course)
    lectures = course.lecture_set.all().order_by('id')

    # 1) Fetch the user's existing course rating
    user_course_rating_obj = CourseRating.objects.filter(course=course, user=request.user).first()
    user_course_rating = user_course_rating_obj.rating if user_course_rating_obj else 0

    # 2) Aggregate avg and count
    course_rating_data = CourseRating.objects.filter(course=course).aggregate(
        avg_rating=Avg('rating'),
        count_rating=Count('id')
    )


    if not Enroll.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'Please enroll in the course first.')
        return redirect('course-detail', course_slug=course_slug)
    

    session_key = f'viewed_lecture_{lecture_selected.id}'
    if not request.session.get(session_key):
        LectureView.objects.get_or_create(
            lecture=lecture_selected,
            user=request.user
        )
        request.session[session_key] = True
    lectures = course.lecture_set.all().order_by('id')
    
    lecture_rating = LectureRating.objects.filter(
        lecture=lecture_selected, 
        user=request.user
    ).first()
    lecture_rating_data = LectureRating.objects.filter(lecture=lecture_selected).aggregate(
        avg_rating=Avg('rating'),
        rating_count=Count('id')
    )

    
    # Prefetch answers and their ratings for the current user
    questions = Question.objects.filter(lecture=lecture_selected).order_by('-created_at').prefetch_related(
        Prefetch(
            'answers',
            queryset=Answer.objects.prefetch_related(
                Prefetch(
                    'ratings',
                    queryset=AnswerRating.objects.filter(user=request.user),
                    to_attr='user_ratings'
                )
            )
        )
    )

    for question in questions:
        for answer in question.answers.all():
            # Calculate average rating
            agg = answer.ratings.aggregate(avg_rating=Avg('rating'))
            answer.avg_rating = agg['avg_rating'] or 0  # Ensure it's a number
            # Get user's rating from prefetched data
            user_rating = answer.user_ratings[0].rating if answer.user_ratings else 0
            answer.user_rating = user_rating

    context = {
        'course': course,
        'lectures': lectures,
        'lecture_selected': lecture_selected,
        'questions': questions,
        'lecture_rating': lecture_rating.rating if lecture_rating else 0,
        'lecture_avg_rating': lecture_rating_data['avg_rating'],
        'lecture_rating_count': lecture_rating_data['rating_count'],
         'user_course_rating': user_course_rating,
        'course_avg_rating': course_rating_data['avg_rating'],
        'course_rating_count': course_rating_data['count_rating'],



    }
    return render(request, 'courses/lecture.html', context)


@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    if not Enroll.objects.filter(user=request.user, course=course).exists():
        Enroll.objects.create(user=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.course_title}')
    
    # Redirect to the lecture page
    return redirect('lecture', course_slug=course.course_slug)


def course_detail(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    lectures = course.lecture_set.all().order_by('id')
    
    # Check if user is enrolled
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enroll.objects.filter(user=request.user, course=course).exists()
    
    # Calculate total views (if you have a view tracking model)
    total_views = 0  # Replace with actual view count if you have it
    
    context = {
        'course': course,
        'lectures': lectures,
        'enrolled': enrolled,
        'total_views': total_views,
    }
    
    return render(request, 'courses/course_detail.html', context)



from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count

@login_required
def rate_lecture(request, lecture_id):
    """Allows a user to rate a lecture from 1 to 5."""
    if request.method == 'POST':
        lecture = get_object_or_404(Lecture, pk=lecture_id)
        rating_value = request.POST.get('rating')

        # Validate rating
        if rating_value and rating_value.isdigit():
            rating_value = int(rating_value)
            if 1 <= rating_value <= 5:
                LectureRating.objects.update_or_create(
                    user=request.user,
                    lecture=lecture,
                    defaults={'rating': rating_value}
                )
                messages.success(request, f"You rated this lecture {rating_value} stars.")
            else:
                messages.error(request, "Invalid rating value (must be between 1 and 5).")
        else:
            messages.error(request, "Invalid rating input.")

        # Redirect to the same lecture page
        return redirect('lecture-selected',
                        course_slug=lecture.course.course_slug,
                        lecture_slug=lecture.lecture_slug)
    return redirect('home')

@login_required
def rate_item(request, item_type, item_id):
    """
    Universal rating function for answers and questions
    item_type can be 'answer' or 'question'
    """
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        
        # Validate rating
        if not (rating_value and rating_value.isdigit() and 1 <= int(rating_value) <= 5):
            messages.error(request, 'Invalid rating. Please rate between 1 and 5 stars.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        rating_value = int(rating_value)
        
        try:
            if item_type == 'answer':
                # Rate an answer
                answer = get_object_or_404(Answer, id=item_id)
                AnswerRating.objects.update_or_create(
                    answer=answer,
                    user=request.user,
                    defaults={'rating': rating_value}
                )
                messages.success(request, f'You rated the answer {rating_value} out of 5 stars!')
                
                # Redirect back to the lecture page
                return redirect('lecture-selected', 
                                course_slug=answer.question.lecture.course.course_slug, 
                                lecture_slug=answer.question.lecture.lecture_slug)
            
            elif item_type == 'question':
                # Rate a question
                question = get_object_or_404(Question, id=item_id)
                QuestionRating.objects.update_or_create(
                    question=question,
                    user=request.user,
                    defaults={'rating': rating_value}
                )
                messages.success(request, f'You rated the question {rating_value} out of 5 stars!')
                
                # Redirect back to the lecture page
                return redirect('lecture-selected', 
                                course_slug=question.lecture.course.course_slug, 
                                lecture_slug=question.lecture.lecture_slug)
            
            else:
                messages.error(request, 'Invalid rating type.')
                return redirect('home')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('home')
    
    return redirect('home')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Lecture, Question, Answer

@login_required
def lecture_detail(request, slug, lecture_slug=None):
    # Get the course
    course = get_object_or_404(Course, course_slug=slug)
    
    # Get all lectures for this course
    lectures = course.lecture_set.all().order_by('id')
    
    # If lecture_slug is provided, get that specific lecture
    if lecture_slug:
        lecture_selected = get_object_or_404(Lecture, lecture_slug=lecture_slug, course=course)
        first_lecture = [lecture_selected]
    else:
        # If no lecture_slug, get the first lecture
        first_lecture = lectures[:1]
    
    # Get questions for the current lecture
    if first_lecture:
        questions = Question.objects.filter(lecture=first_lecture[0]).order_by('-created_at')
    else:
        questions = []

    context = {
        'course': course,
        'lectures': lectures,
        'first_lecture': first_lecture,
        'questions': questions,
    }
    
    return render(request, 'courses/lecture.html', context)

@login_required
def ask_question(request, lecture_id):
    if request.method == 'POST':
        print("ask_question view called with POST:", request.POST)  # Debug line
        lecture = get_object_or_404(Lecture, id=lecture_id)
        question = Question.objects.create(
            lecture=lecture,
            user=request.user,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            video_timestamp=request.POST.get('video_timestamp') or None
        )
        
        messages.success(request, 'Your question has been posted successfully!')
        return redirect('lecture-selected', 
                course_slug=lecture.course.course_slug,
                lecture_slug=lecture.lecture_slug)

    return redirect('home')

@login_required
def add_answer(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        content = request.POST.get('content')
        
        if content:
            Answer.objects.create(
                question=question,
                user=request.user,
                content=content
            )
        return redirect('lecture-selected', 
                course_slug=question.lecture.course.course_slug, 
                lecture_slug=question.lecture.lecture_slug)


@login_required(login_url='account_login')
def instructor_profile(request, username):
    instructor = get_object_or_404(User, username=username)
    instructor_courses = instructor.courses.all()
    
    # Calculate total students
    total_students = sum(course.enroll_set.count() for course in instructor_courses)
    
    # You can add these if you have a review system
    avg_rating = None  # Add your rating calculation here
    total_reviews = 0  # Add your review count here
    
    context = {
        'instructor': instructor,
        'instructor_courses': instructor_courses,
        'total_students': total_students,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
    }
    return render(request, 'courses/instructor_profile.html', context)


@login_required
def edit_question(request, question_id):
    """Let the question owner edit the question."""
    question = get_object_or_404(Question, id=question_id)

    # Only the question owner can edit
    if question.user != request.user:
        messages.error(request, "You don't have permission to edit this question.")
        return redirect('lecture-selected',
                        course_slug=question.lecture.course.course_slug,
                        lecture_slug=question.lecture.lecture_slug)

    if request.method == 'POST':
        # Update the question
        question.title = request.POST.get('title')
        question.content = request.POST.get('content')
        question.video_timestamp = request.POST.get('video_timestamp') or None
        question.save()
        messages.success(request, "Your question has been updated.")
        return redirect('lecture-selected',
                        course_slug=question.lecture.course.course_slug,
                        lecture_slug=question.lecture.lecture_slug)

    return render(request, 'courses/edit_question.html', {'question': question})


@login_required
def delete_question(request, question_id):
    """Let the question owner delete the question."""
    question = get_object_or_404(Question, id=question_id)

    # Only the question owner can delete
    if question.user != request.user:
        messages.error(request, "You don't have permission to delete this question.")
        return redirect('lecture-selected',
                        course_slug=question.lecture.course.course_slug,
                        lecture_slug=question.lecture.lecture_slug)

    if request.method == 'POST':
        question.delete()
        messages.success(request, "Your question has been deleted.")
        return redirect('lecture-selected',
                        course_slug=question.lecture.course.course_slug,
                        lecture_slug=question.lecture.lecture_slug)

    return render(request, 'courses/delete_question_confirm.html', {'question': question})


@login_required
def rate_answer(request, answer_id):
    if request.method == 'POST':
        answer = get_object_or_404(Answer, id=answer_id)
        rating_value = request.POST.get('rating')
        if rating_value and rating_value.isdigit():
            rating_value = int(rating_value)
            if 1 <= rating_value <= 5:
                AnswerRating.objects.update_or_create(
                    answer=answer,
                    user=request.user,
                    defaults={'rating': rating_value}
                )
                messages.success(request, "Your rating has been updated.")
            else:
                messages.error(request, "Invalid rating (must be 1-5).")
        else:
            messages.error(request, "Invalid rating.")
        return redirect('lecture-selected',
                        course_slug=answer.question.lecture.course.course_slug,
                        lecture_slug=answer.question.lecture.lecture_slug)
    return redirect('home')

@login_required(login_url='account_login')
def enrolled_courses(request):

    try:
        courses = Enroll.objects.filter(user=request.user)
        context = {
            'courses': courses,
        }
        return render(request, 'courses/enrolled_courses.html', context)

    except:
        messages.error(request, "Couldn't Enroll to the course. Please try again later.")
        return redirect(index)
    


@login_required
def edit_answer(request, answer_id):
    """Let the answer owner edit their answer."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Only the answer owner can edit
    if answer.user != request.user:
        messages.error(request, "You don't have permission to edit this answer.")
        return redirect('lecture-selected',
                        course_slug=answer.question.lecture.course.course_slug,
                        lecture_slug=answer.question.lecture.lecture_slug)

    if request.method == 'POST':
        # Update the answer with form data
        answer.content = request.POST.get('content', answer.content)
        answer.save()
        messages.success(request, "Your answer has been updated.")
        return redirect('lecture-selected',
                        course_slug=answer.question.lecture.course.course_slug,
                        lecture_slug=answer.question.lecture.lecture_slug)

    # If GET, render a simple edit form or a modal
    context = {
        'answer': answer,
    }
    return render(request, 'courses/edit_answer.html', context)


@login_required
def delete_answer(request, answer_id):
    """Let the answer owner delete their answer."""
    answer = get_object_or_404(Answer, id=answer_id)

    # Only the answer owner can delete
    if answer.user != request.user:
        messages.error(request, "You don't have permission to delete this answer.")
        return redirect('lecture-selected',
                        course_slug=answer.question.lecture.course.course_slug,
                        lecture_slug=answer.question.lecture.lecture_slug)

    if request.method == 'POST':
        answer.delete()
        messages.success(request, "Your answer has been deleted.")
        return redirect('lecture-selected',
                        course_slug=answer.question.lecture.course.course_slug,
                        lecture_slug=answer.question.lecture.lecture_slug)

    # If GET, show a confirmation page or modal
    context = {
        'answer': answer,
    }
    return render(request, 'courses/delete_answer_confirm.html', context)


@login_required
def rate_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        rating_value = request.POST.get('rating')

        if rating_value and rating_value.isdigit():
            rating_value = int(rating_value)
            if 1 <= rating_value <= 5:
                CourseRating.objects.update_or_create(
                    user=request.user,
                    course=course,
                    defaults={'rating': rating_value}
                )
                messages.success(request, f"You rated the course {rating_value} stars!")
            else:
                messages.error(request, "Rating must be between 1 and 5.")
        else:
            messages.error(request, "Invalid rating input.")

        # If you're using a hidden "next" field:
        next_url = request.POST.get('next', 'home')
        return redirect(next_url)

    return redirect('home')

