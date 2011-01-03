
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from ocemr.forms import *

from django.db.models import get_model, Q

@login_required
def med_queue(request):
	"""
	"""
	from datetime import datetime, timedelta
        d_today = datetime.today().date()
	t_missed = datetime.today()-timedelta(7)
	d_missed = t_missed.date()

	q_today = Q( scheduledDate=d_today ) & Q(Q(status='CHOT')|Q(status='RESO'))
	q_missed = Q( scheduledDate__gte=d_missed )& Q( status='CHOT' )
	from ocemr.models import Visit
	visits = Visit.objects.filter(q_today|q_missed)
	cleaned_visits=[]
	for v in visits:
		if v.get_num_meds > 0:
			cleaned_visits.append(v)
	visits = cleaned_visits
	return render_to_response('med_queue.html', locals())

@login_required
def meds_view(request,vid):
	"""
	"""
	from ocemr.models import Visit

	vid = int(vid)
	v = Visit.objects.get(pk=vid)

	return render_to_response('meds_view.html',locals())

