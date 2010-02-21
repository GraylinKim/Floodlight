#Import the files we need to work with the OS and System variables
import os, sys

#Import handlers to setup our app to run as a wsgi child process
import django.core.handlers.wsgi

#Get the drive of this file (should be in root of django app)
#__file__ is a magic python variable that gets the current file
appPath = os.path.dirname(__file__)

#Split the path into appDirectory and appModule
(appDirectory,appModule) = os.path.split(appPath)

#Add the appDirectory to the system path
sys.path.append(appDirectory)

#Use the appModule.settings as the location of settings django settings file
os.environ['DJANGO_SETTINGS_MODULE'] = appModule+'.settings'

#Run our application!!
application = django.core.handlers.wsgi.WSGIHandler()
