from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import BaseFormSet

class SignUpForm(UserCreationForm):
	ROLE_CHOICES = (('','-----------'),('GRDN', 'Guardian'), ('MEMB', 'Member Organization'), ('HEAL', 'Healthcare Provider'))
	role = forms.ChoiceField(help_text="Select account type", choices=ROLE_CHOICES, required=True)
	full_name = forms.CharField(help_text="Please enter your full name or the name of the organization.",required=True)

	class Meta:
		model= User 
		fields=('full_name','username','password1','password2','role')

class NameForm(forms.Form):
	def __init__(self, choices, *args, **kwargs):
		super(NameForm, self).__init__(*args, **kwargs)
		self.fields["child_access"] = forms.ChoiceField(choices=choices, label="Select child")

class NewChildForm(forms.Form):
	def __init__(self, medproviders, members, *args, **kwargs):
		super(NewChildForm, self).__init__(*args, **kwargs)
		self.fields["medproviders"] = forms.MultipleChoiceField(choices=medproviders, required=False, label="Healthcare Providers")
		self.fields["members"] = forms.MultipleChoiceField(choices=members, required=False, label="Member Organizations")

	full_name = forms.CharField(help_text="Please enter your child's full name.", required=True)
	username = forms.CharField(
		help_text="Required. 150 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters.", 
		required=True)
	birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD',input_formats=['%Y-%m-%d'], required=True)
	address = forms.CharField(help_text="Please enter your child's address", required=True)

class UpdateForm(forms.Form):
	def __init__(self, children, *args, **kwargs):
		super(UpdateForm, self).__init__(*args, **kwargs)
		self.fields["child"] = forms.ChoiceField(choices=children, label="Child")

	new_name = forms.CharField(help_text="Please enter your child's full name.", required=False)
	new_address = forms.CharField(help_text="Please enter your child's new address.", required=False)

	def clean(self):
		cleaned_data = super(UpdateForm, self).clean()
		if not (cleaned_data.get("new_name") or cleaned_data.get("new_address")):
			raise forms.ValidationError("Either a new name or new address is required.")
		return cleaned_data

class Immunization(forms.Form):
	name = forms.CharField(help_text="Please enter the vaccine name.", required=True)
	date = forms.DateField(help_text='Format: YYYY-MM-DD',input_formats=['%Y-%m-%d'],required=True)

class RequiredFormSet(BaseFormSet):
	def __init__(self, *args, **kwargs):
		super(RequiredFormSet, self).__init__(*args, **kwargs)
		self.forms[0].empty_permitted = False

	def clean(self):
		if any(self.errors):
			return
		names = []
		for form in self.forms:
			if form.cleaned_data:
				name = form.cleaned_data['name']
				if name in names:
					raise forms.ValidationError("Vaccines must have distinct names.")
				names.append(name)
