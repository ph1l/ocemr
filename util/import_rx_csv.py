#!/usr/bin/python
#
##########################################################################
#
#    This file is part of OCEMR.
#
#    OCEMR is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OCEMR is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OCEMR.  If not, see <http://www.gnu.org/licenses/>.
#
#
#########################################################################
#       Copyright 2011-8 Philip Freeman <elektron@halo.nu>
##########################################################################
import sys, csv, re

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

from django.conf import settings

#from ocemr.models import ###
from ocemr.models import MedType

import datetime
reader = csv.reader(open("%s/source_data/%s/EngeyeEMRrx.csv"%(settings.CONTRIB_PATH, util_conf.SOURCE_TEMPLATE), "rb"))

for row in reader:
	if row[0] == "title": continue
	if len(row) < 1: continue
	if row[0] =="": continue
	title=row[0]
	rt, is_new = MedType.objects.get_or_create(title=title)
	print "MedType: %s "%(rt),
	if is_new:
		print "NEW ",
		rt.save()
	else:
		print "OLD ",
	print ""
