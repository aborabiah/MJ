# courses/templatetags/course_extras.py
from django import template

register = template.Library()

@register.filter
def get_user_rating(answer, user):
    """
    Returns the first rating for an answer by the given user, or None if not found.
    """
    return answer.ratings.filter(user=user).first()