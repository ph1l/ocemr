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
	p = v.patient

	return render_to_response('meds_view.html',locals())

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
        return render_to_response('close_window.html', {})

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
        return render_to_response('close_window.html', {})

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
        return render_to_response('close_window.html', {})

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
        return render_to_response('close_window.html', {})

#@login_required
#def med_(request,id):
#        """
#        """
#        from ocemr.models import Med
#
#        m = Med.objects.get(pk=id)
#        m.status = ''
#        m.save()
#        return render_to_response('close_window.html', {})

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
        return render_to_response('popup_form.html', {
                'title': 'Add a Med Note: %s'%(m.type.title),
                'form_action': '/med/%d/notate/'%(m.id),
                'form': form,
        })

