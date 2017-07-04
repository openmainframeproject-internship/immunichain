# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.forms.formsets import formset_factory
from core.forms import SignUpForm, NameForm, NewChildForm, UpdateForm, Immunization, RequiredFormSet
from django.template.defaulttags import register
import json
import requests

SUCCESS_CALL = 200
guardian_prefix = 'resource:ibm.wsc.immunichain.Guardian#'
mprovider_prefix = 'resource:ibm.wsc.immunichain.MedProvider#'
memberorg_prefix = 'resource:ibm.wsc.immunichain.Member#'

# Create your views here.
@login_required
def home(request):
	user_role = request.user.profile.role
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	if user_role == 'GRDN':
		r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
	elif user_role == "MEMB":
		r = list(filter(lambda d: (memberorg_prefix+request.user.username) in d['members'], h ))
	else:
		r = list(filter(lambda d: (mprovider_prefix+request.user.username) in d['medproviders'], h ))
	return render(request, 'home.html', {'r':r})

@login_required
def viewchild(request):
	user_role = request.user.profile.role
	username = request.user.username
	r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	CHILD_CHOICES = [('','-----------')]
	for child in r.json():
		if user_role == 'GRDN':
			if ("resource:ibm.wsc.immunichain.Guardian#"+username) == child['guardian']:
				CHILD_CHOICES.append((child['cid'],child['name']))
		elif user_role == 'MEMB':
			if (memberorg_prefix+username) in child['members']:
				CHILD_CHOICES.append((child['cid'],child['name']))
		else:
			if (mprovider_prefix+username) in child['medproviders']:
				CHILD_CHOICES.append((child['cid'],child['name']))

	if request.method == 'POST':
		form = NameForm(CHILD_CHOICES, request.POST)
		if form.is_valid():
			cid = form.cleaned_data.get('child_access')
			h = (item for item in r.json() if item["cid"] == cid).next()
			userdict = {}
			providers = h["medproviders"]
			members = h["members"]
			vaccines = h["immunizations"]
			guardian = h["guardian"]
			for provider in providers:
				if provider not in userdict.keys():
					garbage,lookup=provider.split("#",1)
					r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.MedProvider/"+lookup)
					r = r.json()
					userdict[provider] = r["name"]
			for member in members:
				if member not in userdict.keys():
					garbage,lookup=member.split("#",1)
					r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Member/"+lookup)
					r = r.json()
					userdict[member] = r["name"]
			if guardian not in userdict.keys():
				garbage,lookup=guardian.split("#",1)
				r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Guardian/"+lookup)
				r = r.json()
				userdict[guardian] = r["name"]
			for record in vaccines:
				if record['provider'] not in userdict.keys() and record['provider']!='default':
					r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.MedProvider/"+record['provider'])
					r = r.json()
					userdict[record['provider']] = r["name"]

			return render(request, 'viewchild.html', {'h':h, 'form': form, "userdict": userdict})
	else:
		form = NameForm(CHILD_CHOICES)

	return render(request, 'viewchild.html', {'form': form})

@login_required
def auth_member_select(request):
	assert request.user.profile.role == 'GRDN'
	children = []
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
	for child in r:
		children.append((child['cid'], child['name']))
	if request.method == 'POST':
		form = NameForm(children, request.POST)
		if form.is_valid():
			cid = form.cleaned_data.get('child_access')
			chosen = (item for item in r if item["cid"] == cid).next()
			child_name = chosen["name"]			
			r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Member")
			avail_members = [(d['name'], d['memid']) for d in r.json()]
			renderdict = {'cid': cid, 'child_name': child_name, 'avail_members': avail_members}
			return render(request, 'auth_member_select.html', renderdict)
	else:
		form = NameForm(children)
	return render(request, 'auth_member_select.html', {'form':form})

@login_required
def auth_member_submit(request):
	assert request.user.profile.role == 'GRDN'
	memid = request.POST['newmember']
	cid = request.POST["child"]
	r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform/"+cid)
	r = r.json()
	existing_members = r["members"]

	if (memberorg_prefix+memid) not in existing_members:
		gid = request.user.username
		d = {"guardian": gid,"member": memid, "childform": cid}
		make = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.authMember", data=d)
		assert make.status_code == SUCCESS_CALL

	return render(request, 'auth_member_submit.html')

@login_required
def assignmed_select(request):
	assert request.user.profile.role == 'GRDN'
	children = []
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
	for child in r:
		children.append((child['cid'], child['name']))
	if request.method == 'POST':
		form = NameForm(children, request.POST)
		if form.is_valid():
			cid = form.cleaned_data.get('child_access')
			chosen = (item for item in r if item["cid"] == cid).next()
			child_name = chosen["name"]			
			r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.MedProvider")
			avail_medproviders = [(d['name'], d['medid']) for d in r.json()]
			renderdict = {'cid': cid, 'child_name': child_name, 'avail_medproviders': avail_medproviders}
			return render(request, 'assignmed_select.html', renderdict)
	else:
		form = NameForm(children)
	return render(request, 'assignmed_select.html', {'form':form})

@login_required
def assignmed_submit(request):
	assert request.user.profile.role == 'GRDN'
	medid = request.POST['newmed']
	cid = request.POST["child"]
	r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform/"+cid)
	r = r.json()
	existing_medproviders = r["medproviders"]

	if (mprovider_prefix+medid) not in existing_medproviders:
		gid = request.user.username
		d = {"guardian": gid,"medprovider": medid, "childform": cid}
		make = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.assignMedProvider", data=d)
		assert make.status_code == SUCCESS_CALL

	return render(request, 'assignmed_submit.html')

@login_required
def deauth_member_select(request):
	assert request.user.profile.role == 'GRDN'
	children = []
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
	for child in r:
		children.append((child['cid'], child['name']))
	if request.method == 'POST':
		form = NameForm(children, request.POST)
		if form.is_valid():
			cid = form.cleaned_data.get('child_access')
			chosen = (item for item in r if item["cid"] == cid).next()
			child_name = chosen["name"]
			current_members = chosen["members"]
			cleaned = [s.replace(memberorg_prefix, '') for s in current_members]
			avail_members=[]
			for memberid in cleaned:
				user = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Member/"+memberid)
				user = user.json()
				avail_members.append((user['name'], memberid))
			renderdict = {'cid': cid, 'child_name': child_name, 'avail_members': avail_members}
			return render(request, 'deauth_member_select.html', renderdict)
	else:
		form = NameForm(children)
	return render(request, 'deauth_member_select.html', {'form':form})

@login_required
def deauth_member_submit(request):
	assert request.user.profile.role == 'GRDN'
	memid = request.POST['newmember']
	cid = request.POST["child"]
	r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform/"+cid)
	r = r.json()
	existing_members = r["members"]

	if (memberorg_prefix+memid) in existing_members:
		gid = request.user.username
		d = {"guardian": gid,"member": memid, "childform": cid}
		make = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.removeMemberAuth", data=d)
		assert make.status_code == SUCCESS_CALL

	return render(request, 'deauth_member_submit.html')

@login_required
def update(request):
	assert request.user.profile.role == 'GRDN'
	children = [('','-----------')]
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
	for child in r:
		children.append((child['cid'], child['name']))
	if request.method == 'POST':
		form = UpdateForm(children, request.POST)
		if form.is_valid():
			cid = form.cleaned_data.get('child')
			name = form.cleaned_data.get('new_name')
			address = form.cleaned_data.get('new_address')
			if not name:
				d = {'childform': cid, 'address':address}
			elif not address:
				d = {'childform': cid, 'name':name }
			else:
				d = {'childform': cid, 'address':address, 'name':name }
			r = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.updateChildForm", data=d)
			if r.status_code == SUCCESS_CALL:
				return redirect('success')
			else:
				return redirect('failure')
	else:
		form = UpdateForm(children)

	return render(request, 'update.html', {'form':form})

@login_required
def addImmunizations(request):
	assert request.user.profile.role == 'HEAL'
	children = [('','-----------')]
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	r = list(filter(lambda d: (mprovider_prefix+request.user.username) in d['medproviders'], h ))
	for child in r:
		children.append((child['cid'], child['name']))
	form = NameForm(children)
	return render(request, 'addImmunizations.html', {'form':form})

@login_required
def addImmunizations_submit(request):
	assert request.user.profile.role == "HEAL"
	if request.method == "GET":
		cid = request.GET.get('child_access')
	else:
		cid = request.POST["child"]
	Immunirecord = formset_factory(Immunization, formset=RequiredFormSet)
	h = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform")
	h = h.json()
	r = list(filter(lambda d: (mprovider_prefix+request.user.username) in d['medproviders'], h ))
	chosen = (item for item in r if item["cid"] == cid).next()
	child_name = chosen["name"]
	existing_record = chosen["immunizations"]
	meddict = {}
	for record in existing_record:
		if record['provider'] not in meddict.keys() and record['provider']!="default":
			r = requests.get("http://148.100.4.163:3000/api/ibm.wsc.immunichain.MedProvider/"+record['provider'])
			r = r.json()
			meddict[record['provider']] = r["name"]
	renderdict = {'cid': cid, 'child_name': child_name, 'existing_record': existing_record, "meddict": meddict,'Immunirecord': Immunirecord}

	if request.method == "POST":
		formset = Immunirecord(request.POST)	#cleaning process starts here
		if formset.is_valid():
			immunizations = []
			providerid = request.user.username
			for form in formset:
				name = form.cleaned_data.get('name')
				date = form.cleaned_data.get('date')
				if name and date:
					d = {'name': name, 'provider': providerid, 'imdate':str(date)}
					immunizations.append(d)
			immunizations = json.dumps(immunizations)
			d = {"childform": cid, "vaccines": immunizations}
			r = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.addImmunizations", data=d)
			assert r.status_code == SUCCESS_CALL
			return redirect('success')
		else:
			renderdict['Immunirecord'] = formset
	return render(request, 'addImmunizations_submit.html', renderdict)

@login_required
def newchild(request):
	assert request.user.profile.role == 'GRDN'
	if request.method == 'POST':
		form = NewChildForm(request.POST)
		if form.is_valid():
			child = form.save()
			cid = form.cleaned_data.get('username')
			name = form.cleaned_data.get('full_name')
			address = form.cleaned_data.get('address')
			guardian = request.user.username
			dob = form.cleaned_data.get('birthdate')
			medproviders = form.cleaned_data.get('medproviders') 
			members = form.cleaned_data.get('members')
			medproviders = json.dumps(medproviders)
			members = json.dumps(members)
			default = json.dumps([{"name": "default", "provider": "default", "imdate": "default"}])
			d = {'cid':cid, 'name':name, 'address':address, "guardian":guardian, 'dob':dob, 
			'medproviders': medproviders, 'members':members, "immunizations": default }
			r = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Childform", data=d)
			print r
			if r.status_code == SUCCESS_CALL:
				return redirect('success')
			else:
				return redirect('failure')
	else:
		form = NewChildForm()

	return render(request, 'newchild.html', {'form':form})

def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		print "HELLO"
		if form.is_valid():
			role = form.cleaned_data.get('role')
			full_name = form.cleaned_data.get('full_name')
			username = form.cleaned_data.get('username')

			assert role in ["GRDN","MEMB","HEAL"]
			if role == 'GRDN':
				d = {'gid': username, 'name': full_name}
				r = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Guardian", data=d)
				assert r.status_code == SUCCESS_CALL
			elif role == "MEMB":
				d = {'memid': username, 'name': full_name}
				r = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.Member", data=d)
				assert r.status_code == SUCCESS_CALL
			else:
				d = {'medid': username, 'name': full_name}
				r = requests.post("http://148.100.4.163:3000/api/ibm.wsc.immunichain.MedProvider", data=d)
				assert r.status_code == SUCCESS_CALL

			user = form.save()
			user.refresh_from_db()
			user.profile.role = role
			user.profile.full_name = full_name
			user.save()
			raw_password= form.cleaned_data.get('password1')
			user=authenticate(username=user.username,password=raw_password)
			login(request,user)
			return redirect('home')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form':form})


@login_required
def success(request):
	return render(request, 'success.html')

@login_required
def failure(request):
	return render(request, 'failure.html')

@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)