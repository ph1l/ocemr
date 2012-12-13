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
#       Copyright 2011 Philip Freeman <philip.freeman@gmail.com>
##########################################################################
import sys, csv, re, json, datetime

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

from django.core.management import setup_environ

import settings

setup_environ(settings)

#from ocemr.models import ###
from ocemr.models import Patient, Village, Visit
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

reader = csv.reader(open("%s"%(sys.argv[1]), "rb"))

u = User.objects.get(pk=1)
patient_list = []
patient = None
patient_row_num=0
found_header = False
current_year = datetime.now().year

for row in reader:
	if row[0] == "Patient Name":
		found_header = True
		continue
	if not found_header:
		continue
	if len(row) < 17: continue
	patient_row_num += 1
	if row[0] != '': # New Patient
		if patient != None:
			patient_list.append(patient)
		patient = {}
		patient['visits']=[]
		patient_row_num=1
		# Name
		name_split = row[0].split(" ")
		if len(name_split) == 2:
			patient['familyName'] = name_split[0]
			patient['givenName'] = name_split[1]
		elif len(name_split) == 3:
			patient['familyName'] = name_split[0]
			patient['givenName'] = name_split[1]
			patient['middleName'] = name_split[1]
		else:
			sys.stderr.write("Name Parse Error row 0: %s. slit into %d pieces\n"%( row, len(name_split)))
			patient = None
			continue
		# Sex
		if row[1].strip().upper() in ( 'M', 'F' ):
			patient['gender'] = row[1].strip().upper()
		else:
			sys.stderr.write("Gender Parse Error row 1: %s\n"%(row))
			patient = None
			continue
		# Age
		try:
			age = int(row[2])
		except:
			sys.stderr.write("Age Parse Error row 2: %s\n"%(row))
			patient=None
			continue
		patient['birthYear']=current_year-age
		patient['village']=row[3]
	else: # following rows
		if patient_row_num == 2:
			try:
				patient['id'] = int(row[4])
			except:
				sys.stderr.write("Warning: id not found for %s %s %s.\n"%(" ".join((patient['givenName'], patient['familyName'])), patient['gender'],patient['birthYear']))
				patient['id'] = None
			
		
	continue
print json.dumps(patient_list, sort_keys=True, indent=4)
