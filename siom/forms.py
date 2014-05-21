from django import forms
from django.forms.widgets import PasswordInput
from siom.models import *

class SubmissionForm(forms.ModelForm):
	source_file = forms.FileField()
	
	class Meta:
		model = Submission
		fields = ('task', 'language')

class RegistrationForm(forms.ModelForm):
	password1 = forms.CharField(label='Password', min_length=6, widget=PasswordInput())
	password2 = forms.CharField(label='Repeat password', widget=PasswordInput())

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True
		self.fields['email'].required = True

	def clean(self):
		cleaned_data = super(RegistrationForm, self).clean()

		pass1 = cleaned_data.get('password1')
		pass2 = cleaned_data.get('password2')
		if pass1 and pass2:
			if pass1 != pass2:
				self._errors['password2'] = self.error_class(['Passwords do not match.'])
		return cleaned_data
