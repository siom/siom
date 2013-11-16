from functools import wraps

from django.shortcuts import get_object_or_404
from django.http import Http404

from siom.models import *

def course_view(func):
	@wraps(func)
	def dec(request, course_code, *args, **kwargs):
		course = get_object_or_404(Course, code=course_code)
		in_course = request.user.is_authenticated() and course.users.filter(pk=request.user.id).exists()
		if not course.open and not in_course:
			raise Http404
		request.user.in_course = in_course
		return func(request, course, *args, **kwargs)
	return dec
