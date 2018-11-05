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
#  This searches out irregularities in the Vitals data and attempts to
# correct or clean it up.
#
# Temperature  - look for values outside the normal ranges and auto-
#		convert them or delete them.
#
#

import sys, re

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

from ocemr.models import Vital
from ocemr.models import VitalType

from django.db.models import get_model, Q
from datetime import datetime

# Temperature
for v in Vital.objects.filter( Q(type=VitalType.objects.get(id=3)) ):
	if v.data > 45.:
		print v,
		# do something
		print 

	#v.save()
