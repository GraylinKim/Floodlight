#Import the files we need to work with the OS and System variables
import os, sys

#Get the drive of this file (should be root of django app)
#__file__ is a magic python variable that gets the current file
appFolder = os.path.dirname(__file__)

#Step back to the parent directory by joining with a ../
parentFolder = os.path.join(appFolder,'../')

#Append this folder to the system path so python can find our application files
sys.path.append(parentFolder)

#Set the location of settings file for django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Floodlight.settings'

#Import the wsgi handler and launch it!
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
