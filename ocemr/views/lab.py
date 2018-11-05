
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest


from django.db.models import Q


@login_required
def lab_queue(request):
	"""
	"""
	from datetime import datetime, timedelta
	d_today = datetime.today()
	d_midnight = datetime(d_today.year,d_today.month,d_today.day,0,0,0)

	from ocemr.models import Lab

	active_q = Q(status='ORD' ) | Q(status='PEN' )
	inactive_q = Q(orderedDateTime__gte=d_midnight) & ( Q(status='CAN' ) | Q(status='COM' ) | Q(status='FAI') )

	labs_active = Lab.objects.filter(active_q).order_by('orderedDateTime', '-id')
	labs_inactive = Lab.objects.filter(inactive_q).order_by('orderedDateTime', '-id')
	return render(request, 'lab_queue.html', locals())

@login_required
def lab_start(request,id):
	"""
	"""
	from ocemr.models import Lab, LabNote

	l = Lab.objects.get(pk=id)
	l.status = 'PEN'
	l.save()
	ln = LabNote(lab=l, addedBy=request.user, note="Lab Started")
	ln.save()
	return render(request, 'close_window.html', {})

@login_required
def lab_cancel(request,id):
	"""
	"""
	from ocemr.models import Lab, LabNote

	l = Lab.objects.get(pk=id)
	l.status = 'CAN'
	l.save()
	ln = LabNote(lab=l, addedBy=request.user, note="Lab Canceled")
	ln.save()
	return render(request, 'close_window.html', {})

@login_required
def lab_fail(request,id):
	"""
	"""
	from ocemr.models import Lab, LabNote

	l = Lab.objects.get(pk=id)
	l.status = 'FAI'
	l.save()
	ln = LabNote(lab=l, addedBy=request.user, note="Lab Failed")
	ln.save()
	return render(request, 'close_window.html', {})
@login_required
def lab_reorder(request,id):
	"""
	"""
	from ocemr.models import Lab

	l = Lab.objects.get(pk=id)
	newl = Lab(type = l.type, patient = l.patient, visit=l.visit, orderedBy=request.user, status='ORD')
	newl.save()
	return render(request, 'close_window.html', {})

@login_required
def lab_notate(request, id):
	"""
	"""
	from ocemr.models import LabNote, Lab, Visit
	from ocemr.forms import NewLabNoteForm

	labid=int(id)
	l=Lab.objects.get(pk=labid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewLabNoteForm(l, request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewLabNoteForm(l, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Add an Lab Note: %s'%(l.type.title),
		'form_action': '/lab/%d/notate/'%(l.id),
		'form': form,
	})

@login_required
def lab_complete(request, id):
	"""
	"""
	from ocemr.models import Lab
	from ocemr.forms import CompleteLabForm
	l = Lab.objects.get(pk=id)

	if request.method == 'POST':
		form = CompleteLabForm(request.POST)
		if form.is_valid():
			l.result = form.cleaned_data['result']
			l.status='COM'
			l.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = CompleteLabForm()
	return render(request, 'popup_form.html', {
		'title': 'Complete Lab: %s'%(l),
		'form_action': '/lab/%s/complete/'%(l.id),
		'form': form,
	})
