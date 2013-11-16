from django import forms
from siom.models import *

class SubmissionForm(forms.ModelForm):
	source_file = forms.FileField()
	
	class Meta:
		model = Submission
		fields = ('task', 'language')
