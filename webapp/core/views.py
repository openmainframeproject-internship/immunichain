# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from core.forms import SignUpForm, NameForm, NewChildForm, UpdateForm, SignUpForm_reassign
from django.template.defaulttags import register
from datetime import datetime
import json
import requests

SUCCESS_CALL = 200
LEGAL_AGE = 18.0
guardian_prefix = 'resource:ibm.wsc.immunichain.Guardian#'
mprovider_prefix = 'resource:ibm.wsc.immunichain.MedProvider#'
memberorg_prefix = 'resource:ibm.wsc.immunichain.Member#'
rest_prefix = 'https://148.100.4.163:3000/api/'

# Create your views here.
@login_required
def home(request):
	user_role = request.user.profile.role
	h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
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
	r = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
	CHILD_CHOICES = [("","-----------")]
	for child in r.json():
		if user_role == 'GRDN':
			if ("resource:ibm.wsc.immunichain.Guardian#"+username) == child['guardian']:
				CHILD_CHOICES.append((child['cid'],child['name']+", "+child['cid']))
		elif user_role == 'MEMB':
			if (memberorg_prefix+username) in child['members']:
				CHILD_CHOICES.append((child['cid'],child['name']+", "+child['cid']))
		else:
			if (mprovider_prefix+username) in child['medproviders']:
				CHILD_CHOICES.append((child['cid'],child['name']+", "+child['cid']))

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
					r = requests.get(rest_prefix + "ibm.wsc.immunichain.MedProvider/"+lookup, verify=False)
					r = r.json()
					userdict[provider] = r["name"]
			for member in members:
				if member not in userdict.keys():
					garbage,lookup=member.split("#",1)
					r = requests.get(rest_prefix + "ibm.wsc.immunichain.Member/"+lookup, verify=False)
					r = r.json()
					userdict[member] = r["name"]
			if guardian not in userdict.keys():
				garbage,lookup=guardian.split("#",1)
				r = requests.get(rest_prefix + "ibm.wsc.immunichain.Guardian/"+lookup, verify=False)
				r = r.json()
				userdict[guardian] = r["name"]
			for record in vaccines:
				if record['provider'] not in userdict.keys() and record['provider']!='default':
					r = requests.get(rest_prefix + "ibm.wsc.immunichain.MedProvider/"+record['provider'], verify=False)
					r = r.json()
					userdict[record['provider']] = r["name"]

			return render(request, 'viewchild.html', {'h':h, 'form': form, "userdict": userdict})
	else:
		form = NameForm(CHILD_CHOICES)

	return render(request, 'viewchild.html', {'form': form})

@login_required
def auth_member_select(request):
	if request.user.profile.role == 'GRDN':
		children = [("","-----------")]
		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
		for child in r:
			children.append((child['cid'], child['name']+", "+child['cid']))
		if request.method == 'POST':
			form = NameForm(children, request.POST)
			if form.is_valid():
				cid = form.cleaned_data.get('child_access')
				chosen = (item for item in r if item["cid"] == cid).next()
				child_name = chosen["name"]			
				r = requests.get(rest_prefix + "ibm.wsc.immunichain.Member", verify=False)
				avail_members = [(d['name'], d['memid']) for d in r.json()]
				renderdict = {'cid': cid, 'child_name': child_name, 'avail_members': avail_members}
				return render(request, 'auth_member_select.html', renderdict)
		else:
			form = NameForm(children)
		return render(request, 'auth_member_select.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def auth_member_submit(request):
	if request.user.profile.role == 'GRDN' and request.method == 'POST':
		memid = request.POST['newmember']
		cid = request.POST["child"]
		r = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform/"+cid, verify=False)
		r = r.json()
		existing_members = r["members"]

		if (memberorg_prefix+memid) not in existing_members:
			gid = request.user.username
			d = {"guardian": gid,"member": memid, "childform": cid}
			make = requests.post(rest_prefix + "ibm.wsc.immunichain.authMember", data=d, verify=False)
			assert make.status_code == SUCCESS_CALL

		return redirect('success')
	else:
		return redirect('deny')

@login_required
def assignmed_select(request):
	if request.user.profile.role == 'GRDN':
		children = [("","-----------")]
		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
		for child in r:
			children.append((child['cid'], child['name']+", "+child['cid']))
		if request.method == 'POST':
			form = NameForm(children, request.POST)
			if form.is_valid():
				cid = form.cleaned_data.get('child_access')
				chosen = (item for item in r if item["cid"] == cid).next()
				child_name = chosen["name"]			
				r = requests.get(rest_prefix + "ibm.wsc.immunichain.MedProvider", verify=False)
				avail_medproviders = [(d['name'], d['medid']) for d in r.json()]
				renderdict = {'cid': cid, 'child_name': child_name, 'avail_medproviders': avail_medproviders}
				return render(request, 'assignmed_select.html', renderdict)
		else:
			form = NameForm(children)
		return render(request, 'assignmed_select.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def assignmed_submit(request):
	if request.user.profile.role == 'GRDN' and request.method == 'POST':
		medid = request.POST['newmed']
		cid = request.POST["child"]
		r = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform/"+cid, verify=False)
		r = r.json()
		existing_medproviders = r["medproviders"]

		if (mprovider_prefix+medid) not in existing_medproviders:
			gid = request.user.username
			d = {"guardian": gid,"medprovider": medid, "childform": cid}
			make = requests.post(rest_prefix + "ibm.wsc.immunichain.assignMedProvider", data=d, verify=False)
			assert make.status_code == SUCCESS_CALL

		return redirect('success')
	else:
		return redirect('deny')

@login_required
def deauth_member_select(request):
	if request.user.profile.role == 'GRDN':
		children = [("","-----------")]
		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
		for child in r:
			children.append((child['cid'], child['name']+", "+child['cid']))
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
					user = requests.get(rest_prefix + "ibm.wsc.immunichain.Member/"+memberid, verify=False)
					user = user.json()
					avail_members.append((user['name'], memberid))
				renderdict = {'cid': cid, 'child_name': child_name, 'avail_members': avail_members}
				return render(request, 'deauth_member_select.html', renderdict)
		else:
			form = NameForm(children)
		return render(request, 'deauth_member_select.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def deauth_member_submit(request):
	if request.user.profile.role == 'GRDN' and request.method == 'POST':
		memid = request.POST['newmember']
		cid = request.POST["child"]
		r = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform/"+cid, verify=False)
		r = r.json()
		existing_members = r["members"]
		if (memberorg_prefix+memid) in existing_members:
			gid = request.user.username
			d = {"guardian": gid,"member": memid, "childform": cid}
			make = requests.post(rest_prefix + "ibm.wsc.immunichain.removeMemberAuth", data=d, verify=False)
			assert make.status_code == SUCCESS_CALL
		return redirect('success')
	else:
		return redirect('deny')

@login_required
def update(request):
	if request.user.profile.role == 'GRDN':
		children = [("","-----------")]
		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
		for child in r:
			children.append((child['cid'], child['name']+', '+child['cid']))
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
				r = requests.post(rest_prefix + "ibm.wsc.immunichain.updateChildForm", data=d, verify=False)
				if r.status_code == SUCCESS_CALL:
					return redirect('success')
				else:
					return redirect('failure')
		else:
			form = UpdateForm(children)
		return render(request, 'update.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def addImmunizations(request):
	if request.user.profile.role == 'HEAL':
		children = [("","-----------")]
		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: (mprovider_prefix+request.user.username) in d['medproviders'], h ))
		for child in r:
			children.append((child['cid'], child['name']+', '+child['cid']))
		form = NameForm(children)
		return render(request, 'addImmunizations.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def addImmunizations_submit(request):
	if request.user.profile.role == "HEAL":
		# We reach here by addImmunizations and choose the childform
		if request.method == "GET":
			cid = request.GET.get('child_access')
		#if this is a POST request, we have the form
		else:
			cid = request.POST["child"]

		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: (mprovider_prefix+request.user.username) in d['medproviders'], h ))
		chosen = (item for item in r if item["cid"] == cid).next()
		child_name = chosen["name"]
		existing_record = chosen["immunizations"]
		meddict = {}
		for record in existing_record:
			if record['provider'] not in meddict.keys() and record['provider']!="default":
				r = requests.get(rest_prefix + "ibm.wsc.immunichain.MedProvider/"+record['provider'], verify=False)
				r = r.json()
				meddict[record['provider']] = r["name"]
		renderdict = {'cid': cid, 'child_name': child_name, 'existing_record': existing_record, "meddict": meddict,}

		if request.method == "POST":
			immunizations = []
			providerid = request.user.username
			names = request.POST.getlist('vaccine[]')
			dates = request.POST.getlist('immundate[]')

			for x in zip(names,dates):
				d = {'name': x[0], 'provider': providerid, 'imdate':str(x[1])}
				immunizations.append(d)

			immunizations = json.dumps(immunizations)
			d = {"childform": cid, "vaccines": immunizations}
			r = requests.post(rest_prefix + "ibm.wsc.immunichain.addImmunizations", data=d, verify=False)
			if r.status_code == SUCCESS_CALL:
				return redirect('success')
			else:
				return redirect('failure')

		#Dynamic formset is a pain to implement, so I got rid of it
		return render(request, 'addImmunizations_submit.html', renderdict)
	else:
		return redirect('deny')

@login_required
def newchild(request):
	if request.user.profile.role == 'GRDN':
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
				r = requests.post(rest_prefix + "ibm.wsc.immunichain.Childform", data=d, verify=False)
				if r.status_code == SUCCESS_CALL:
					return redirect('success')
				else:
					return redirect('failure')
		else:
			form = NewChildForm()

		return render(request, 'newchild.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def reassign_select(request):
	if request.user.profile.role == 'GRDN':
		children = [("","-----------")]
		h = requests.get(rest_prefix + "ibm.wsc.immunichain.Childform", verify=False)
		h = h.json()
		r = list(filter(lambda d: d['guardian'] == (guardian_prefix+request.user.username), h ))
		for child in r:
			children.append((child['cid'], child['name']+", "+child['cid']))
		if request.method == 'POST':
			form = NameForm(children, request.POST)
			if form.is_valid():
				cid = form.cleaned_data.get('child_access')
				chosen = (item for item in r if item["cid"] == cid).next()
				#check if the child is old enough
				dob = chosen["dob"]
				dobcheck = datetime.strptime(dob, '%Y-%m-%d')
				timenow = datetime.now()
				difference = timenow - dobcheck
				difference_in_years = (difference.days + difference.seconds/86400)/365.0
				if difference_in_years >= LEGAL_AGE:
					child_name = chosen["name"]
					newform = SignUpForm_reassign()
					renderdict = {'cid': cid, 'child_name': child_name, 'newform': newform}
					return render(request, 'reassign_select.html', renderdict)
				else:
					return redirect('underage')
		else:
			form = NameForm(children)
		return render(request, 'reassign_select.html', {'form':form})
	else:
		return redirect('deny')

@login_required
def reassign_submit(request):
	if request.user.profile.role == 'GRDN' and request.method == 'POST':
		ids = request.POST.getlist('child[]')
		cid = ids[0]
		full_name = ids[1]
		form = SignUpForm_reassign(request.POST)
		if form.is_valid():
			print "I'm valid"
			username = form.cleaned_data.get('username')
			d = {'gid': username, 'name': full_name}
			r = requests.post(rest_prefix + "ibm.wsc.immunichain.Guardian", data=d, verify=False)
			assert r.status_code == SUCCESS_CALL
			user = form.save()
			user.refresh_from_db()
			user.profile.role = 'GRDN'
			user.profile.full_name = full_name
			user.save()
			raw_password= form.cleaned_data.get('password1')
			user = authenticate(username=user.username,password=raw_password)
			d = {"oldguardian": request.user.username, "newguardian": username, "childform": cid}
			r = requests.post(rest_prefix + "ibm.wsc.immunichain.reassignGuardian", data=d, verify=False)
			assert r.status_code == SUCCESS_CALL
			return redirect('success')
		else:
			renderdict = {'cid': cid, 'child_name': full_name, 'newform': form}
		return render(request, 'reassign_select.html', renderdict)
	else:
		return redirect('deny')

def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			role = form.cleaned_data.get('role')
			full_name = form.cleaned_data.get('full_name')
			username = form.cleaned_data.get('username')
			assert role in ["GRDN","MEMB","HEAL"]
			if role == 'GRDN':
				d = {'gid': username, 'name': full_name}
				r = requests.post(rest_prefix + "ibm.wsc.immunichain.Guardian", data=d, verify=False)
				assert r.status_code == SUCCESS_CALL
			elif role == "MEMB":
				d = {'memid': username, 'name': full_name}
				r = requests.post(rest_prefix + "ibm.wsc.immunichain.Member", data=d, verify=False)
				assert r.status_code == SUCCESS_CALL
			else:
				d = {'medid': username, 'name': full_name}
				r = requests.post(rest_prefix + "ibm.wsc.immunichain.MedProvider", data=d, verify=False)
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

@login_required
def deny(request):
	return render(request, 'deny.html')

@login_required
def underage(request):
	return render(request, 'underage.html')

@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)