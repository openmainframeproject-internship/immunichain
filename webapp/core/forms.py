from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import BaseFormSet, ModelForm
from core.models import ChildProfile, get_choices

class SignUpForm(UserCreationForm):
	ROLE_CHOICES = (('','-----------'),('GRDN', 'Guardian'), ('MEMB', 'Member Organization'), ('HEAL', 'Healthcare Provider'))
	role = 	forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), help_text="Select account type", choices=ROLE_CHOICES) 
	full_name = forms.CharField(label="Name", widget=forms.TextInput(attrs={'class':'form-control'}),help_text="Your full name or the name of the organization",)

	class Meta:
		model= User 
		fields=('full_name','username','password1','password2','role')


class SignUpForm_reassign(UserCreationForm):
	class Meta:
		model= User 
		fields=('username','password1','password2')

class NameForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(NameForm, self).__init__(*args, **kwargs)
		self.fields["child_access"] = forms.ChoiceField(choices=choices, label="Select")

class NewChildForm(ModelForm):
	medproviders = forms.MultipleChoiceField(required=False, label="Healthcare Providers")
	members = forms.MultipleChoiceField(required=False, label="Member Organizations",)

	def __init__(self, *args, **kwargs):
		super(NewChildForm, self).__init__(*args, **kwargs)
		self.fields['medproviders'].choices = get_choices("HEAL")
		self.fields['members'].choices = get_choices("MEMB")

	birthdate = forms.DateField(input_formats=['%Y-%m-%d'])
	class Meta:
		model = ChildProfile
		fields = ['full_name', 'username', 'birthdate', 'address', 'medproviders', 'members']

class UpdateForm(forms.Form):
	def __init__(self, children, *args, **kwargs):
		super(UpdateForm, self).__init__(*args, **kwargs)
		self.fields["child"] = forms.ChoiceField(choices=children, label="Child")
	new_name = forms.CharField(required=False)
	new_address = forms.CharField(required=False)
	def clean(self):
		cleaned_data = super(UpdateForm, self).clean()
		if not (cleaned_data.get("new_name") or cleaned_data.get("new_address")):
			raise forms.ValidationError("Either a new name or new address is required.")
		return cleaned_data
