# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests 

# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	full_name = models.CharField(max_length=60)
	ROLE_CHOICES = (('','-----------'),('GRDN', 'Guardian'), ('MEMB', 'Member Organization'), ('HEAL', 'Healthcare Provider'))
	role = models.CharField(max_length=4,choices=ROLE_CHOICES)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	instance.profile.save()

class ChildProfile(models.Model):
	username = models.CharField(unique=True, help_text="Required. 150 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters.", max_length=150)
	full_name = models.CharField(help_text="Please enter your child's full name.", max_length=60)
	address = models.CharField(help_text="Please enter your child's address", max_length=24)

def get_choices(participant):
	print "I'm getting choices!"
	results = []
	if participant == "MEMB":
		r = requests.get("https://148.100.4.163:3000/api/ibm.wsc.immunichain.Member", verify=False)
		for member in r.json():
			results.append((member['memid'], member['name']))
		return results
	elif participant == "HEAL":
		r = requests.get("https://148.100.4.163:3000/api/ibm.wsc.immunichain.MedProvider", verify=False)
		for provider in r.json():
			results.append((provider['medid'], provider['name']))
		return results
	else:
		return results