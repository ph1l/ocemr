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

def get_visit_menu(current,patient):
	
	menu = [
		{ 'link': 'past', 'ord':1, 'title': 'Past Visits', 'active': False },
		{ 'link': 'subj', 'ord':2, 'title': 'Reason for Visit', 'active': False },
		{ 'link': 'obje', 'ord':3, 'title': 'Vitals/Exam', 'active': False },
		{ 'link': 'labs', 'ord':4, 'title': 'Labs', 'active': False },
		{ 'link': 'plan', 'ord':5, 'title': 'Assessment/Plan', 'active': False },
		{ 'link': 'meds', 'ord':6, 'title': 'Meds', 'active': False },
		{ 'link': 'refe', 'ord':8, 'title': 'Referrals', 'active': False },
		{ 'link': 'note', 'ord':10, 'title': 'Notes', 'active': False, 'hilite': False },
		]
	for i in range(0,len(menu)):
		if menu[i]['link']==current:
			menu[i]['active']=True
	if patient.scratchNote:
		for i in range(0,len(menu)):
			if menu[i]['link']=='note':
				menu[i]['hilite']=True
	return menu
@login_required
def visit(request,id):
	"""
	"""
	return HttpResponseRedirect('/visit/%s/past/'%(id))

@login_required
def visit_claim(request,id):
	"""
	"""
	from ocemr.models import Visit, Diagnosis

	v = Visit.objects.get(pk=id)
	v.status = 'INPR'
	from datetime import datetime
	v.claimedBy = request.user
	v.claimedDateTime = datetime.now()
	v.save()
	
	p = v.patient

	try:
		old_v = Visit.objects.filter(patient=p).filter(status='RESO').order_by('-finishedDateTime')[0]
	except:
		old_v = None
	if old_v != None:
		old_diags = Diagnosis.objects.filter(visit=old_v).exclude(status='RES')
		for old_diag in old_diags:
			try: # Check for existing Diagnosis in this record
				d = Diagnosis.objects.get(type=old_diag.type, patient=p, visit=v)
			except: 
				d = None
			if d == None: # Create the record.
				d, is_new = Diagnosis.objects.get_or_create(type=old_diag.type, patient=p, visit=v, diagnosedBy=request.user)
				if is_new:
					d.save()
				
		
	return render(request, 'close_window.html', {})

@login_required
def visit_unclaim(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	v.status = 'WAIT'
	v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_finish(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if v.status == 'INPR':
		v.status = 'CHOT'
	else:
		v.status = 'MISS'
	from datetime import datetime
	v.finishedBy = request.user
	v.finishedDateTime = datetime.now()
	v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_unfinish(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if v.status == 'MISS':
		from datetime import datetime
		v.seenDateTime = datetime.now()
		v.status = 'WAIT'
	else:
		v.status = 'INPR'
	v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_seen(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if v.status == 'SCHE':
		v.status = 'WAIT'
	from datetime import datetime
	v.seenDateTime = datetime.now()
	v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_unseen(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if v.status == 'WAIT':
		v.status = 'SCHE'
	v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_past(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('past', p)

	
	return render(request, 'visit_past.html', locals())

@login_required
def visit_subj(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit, SymptomType, VisitSymptom

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('subj',p)

	symptomTypes = SymptomType.objects.all()
	symptoms = VisitSymptom.objects.filter(visit=v)

	return render(request, 'visit_subj.html', locals())

@login_required
def visit_subj_new(request,id, symptomtypeid):
	"""
	"""
	from ocemr.models import SymptomType
	from ocemr.forms import NewVisitSymptomForm
	vid=int(id)
	stid=int(symptomtypeid)
	st=SymptomType.objects.get(pk=stid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewVisitSymptomForm(vid, stid, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewVisitSymptomForm(vid, stid) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Add a Symptom: %s'%(st.title),
		'form_action': '/visit/%d/subj/new/%d/'%(vid,stid),
		'form': form,
	})

@login_required
def visit_subj_edit(request,id, visitsymptomid):
	"""
	"""
	from ocemr.models import VisitSymptom
	from ocemr.forms import EditVisitSymptomForm
	vs = VisitSymptom.objects.get(pk=visitsymptomid)
	
	if request.method == 'POST': 
		form = EditVisitSymptomForm(request.POST)
		if form.is_valid():
			vs.notes = form.cleaned_data['notes']
			vs.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditVisitSymptomForm(initial={'notes': vs.notes})
	return render(request, 'popup_form.html', {
		'title': 'Edit Symptom Notes: %s'%(vs.type.title),
		'form_action': '/visit/%s/subj/edit/%s/'%(id,visitsymptomid),
		'form': form,
	})

@login_required
def visit_subj_delete(request,id, visitsymptomid):
	"""
	"""
	from ocemr.models import VisitSymptom
	o = VisitSymptom.objects.get(pk=visitsymptomid)

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
		'title': 'Delete Symptom: %s'%(o.type.title),
		'form_action': '/visit/%s/subj/delete/%s/'%(id,visitsymptomid),
		'form': form,
	})

	

@login_required
def visit_obje(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit, VitalType, Vital
	from ocemr.models import ExamNoteType, ExamNote

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('obje',p)

	vitalTypes = VitalType.objects.all()
	vital_times_in = Vital.objects.filter(visit=v).values('observedDateTime').distinct()
	vital_times = []
	for vt in vital_times_in:
		vitals = Vital.objects.filter(visit=v, observedDateTime=vt['observedDateTime'])
		vital_times.append( [ vt['observedDateTime'], vitals ] )
	#vitals = Vital.objects.filter(visit=v)

	examNoteTypes = ExamNoteType.objects.all()
	examNotes = ExamNote.objects.filter(visit=v)

	return render(request, 'visit_obje.html', locals())

@login_required
def visit_obje_vitals_new(request,id):
	"""
	"""
	from ocemr.models import Vital, VitalType, Visit
	from ocemr.forms import NewVitalsForm
	vid=int(id)
	v=Visit.objects.get(pk=vid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewVitalsForm(v, request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			#form.cleaned_data['']
			p = form.cleaned_data['patient']
			vis = form.cleaned_data['visit']
			dt = form.cleaned_data['observedDateTime']
			u = form.cleaned_data['observedBy']
			# Temp
			data = form.cleaned_data['temp_in']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='Temp')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#
			data = form.cleaned_data['bloodPressureSystolic']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='BP - Systolic')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#
			data = form.cleaned_data['bloodPressureDiastolic']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='BP - Diastolic')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#
			data = form.cleaned_data['heartRate']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='HR')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#
			data = form.cleaned_data['respiratoryRate']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='RR')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#
			data = form.cleaned_data['height_in']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='Height')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#
			data = form.cleaned_data['weight_in']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='Weight')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()
			#SpO2
			data = form.cleaned_data['spo2_in']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='SpO2')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			#Oxygen
			data = form.cleaned_data['oxygen_in']
			if not ( data == None or data == ''):
				vt = VitalType.objects.get(title='Oxygen')
				v = Vital(
					type=vt,patient=p, visit=vis,
					observedDateTime=dt, observedBy=u,
					data=data)
				v.save()

			return HttpResponseRedirect('/close_window/')
	else:
		form = NewVitalsForm(v, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Add Vitals',
		'form_action': '/visit/%d/obje/vitals/new/'%(vid),
		'form': form,
	})

@login_required
def visit_obje_vital_delete(request,id, oid):
	"""
	"""
	from ocemr.models import Vital
	o = Vital.objects.get(pk=oid)

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
		'title': 'Delete Vital: %s'%(o),
		'form_action': '/visit/%s/obje/vital/delete/%s/'%(id,oid),
		'form': form,
	})

	
@login_required
def visit_obje_examNote_new(request,id, examnotetypeid):
	"""
	"""
	from ocemr.models import ExamNoteType, Visit
	from ocemr.forms import NewExamNoteForm
	vid=int(id)
	entid=int(examnotetypeid)
	v=Visit.objects.get(pk=vid)
	ent=ExamNoteType.objects.get(pk=entid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewExamNoteForm(v, ent, request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewExamNoteForm(v, ent, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Add an Exam Note: %s'%(ent.title),
		'form_action': '/visit/%d/obje/examNote/new/%d/'%(vid,entid),
		'form': form,
	})

@login_required
def visit_obje_examNote_edit(request,id, examnoteid):
	"""
	"""
	from ocemr.models import ExamNote
	from ocemr.forms import EditExamNoteForm
	en = ExamNote.objects.get(pk=examnoteid)
	
	if request.method == 'POST': 
		form = EditExamNoteForm(request.POST)
		if form.is_valid():
			en.note = form.cleaned_data['note']
			en.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditExamNoteForm(initial={'note': en.note})
	return render(request, 'popup_form.html', {
		'title': 'Edit Exam Note: %s'%(en.type.title),
		'form_action': '/visit/%s/obje/examNote/edit/%s/'%(id,examnoteid),
		'form': form,
	})


@login_required
def visit_labs(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit, LabType, Lab

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('labs',p)

	labTypes = LabType.objects.all()
	labs = Lab.objects.filter(visit=v)
	
	return render(request, 'visit_labs.html', locals())

@login_required
def visit_labs_new(request,id, labtypeid):
	"""
	"""
	from ocemr.models import LabType, Visit, Lab
	vid=int(id)
	ltid=int(labtypeid)
	v = Visit.objects.get(pk=vid)
	lt=LabType.objects.get(pk=ltid)

	l = Lab(type=lt, patient=v.patient, visit=v, orderedBy=request.user, status='ORD')
	l.save()
	return HttpResponseRedirect('/close_window/')

@login_required
def visit_plan(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('plan',p)

	return render(request, 'visit_plan.html', locals())

@login_required
def visit_plan_diag_new(request,id):
        """
        """
	from ocemr.models import Visit
	from ocemr.forms import NewDiagnosisForm

	v = Visit.objects.get(pk=id)

	p = v.patient

        if request.method == 'POST':
                form = NewDiagnosisForm(v, request.user, request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass
                        o = form.save()
                        return HttpResponseRedirect('/close_window/')
        else:  
                form = NewDiagnosisForm(v, request.user) # An unbound form

	return render(request, 'popup_form.html', {
                'title': 'Add a Diagnosis for %s'%(p),
                'form_action': '/visit/%d/plan/diag/new/'%(v.id),
                'form': form,
        })

@login_required
def visit_plan_diag_new_bytype(request, id, dtid):
	from ocemr.models import Visit, DiagnosisType, Diagnosis

	v = Visit.objects.get(pk=id)

	p = v.patient

	dt = DiagnosisType.objects.get(pk=dtid)

	d = Diagnosis(type=dt, patient=p, visit=v, status='NEW')

	d.save()

        return HttpResponseRedirect('/close_window/')


@login_required
def visit_meds(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit, Diagnosis

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('meds',p)
	q_status = Q( status='NEW' ) | Q( status='FOL' )
	diagnoses = Diagnosis.objects.filter(visit=v).filter(q_status)


	return render(request, 'visit_meds.html', locals())

@login_required
def visit_meds_new(request,id,did):
        """
        """
	from ocemr.models import Diagnosis
	from ocemr.forms import NewMedForm

	did = int(did)
	d = Diagnosis.objects.get(pk=did)

        if request.method == 'POST':
                form = NewMedForm(d, request.user, request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass
                        o = form.save()
                        return HttpResponseRedirect('/close_window/')
        else:  
                form = NewMedForm(d, request.user) # An unbound form

	return render(request, 'popup_form.html', {
                'title': 'Add a Med for %s - %s'%(d.patient,d.type.title),
                'form_action': '/visit/%d/meds/new/%d/'%(d.visit.id,did),
                'form': form,
        })

@login_required
def visit_refe(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit, Referral

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('refe',p)

	referrals = Referral.objects.filter(patient=p).order_by('-addedDateTime')

	return render(request, 'visit_refe.html', locals())

@login_required
def visit_refe_new(request,id):
	"""
	"""
	from ocemr.models import Visit, Referral
	from ocemr.forms import NewReferralForm
	vid=int(id)
	v=Visit.objects.get(pk=vid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewReferralForm(v, request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewReferralForm(v, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Add a Referral',
		'form_action': '/visit/%d/refe/new/'%(vid),
		'form': form,
	})

@login_required
def visit_refe_edit(request,id, refid):
	"""
	"""
	from ocemr.models import Referral
	from ocemr.forms import EditReferralForm
	r = Referral.objects.get(pk=refid)
	
	if request.method == 'POST': 
		form = EditReferralForm(request.POST)
		if form.is_valid():
			r.to = form.cleaned_data['to']
			r.reason = form.cleaned_data['reason']
			r.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditReferralForm(initial={'to':r.to, 'reason': r.reason})
	return render(request, 'popup_form.html', {
		'title': 'Edit Referral: %s'%(r),
		'form_action': '/visit/%s/refe/edit/%s/'%(id,refid),
		'form': form,
	})


@login_required
def visit_note(request,id):
	"""
	Visit 
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	p = v.patient
	menu = get_visit_menu('note',p)
	return render(request, 'visit_note.html', locals())

@login_required
def visit_allergy_new(request,id):
	"""
	"""
	from ocemr.models import Visit, Allergy
	from ocemr.forms import NewAllergyForm
	vid=int(id)
	v=Visit.objects.get(pk=vid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewAllergyForm(v, request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewAllergyForm(v, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Add an Allergy',
		'form_action': '/visit/%d/allergy/new/'%(vid),
		'form': form,
	})

@login_required
def visit_allergy_delete(request,id, oid):
	"""
	"""
	from ocemr.models import Allergy
	o = Allergy.objects.get(pk=oid)

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
		'title': 'Delete Allergy: %s'%(o.to),
		'form_action': '/visit/%s/allergy/delete/%s/'%(id,oid),
		'form': form,
	})

@login_required
def visit_collect(request,id):
	"""
	"""
	from ocemr.models import Visit
	from ocemr.forms import NewCashLogForm
	vid=int(id)
	v=Visit.objects.get(pk=vid)

	if request.method == 'POST': # If the form has been submitted...
		form = NewCashLogForm(v, request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			o = form.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = NewCashLogForm(v, request.user) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Collect',
		'form_action': '/visit/%d/collect/'%(vid),
		'form': form,
	})
	

@login_required
def visit_cost_estimate_detail(request,id):
	from ocemr.models import Visit
	vid=int(id)
	v=Visit.objects.get(pk=vid)
	table="<TR><TH>Title<TH>Base Cost<TH>Quantity<TH>Total</TR>"
	ced = v.get_estimated_visit_cost_detail()
	for row in ced:
		table+="<TR><TD>%s<TD>%s<TD>%s<TD>%s</TR>"%(
			row[0], row[1], row[2], row[3] )
	table+="<TR><TD COLSPAN=3>TOTAL<TD>%s</TR>"%(
		v.get_estimated_visit_cost() )
	return render(request, 'popup_table.html', {
		'title': 'Estimated Visit Cost Detail',
		'table': table,
	})

@login_required
def visit_bill_amount(request,id):
	"""
	"""
	from ocemr.models import Visit
	from ocemr.forms import EditBillAmountForm
	vid=int(id)
	v=Visit.objects.get(pk=vid)

	if request.method == 'POST': # If the form has been submitted...
		form = EditBillAmountForm(v.cost, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			v.cost=form.cleaned_data['amount']
			v.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditBillAmountForm(v.cost) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Bill Amount',
		'form_action': '/visit/%d/bill_amount/'%(vid),
		'form': form,
	})
	

@login_required
def visit_resolve(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if v.status == 'CHOT':
		v.status = 'RESO'
		from datetime import datetime
		v.resolvedBy = request.user
		v.resolvedDateTime = datetime.now()
		v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_unresolve(request,id):
	"""
	"""
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
	if v.status == 'RESO':
		v.status = 'CHOT'
		v.save()
	return render(request, 'close_window.html', {})

@login_required
def visit_record(request, id, type):
	"""
	['enscript', '-P', 'p1102w', '--header=Engeye Health Clinic', '--footer=Page $% of $=', '--word-wrap', '--mark-wrapped-lines=arrow', '/etc/motd']
	"""

	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)

	# TODO: Make this header Configurable!
	head_text = """\t\t\t\tEngeye Health Clinic - Ddegeya-Masaka
\t\t\t\tP.O. Box 26592, Kampala\t\t0772-556105\t\twww.engeye.org

\t\tBino bye bikwata ku kujjanjabibwa kwo funnye leero

"""
	if v.finishedDateTime:
		d = v.finishedDateTime
	else:
		d = v.seenDateTime
	head_text += "\tPatient: %s\tVisit# %05d\tDate: %02d-%02d-%02d\n"%(
		v.patient,v.id,
		d.day, d.month, d.year)
	allergy_list = []
	for a in v.patient.get_allergies():
		 allergy_list.append(a.to)
	if len(allergy_list) > 0:
		head_text += "\t\tAllergies: %s\n"%(", ".join(allergy_list))
	summ_text = v.get_summary_text()
	next_visits = Visit.objects.filter(patient=v.patient,scheduledDate__gt=v.scheduledDate)
	upco_text=""
	if len(next_visits) > 0:
		upco_text = "\n\n\t\tKomawo Kudwaliro nga:\n"
		for uv in next_visits:
			upco_text += "\t%02d-%02d-%02d - %s:%s\n"%(
				uv.scheduledDate.day,
				uv.scheduledDate.month,
				uv.scheduledDate.year,
				uv.displayReason,
				uv.reasonDetail,
			)
		

	text_out = head_text + summ_text + upco_text

	if type == "print":
		from subprocess import Popen, PIPE
		from ocemr.settings import PRINTER_NAME, PAPER_SIZE
		cmd = " ".join( ('enscript', '-P', PRINTER_NAME, '--word-wrap', '--mark-wrapped-lines=arrow', '--font=Times-Roman12', '--header=', '--media='+PAPER_SIZE) )
		p = Popen(cmd, shell=True, bufsize=0,
			stdin=PIPE, stdout=PIPE, close_fds=True)
		(child_stdin, child_stdout) = (p.stdin, p.stdout)
		child_stdin.write(text_out.encode( "utf-8" ))
		out,err=p.communicate()
		return render(request, 'close_window.html', {})
	else:
		lines = text_out.replace('\t','&nbsp;&nbsp;&nbsp;').replace('\n','<BR>')
		return render(request, 'popup_lines.html', {'lines': lines, 'link_text': """<a href="#" onclick="window.print();return false;">Print</a>"""})
