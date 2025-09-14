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
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from ocemr.forms import *

from django.db.models import Q
from django.views.decorators.cache import cache_page

@login_required
def select_date_for_patient_queue(request):
	"""
	"""
	from ocemr.forms import SelectDateForm
	import datetime

	form_valid=0
        if request.method == 'POST':
                form = SelectDateForm(request.POST)
                if form.is_valid():
                        date_in = form.cleaned_data['date']
			form_valid=1
        else:
                form = SelectDateForm()
	if not form_valid:
	        return render(request, 'popup_form.html', {
	                'title': 'Enter Date For Patient Queue',
	                'form_action': '/select_date_for_patient_queue/',
	                'form': form,
	        })
	days_offset=(datetime.date.today()-date_in).days *-1
	return HttpResponseRedirect('/patient_queue/%d/'%(days_offset))

@login_required
def patient_queue(request,dayoffset=0):
	"""
	"""
	from datetime import datetime, timedelta
	from ocemr.models import Visit

	d_today = datetime.today()

	#
	filter_visit_type = request.GET.get('filter_visit_type', None)

	# Cleanup missed visits
	d_missed = d_today-timedelta(7)
	missed_q = Q(scheduledDate__lte=str(d_missed.date())) & Q(status='SCHE')
	for mv in Visit.objects.filter(missed_q):
		mv.status = 'MISS'
		# finished by noone
		#mv.finishedBy = request.user
		mv.finishedDateTime = datetime.now()
		mv.save()

	dayoffset = int(dayoffset)
	dayoffset_prev = dayoffset-1
	dayoffset_next = dayoffset+1

	# Update "today" to be whenever we're offset to
	d_today += timedelta(dayoffset)

	dt_start = datetime(d_today.year,d_today.month,d_today.day,0,0,0)
        dt_end = datetime(d_today.year,d_today.month,d_today.day,23,59,59)

	if filter_visit_type:
		visit_type_q = Q(type=filter_visit_type)
	else:
		visit_type_q = Q()

	active_q = Q(status='WAIT') | Q(status='INPR')
	resolved_q =  ( Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end) ) & ( Q(status='CHOT') | Q(status='RESO') )

	visits = Visit.objects.filter(visit_type_q).filter(active_q).order_by('seenDateTime')
	r_visits = Visit.objects.filter(visit_type_q).filter(resolved_q).order_by('-finishedDateTime')
	num_active = len(visits)
	num_inactive = len(r_visits)

	return render(request, 'patient_queue.html', locals())

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

	return render(request, 'patient_new.html', {
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
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient Name',
		'form_action': '/patient/edit/name/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_gender(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientGenderForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.gender = form.cleaned_data['gender']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientGenderForm(initial={'gender': p.gender}) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient Gender',
		'form_action': '/patient/edit/gender/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_phone(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientPhoneForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.phone = form.cleaned_data['phone']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientPhoneForm(initial={'phone': p.phone}) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient Phone',
		'form_action': '/patient/edit/phone/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_email(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientEmailForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.email = form.cleaned_data['email']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientEmailForm(initial={'email': p.email}) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient E-Mail',
		'form_action': '/patient/edit/email/%s/'%(id),
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
	return render(request, 'popup_form.html', {
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
	return render(request, 'popup_form.html', {
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
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient Note',
		'form_action': '/patient/edit/note/%s/'%(id),
		'form': form,
	})


@login_required
def patient_edit_alt_contact_name(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientAltContactNameForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.altContactName = form.cleaned_data['alt_contact_name']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientAltContactNameForm(initial={'alt_contact_name': p.altContactName}) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient Alternate Contact Name',
		'form_action': '/patient/edit/alt_contact_name/%s/'%(id),
		'form': form,
	})

@login_required
def patient_edit_alt_contact_phone(request, id):
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditPatientAltContactPhoneForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			p.altContactPhone = form.cleaned_data['alt_contact_phone']
			p.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditPatientAltContactPhoneForm(initial={'alt_contact_phone': p.altContactPhone}) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Patient Alternate Contact Phone',
		'form_action': '/patient/edit/alt_contact_phone/%s/'%(id),
		'form': form,
	})

@login_required
def patient(request,id):
	"""
	Patient Index
	"""
	from ocemr.models import Patient, Visit

	p = Patient.objects.get(pk=id)
	upcoming_visits = Visit.objects.filter(patient=p).filter(status='SCHE').order_by('scheduledDate')
	visits = Visit.objects.filter(patient=p).exclude(status='SCHE').order_by('-seenDateTime')
	return render(request, 'patient.html', {
		'p':p,
		'visits': visits,
		'upcoming_visits': upcoming_visits,
	})

@login_required
def patient_search(request):
	"""
	"""
	if request.method == 'POST': # If the form has been submitted...
		form = PatientSearchForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			name = form.cleaned_data['name']
			village = form.cleaned_data['village']
			pid = form.cleaned_data['pid']
			from django.db.models import Q
			from ocemr.models import Patient
			#qset = Q ()
			patients = Patient.objects.all()
			if village != "":
				patients = patients.filter(village__name__icontains=village)
			if name != "":
				i = 0
				for term in name.split():
					if i:
					  q_name = q_name & (
					    Q( familyName__icontains=term ) |
					    Q( givenName__icontains=term )
					  )
					else:
					  q_name = (
                                            Q( familyName__icontains=term ) |
                                            Q( givenName__icontains=term )
                                          )
					i += 1
				patients = patients.filter(q_name)
			if pid != None:
				patients = patients.filter(pk=pid)
			return render(request, 'patient_list.html', {
				'patients':patients,
			})
	else:
		form = PatientSearchForm() # An unbound form

	return render(request, 'patient_search.html', {
		'form': form,
	})

@login_required
def schedule_new_visit(request, id):
	"""
	"""
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)

	if request.method == 'POST': # If the form has been submitted...
		form = NewScheduledVisitForm(request.user, p, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewScheduledVisitForm(request.user, p) # An unbound form

	return render(request, 'popup_form.html', {
		'title': 'Scedule Patient Visit',
		'form_action': '/patient/schedule_new_visit/%s/'%(id),
		'form': form,
	})

@login_required
def schedule_walkin_visit(request, id):
	"""
	"""
	from ocemr.models import Patient

	p = Patient.objects.get(pk=id)

	if request.method == 'POST': # If the form has been submitted...
		form = NewWalkinVisitForm(request.user, p, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewWalkinVisitForm(request.user, p) # An unbound form

	return render(request, 'popup_form.html', {
		'title': 'Schedule Patient Visit',
		'form_action': '/patient/schedule_walkin_visit/%s/'%(id),
		'form': form,
	})

@login_required
def delete_visit(request, id):
	"""
	"""
	from ocemr.models import Visit

	o = Visit.objects.get(pk=id)
	if not (o.status == 'SCHE' or o.status == 'WAIT'):
		return render(request, 'popup_info.html', {
			'title': 'Schedule Patient Visit',
			'info': "Cannot Delete Active Visit",
		})


        from ocemr.forms import ConfirmDeleteForm

        if request.method == 'POST':
                form = ConfirmDeleteForm(request.POST)
                if form.is_valid():
                        if form.cleaned_data['doDelete']:
                                o.delete()
                        return HttpResponseRedirect('/close_window/')
        else:
                form = ConfirmDeleteForm()
        return render(request, 'popup_form.html', {
                'title': 'Delete Visit: %s'%(o),
                'form_action': '/patient/delete_visit/%s/'%(id),
                'form': form,
        })

@login_required
def edit_visit(request, id):
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditScheduledVisitForm(v,request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			v.scheduledBy = form.cleaned_data['scheduledBy']
			v.scheduledDate = form.cleaned_data['scheduledDate']
			v.reasonDetail = form.cleaned_data['reasonDetail']
			v.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditScheduledVisitForm(v, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Visit',
		'form_action': '/patient/edit_visit/%s/'%(id),
		'form': form,
	})

@login_required
def edit_visit_seen(request, id):
	from django.utils import formats
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditVisitSeenForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			v.seenDateTime = "%s %s"%( form.cleaned_data['seenDate'], form.cleaned_data['seenTime'] )
			v.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditVisitSeenForm(initial={
			'seenDate':formats.date_format(
				v.seenDateTime, 'SHORT_DATE_FORMAT'),
			'seenTime':formats.date_format(
				v.seenDateTime, 'TIME_FORMAT'),
			})
	return render(request, 'popup_form.html', {
		'title': 'Edit Visit seen time',
		'form_action': '/patient/edit_visit_seen/%s/'%(id),
		'form': form,
	})

@login_required
def edit_visit_reason(request, id):
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if request.method == 'POST': # If the form has been submitted...
		form = EditVisitReasonForm(v, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			v.reasonDetail = form.cleaned_data['reasonDetail']
			v.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditVisitReasonForm(v) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Visit Reason',
		'form_action': '/patient/edit_visit_reason/%s/'%(id),
		'form': form,
	})

@login_required
def patient_merge(request, id):
	from ocemr.models import Patient, Visit, Vital, Lab, Diagnosis, Med, Referral, Allergy, CashLog

	p = Patient.objects.get(pk=int(id))
	valid_form=False

	if request.method == 'POST': # If the form has been submitted...
		form = MergePatientForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			duplicateID = form.cleaned_data['duplicateID']
			valid_form=True
	else:
		form = MergePatientForm() # An unbound form
	if not valid_form:
		return render(request, 'popup_form.html', {
			'title': 'Merge Patient Records',
			'form_action': '/patient/merge/%s/'%(id),
			'form': form,
		})
	pdup = Patient.objects.get(pk=int(duplicateID))
	out_txt="Merge %s: %s\n  into %s: %s\n\n"%(pdup.id, pdup, p.id, p)

	visits=		Visit.objects.filter(patient=pdup)
	vitals=		Vital.objects.filter(patient=pdup)
	labs=		Lab.objects.filter(patient=pdup)
	diagnoses=	Diagnosis.objects.filter(patient=pdup)
	meds=		Med.objects.filter(patient=pdup)
	referrals=	Referral.objects.filter(patient=pdup)
	allergies=	Allergy.objects.filter(patient=pdup)
	cashlogs=	CashLog.objects.filter(patient=pdup)

	for o in visits: out_txt += "  -> Visit: %s\n"%(o)
	for o in vitals: out_txt += "  -> Vital: %s\n"%(o)
	for o in labs: out_txt += "  -> Lab: %s\n"%(o)
	for o in diagnoses: out_txt += "  -> Diagnosis: %s\n"%(o)
	for o in meds: out_txt += "  -> Med: %s\n"%(o)
	for o in referrals: out_txt += "  -> Referral: %s\n"%(o)
	for o in allergies: out_txt += "  -> Allergy: %s\n"%(o)
	for o in cashlogs: out_txt += "  -> CashLog: %s\n"%(o)

	out_txt += "\n\nThere is NO UNDO function to reverse this change.\n"
	out_txt += "Please be sure this is what you want before continuing...\n"
	out_link = "<A HREF=/patient/merge/%d/%d/>Do the merge!</A> or "%(p.id,pdup.id)
	return render(request, 'popup_info.html', {
		'title': 'Schedule Patient Visit',
		'info': out_txt,
		'link_text': out_link,
		})

@login_required
def patient_do_merge(request, id, dupid):
	from ocemr.models import Patient, Visit, Vital, Lab, Diagnosis, Med, Referral, Allergy, CashLog

	p = Patient.objects.get(pk=int(id))
	pdup = Patient.objects.get(pk=int(dupid))


	visits=		Visit.objects.filter(patient=pdup)
	vitals=		Vital.objects.filter(patient=pdup)
	labs=		Lab.objects.filter(patient=pdup)
	diagnoses=	Diagnosis.objects.filter(patient=pdup)
	meds=		Med.objects.filter(patient=pdup)
	referrals=	Referral.objects.filter(patient=pdup)
	allergies=	Allergy.objects.filter(patient=pdup)
	cashlogs=	CashLog.objects.filter(patient=pdup)

	for o in visits:
		o.patient=p
		o.save()
	for o in vitals:
		o.patient=p
		o.save()
	for o in labs:
		o.patient=p
		o.save()
	for o in diagnoses:
		o.patient=p
		o.save()
	for o in meds:
		o.patient=p
		o.save()
	for o in referrals:
		o.patient=p
		o.save()
	for o in allergies:
		o.patient=p
		o.save()
	pdup.delete()

	return HttpResponseRedirect('/close_window/')
