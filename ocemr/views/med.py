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
from ocemr.forms import *

from django.db.models import Q

@login_required
def med_queue(request):
	"""
	"""
	from datetime import datetime, timedelta
        d_today = datetime.today().date()
        dt_start = datetime(d_today.year,d_today.month,d_today.day,0,0,0)
        dt_end = datetime(d_today.year,d_today.month,d_today.day,23,59,59)

	q_active = Q(status='CHOT')
	q_inactive = ( Q( resolvedDateTime__gte=dt_start ) & Q( resolvedDateTime__lte=dt_end ) ) & Q(status='RESO')

	from ocemr.models import Visit
	visits_active = Visit.objects.filter(q_active).order_by('finishedDateTime')
	visits_inactive = Visit.objects.filter(q_inactive).order_by('-resolvedDateTime')
	return render(request, 'med_queue.html', locals())

@login_required
def meds_view(request,vid):
	"""
	"""
	from ocemr.models import Visit

	vid = int(vid)
	v = Visit.objects.get(pk=vid)
	p = v.patient

	return render(request, 'meds_view.html',locals())

@login_required
def med_dispense(request,id):
        """
        """
        from ocemr.models import Med, MedNote

        m = Med.objects.get(pk=id)
        m.status = 'DIS'
        m.save()
	mn = MedNote( med=m, addedBy=request.user, note="Dispensed" )
	mn.save()
        return render(request, 'close_window.html', {})

@login_required
def med_substitute(request,id):
        """
        """
        from ocemr.models import Med, MedNote

        m = Med.objects.get(pk=id)
        m.status = 'SUB'
        m.save()
	mn = MedNote( med=m, addedBy=request.user, note="Substituted" )
	mn.save()
	return HttpResponseRedirect('/visit/%s/meds/new/%s/'%(m.visit.id, m.diagnosis.id))

@login_required
def med_cancel(request,id):
        """
        """
        from ocemr.models import Med, MedNote

        m = Med.objects.get(pk=id)
        m.status = 'CAN'
        m.save()
	mn = MedNote( med=m, addedBy=request.user, note="Canceled" )
	mn.save()
        return render(request, 'close_window.html', {})

@login_required
def med_undo_dispense(request,id):
        """
        """
        from ocemr.models import Med, MedNote

        m = Med.objects.get(pk=id)
        m.status = 'ORD'
        m.save()
	mn = MedNote( med=m, addedBy=request.user, note="Undo Dispense" )
	mn.save()
        return render(request, 'close_window.html', {})

@login_required
def med_undo_cancel(request,id):
        """
        """
        from ocemr.models import Med, MedNote

        m = Med.objects.get(pk=id)
        m.status = 'ORD'
        m.save()
	mn = MedNote( med=m, addedBy=request.user, note="Undo Cancel" )
	mn.save()
        return render(request, 'close_window.html', {})

@login_required
def med_notate(request, id):
        """
        """
        from ocemr.models import MedNote, Med, Visit
        from ocemr.forms import NewMedNoteForm

        medid=int(id)
        m=Med.objects.get(pk=medid)

        if request.method == 'POST': # If the form has been submitted...
                form = NewMedNoteForm(m, request.user, request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass
                        o = form.save()
                        return HttpResponseRedirect('/close_window/')
        else:
                form = NewMedNoteForm(m, request.user) # An unbound form
        return render(request, 'popup_form.html', {
                'title': 'Add a Med Note: %s'%(m.type.title),
                'form_action': '/med/%d/notate/'%(m.id),
                'form': form,
        })

@login_required
def med_edit(request,id):
	"""
	"""
	from ocemr.models import Med
	from ocemr.forms import EditMedForm
	m = Med.objects.get(pk=id)
	
	if request.user != m.addedBy:
		return render(request, 'popup_info.html', {
			'title': 'Error',
			'info': 'You cannot edit This Med, cancel it and re-add instead.',
			})
	if request.method == 'POST': 
		form = EditMedForm(request.POST)
		if form.is_valid():
			m.type = form.cleaned_data['type']
			m.dosage = form.cleaned_data['dosage']
			if form.cleaned_data['dispenseAmount']:
				m.dispenseAmount = form.cleaned_data['dispenseAmount']
			m.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditMedForm(initial={'type': m.type.title, 'dosage': m.dosage, 'dispenseAmount':m.dispenseAmount})
	return render(request, 'popup_form.html', {
		'title': 'Edit Med',
		'form_action': '/med/%s/edit/'%(id),
		'form': form,
	})

