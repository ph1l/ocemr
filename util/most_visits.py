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


#
#   This is a quick and dirty hack to see which patients have the most
# visits. It makes it easier to find the best patients to test some
# things.
#

import sys, re

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

#from ocemr.models import ###
from ocemr.models import Patient
from ocemr.models import Visit

from django.db.models import get_model, Q
from datetime import datetime

patient_visit_count={}
for p in Patient.objects.all():
	patient_visit_count[p] = 0
	for v in Visit.objects.filter( Q(status='RESO') ).filter(patient=p):
		patient_visit_count[p] += 1
	print "%d %s" % ( patient_visit_count[p], p)
