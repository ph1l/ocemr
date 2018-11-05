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
from ocemr.models import VitalType

import datetime
reader = csv.reader(open("%s/source_data/%s/OcemrVitalTypes.csv"%(settings.CONTRIB_PATH, util_conf.SOURCE_TEMPLATE), "rb"))

for row in reader:
	if row[0] == "title": continue
	if len(row) < 4: continue
	if row[3] =="": continue
	title=row[0]
	unit=row[1]
	minValue=float(row[2])
	maxValue=float(row[3])
	vt, is_new = VitalType.objects.get_or_create(title=title)
	print "Vital: %s "%(vt),
	if is_new:
		print "NEW ",
		vt.save()
	else:
		print "OLD ",
	print "[%s"%(unit),
	if vt.unit != unit:
		vt.unit=unit
		print "!",
		vt.save()
	print ":%s"%(minValue),
	if vt.minValue != minValue:
		vt.minValue = minValue
		print "!",
		vt.save()
	print ":%s"%(maxValue),
	if vt.maxValue != maxValue:
		vt.maxValue = maxValue
		print "!",
		vt.save()
	print "]"
