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
#  This was a quick and dirty hack to add some data to the DB after a schema
# change.
#

import sys, re

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

#from ocemr.models import ###
from ocemr.models import Visit
from ocemr.models import User

from django.db.models import get_model, Q
from datetime import datetime
visits = Visit.objects.filter( Q(status='RESO') & 
		(
		Q(seenDateTime=None) |
		Q(claimedDateTime=None) |
		Q(finishedDateTime=None) |
		Q(resolvedDateTime=None) |
		Q(claimedBy=None) |
		Q(finishedBy=None) |
		Q(resolvedBy=None)
		)
		)
u = User.objects.get(pk=1)

for v in visits:
	print v
	dd = v.scheduledDate
	if v.seenDateTime == None:
		v.seenDateTime=datetime(dd.year,dd.month,dd.day,9,42,0)
	if v.claimedDateTime == None:
		v.claimedDateTime=datetime(dd.year,dd.month,dd.day,9,42,0)
	if v.claimedBy == None:
		v.claimedBy = u
	if v.finishedDateTime == None:
		v.finishedDateTime=datetime(dd.year,dd.month,dd.day,9,42,0)
	if v.finishedBy == None:
		v.finishedBy = u
	if v.resolvedDateTime == None:
		v.resolvedDateTime=datetime(dd.year,dd.month,dd.day,9,42,0)
	if v.resolvedBy == None:
		v.resolvedBy = u
	v.save()
