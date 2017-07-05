######
IMMUNIchain Webapp
######

This has been tested on Ubuntu 16.04
Prerequisite software:
	- Django, run ```sudo pip install Django==1.11.3```
	- requests, run ```sudo pip install requests```

1- 	Navigate to the folder with ```manage.py``` in it, in this case
	it should be in webapp/

2-	Run ```python manage.py makemigrations core```
3- 	Run ```python manage.py migrate```
4- 	Run ```python manage.py runserver```

5-	If there are no errors, the webpage should be open on localhost:8000

Notes: 	Because this has not been deployed to a server yet, the blockchain will have
		more participants than there locally are in your own database. In this case,
		if you want to play around with multiple participant types, you will need 
		to keep track of the participants you have created. When the app is deployed
		to a server, the login database and blockchain will be in sync.