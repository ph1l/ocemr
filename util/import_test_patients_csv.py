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
from ocemr.models import Patient, Village, Visit
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

reader = csv.reader(open("%s/source_data/%s/OcemrTestPatients.csv"%(settings.CONTRIB_PATH, util_conf.SOURCE_TEMPLATE), "rb"))

u = User.objects.get(pk=1)

for row in reader:
	if row[0] == "Family Name": continue
	if len(row) < 6: continue
	if row[5] =="": continue
	f_name=row[0]
	g_name=row[1]
	m_name=row[2]
	gender=row[3]
	byear=row[4]
	village_in=row[5]
	v, is_new = Village.objects.get_or_create(name=village_in)
	if is_new:
		print "NEW Village: %s"%(v)
		v.save()
	print "[%s:%s:%s:%s:%s:%s] "%(f_name,g_name,m_name,gender,byear,v),
	p, is_new = Patient.objects.get_or_create(familyName=f_name,givenName=g_name,middleName=m_name,gender=gender,birthYear=byear,village=v,createdBy=u)
	if is_new:
		print "{NEW} ",
		p.save()
	else:
		print "{exists} ",
	# Add a Randomish Visit
	d = datetime.today()+timedelta(random.choice((-1,0,0,1,1,1,2)) )
	t = random.choice( ("7:00","9:00","11:00","13:00","15:00")  )
	print " V:%s:%s"%(d.date(),t)
	v = Visit.objects.create(patient=p, scheduledDate=d.date(), scheduledBy=u)
	v.save()
