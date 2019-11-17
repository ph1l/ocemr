
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


#from django.db.models import get_model, Q


@login_required
def diag_stat_change(request,id,newstat):
	"""
	"""
	from ocemr.models import Diagnosis

	d = Diagnosis.objects.get(pk=id)
	valid_statuses = []
	for s in d.DIAGNOSIS_STATUS_CHOICES:
		valid_statuses.append(s[0])
	if newstat in valid_statuses:
		d.status = newstat
		d.save()
	return render(request, 'close_window.html', {})

@login_required
def diag_patienttypehistory(request,pid,dtid):
	"""
	"""
	from ocemr.models import Diagnosis, DiagnosisType, Patient

	dtid=int(dtid)
	pid=int(pid)
	p = Patient.objects.get(pk=pid)
	dt = DiagnosisType.objects.get(pk=dtid)
	diags = Diagnosis.objects.filter(patient=p,type=dt)
	return render(request, 'diag_view.html', locals())

@login_required
def diag_history(request,id):
	"""
	"""
	from ocemr.models import Diagnosis

	d = Diagnosis.objects.get(pk=id)
	dt = d.type
	diags = Diagnosis.objects.filter(patient=d.patient,type=d.type)
	return render(request, 'diag_view.html', locals())

@login_required
def diag_edit_notes(request, id):
	"""
	"""
	from ocemr.models import Diagnosis
	from ocemr.forms import EditDiagnosisNotesForm

	diagid=int(id)
	d=Diagnosis.objects.get(pk=diagid)

	if request.method == 'POST': # If the form has been submitted...
		form = EditDiagnosisNotesForm(d, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			from datetime import datetime
			d.notes = form.cleaned_data['notes']
			d.addedBy = request.user
			d.addedDateTime = datetime.now()
			d.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditDiagnosisNotesForm(d) # An unbound form
	return render(request, 'popup_form.html', {
		'title': 'Edit Diagnosis Notes: %s'%(d.type.title),
		'form_action': '/diag/%d/edit/notes/'%(d.id),
		'form': form,
		})

@login_required
def diag_delete(request,id):
        """
        """
        from ocemr.models import Diagnosis
        o = Diagnosis.objects.get(pk=id)

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
                'title': 'Delete Diagnosis: %s'%(o),
                'form_action': '/diag/%s/delete/'%(id),
                'form': form,
        })

