# vim:set ts=4 sw=4 noexpandtab:

from django.shortcuts import render_to_response, get_list_or_404
from siom.models import Course

def course_index(request):
	course_list = get_list_or_404(Course)
	return render_to_response('course_index.html', {'course_list': course_list})
