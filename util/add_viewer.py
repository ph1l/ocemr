#!/usr/bin/python

import sys

import util_conf
sys.path = [util_conf.APP_PATH] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

from django.contrib.auth.models import User
user = User.objects.create_user('viewer', 'asdf@asdf.com',
                                util_conf.VIEWER_PASSWORD)

user.is_staff = True
user.is_superuser = True
user.save()
