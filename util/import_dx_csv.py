#!/usr/bin/python
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
#
import sys, csv, re

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

from django.conf import settings

#from ocemr.models import ###
from ocemr.models import DiagnosisType
reader = csv.reader(open("%s/source_data/%s/EngeyeEMRdx.csv"%(settings.CONTRIB_PATH, util_conf.SOURCE_TEMPLATE), "rb"))

for row in reader:
	if row[0] == "icpc2code": continue
	if len(row) < 3: continue
	if row[2] =="": continue
	icpc2Code=row[0]
	title=row[2]
	print "[%s:%s] "%(icpc2Code,title),
	dt, is_new = DiagnosisType.objects.get_or_create(icpc2Code=icpc2Code,title=title)
	if is_new:
		print "{NEW} ",
		dt.save()
	else:
		print "{exists} ",
	print ""
	
