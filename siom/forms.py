# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4:

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
from siom.models import *

class SubmissionForm(forms.ModelForm):
    source_file = forms.FileField()

    class Meta:
        model = Submission
        fields = ('language',)

class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
