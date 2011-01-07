#!/usr/bin/python

import sys

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

from django.core.management import setup_environ

import settings

setup_environ(settings)


from django.contrib.auth.models import User
user = User.objects.create_user('viewer', 'asdf@asdf.com', util_conf.VIEWER_PASSWORD)

user.is_staff = True
user.is_superuser = True
user.save()
