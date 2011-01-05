
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
from django.views.decorators.cache import cache_page

@login_required
def patient_queue(request):
	"""
	"""
	from datetime import datetime, timedelta
	d_today = datetime.today()
	d_missed = datetime.today()-timedelta(7)
	d_upcoming = datetime.today()+timedelta(7)

	from ocemr.models import Visit

	unresolved_q = Q(scheduledDate__lte=d_today.date) & ( Q(status='SCHE') | Q(status='WAIT') | Q(status='INPR') )
	resolved_q =  Q(scheduledDate=d_today.date) & ( Q(status='MISS') | Q(status='CHOT') | Q(status='RESO') )
	missed_q = Q(scheduledDate__gt=d_missed.date) & Q(status='MISS')
	
	visits = Visit.objects.filter(unresolved_q).order_by('scheduledDate', 'scheduledTime', 'id')
	r_visits = Visit.objects.filter(resolved_q).order_by('scheduledDate', 'scheduledTime', 'id')
	return render_to_response('patient_queue.html', locals())

@login_required
def patient_new(request):
	"""
	Create a new Patient Record
	Redirect to Patient detail page
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = NewPatientForm(request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/patient/%d/'%(o.id))
	else:
		form = NewPatientForm(request.user) # An unbound form

	return render_to_response('patient_new.html', {
		'form': form,
	})

@login_required
def patient_edit_name(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientNameForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.familyName = form.cleaned_data['familyName']
			p.givenName = form.cleaned_data['givenName']
			p.middleName = form.cleaned_data['middleName']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientNameForm(initial={'familyName': p.familyName, 'givenName': p.givenName, 'middleName': p.middleName }) # An unbound form
	return render_to_response('popup_form.html', {
		'title': 'Edit Patient Name',
		'form_action': '/patient/edit/name/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_age(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientAgeForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.birthYear = form.cleaned_data['birthYear']
			p.birthDate = form.cleaned_data['birthDate']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientAgeForm(initial={'birthYear': p.birthYear, 'birthDate': p.birthDate}) # An unbound form
	return render_to_response('popup_form.html', {
		'title': 'Edit Patient Age',
		'form_action': '/patient/edit/age/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_village(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientVillageForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.village = form.cleaned_data['village']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientVillageForm(initial={'village': p.village}) # An unbound form
	return render_to_response('popup_form.html', {
		'title': 'Edit Patient Village',
		'form_action': '/patient/edit/village/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_note(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientNoteForm(p,request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.scratchNote = form.cleaned_data['NoteText']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientNoteForm(p) # An unbound form
	return render_to_response('popup_form.html', {
		'title': 'Edit Patient Note',
		'form_action': '/patient/edit/note/%s/'%(id),
		'form': form,
	})


@login_required
def patient(request,id):
	"""
	Patient Index
	"""
	from ocemr.models import Patient, Visit

	p = Patient.objects.get(pk=id)
	visits = Visit.objects.filter(patient=p).order_by('-id')
	return render_to_response('patient.html', {
		'p':p,
		'visits': visits,
	})

@login_required
def patient_search(request):
	"""
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = PatientSearchForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			familyName = form.cleaned_data['familyName']
			givenName = form.cleaned_data['givenName']
			village = form.cleaned_data['village']
			from django.db.models import Q
			from ocemr.models import Patient
			#qset = Q ()
			patients = Patient.objects.all()
			if village != "":
				patients = patients.filter(village__name__icontains=village)
			if familyName != "":
				patients = patients.filter(familyName__icontains=familyName)
			if givenName != "":
				patients = patients.filter(givenName__icontains=givenName)
			return render_to_response('patient_list.html', {
				'patients':patients,
			})
	else:
		form = PatientSearchForm() # An unbound form

	return render_to_response('patient_search.html', {
		'form': form,
	})

@login_required
def patient_new_visit(request, id):
	"""
	"""
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)

	if request.method == 'POST': # If the form has been submitted...
		form = NewVisitForm(request.user, p, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewVisitForm(request.user, p) # An unbound form

	return render_to_response('popup_form.html', {
		'title': 'Scedule Patient Visit',
		'form_action': '/patient/new_visit/%s/'%(id),
		'form': form,
	})
