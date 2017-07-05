from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import BaseFormSet, ModelForm
from core.models import ChildProfile, get_choices

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
		self.fields["child_access"] = forms.ChoiceField(choices=choices, label="Select")

class NewChildForm(ModelForm):
	medproviders = forms.MultipleChoiceField(required=False, label="Healthcare Providers")
	members = forms.MultipleChoiceField(required=False, label="Member Organizations")

	def __init__(self, *args, **kwargs):
		super(NewChildForm, self).__init__(*args, **kwargs)
		self.fields['medproviders'].choices = get_choices("HEAL")
		self.fields['members'].choices = get_choices("MEMB")

	birthdate = forms.DateField(help_text='Required. Format: YYYY-MM-DD',input_formats=['%Y-%m-%d'], required=True)
	class Meta:
		model = ChildProfile
		fields = ['full_name', 'username', 'birthdate', 'address', 'medproviders', 'members']

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
	name = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'placeholder': 'Enter vaccine',}),
							required=False)
	date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Format: YYYY-MM-DD',}),
							input_formats=['%Y-%m-%d'], required=False)

class RequiredFormSet(BaseFormSet):
	def clean(self):
		if any(self.errors):
			return
		names = []
		dates = []
		duplicates = False
		if not self.forms:
			raise forms.ValidationError('You need to submit at least one record.',
										code = 'missing')
		for form in self.forms:
			if form.cleaned_data:
				name = form.cleaned_data['name']
				date = form.cleaned_data['date']

				#check that no two links have the same name, same date is fine
				if name and date:
					if name in names:
						duplicates = True
					names.append(name)
				if duplicates:
					raise forms.ValidationError('Vaccines must have unique names.',
						code='duplicate_names')
				#check that all immunization records have both a name and date
				if name and not date:
					raise forms.ValidationError('All vaccines must have a date.',
						code='missing_date')
				elif date and not name:
					raise forms.ValidationError('You are missing the vaccine name.',
						code='missing_name')
			else:
				raise forms.ValidationError('Please fill in all the fields or remove rows you do not need.',
							code = 'missing_everything')
