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
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from ocemr.forms import *
from ocemr.models import Patient, VacType, VacNote, Vac

@login_required
def vac_del(request,pid, vtid):
        """
        """

        p = Patient.objects.get(pk=pid)
        vt = VacType.objects.get(pk=vtid)
	vacs = Vac.objects.filter(patient=p, type=vt)
	for v in vacs:
		v.delete()
	#vn = VacNote( vac=v, addedBy=request.user, note="Canceled" )
	#vn.save()
        return render_to_response('close_window.html', {})

@login_required
def vac_notate(request, pid, vtid):
        """
        """

        p = Patient.objects.get(pk=pid)
        vt = VacType.objects.get(pk=vtid)

        if request.method == 'POST': # If the form has been submitted...
                form = NewVacNoteForm(p, vt, request.user, request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass
                        o = form.save()
                        return HttpResponseRedirect('/close_window/')
        else:
                form = NewVacNoteForm(p, vt, request.user) # An unbound form
        return render_to_response('popup_form.html', {
                'title': 'Add a Vac Note: %s'%(vt.title),
                'form_action': '/vac/notate/%d/%d/'%(p.id,vt.id),
                'form': form,
        },context_instance=RequestContext(request))

@login_required
def vac_new(request,pid,vtid):
        """
        """
	from ocemr.models import VacType, Patient
	from ocemr.forms import NewVacForm

        pid = int(pid)
        vtid = int(vtid)
        p = Patient.objects.get(pk=pid)
        vact = VacType.objects.get(pk=vtid)

        if request.method == 'POST':
                form = NewVacForm(p, vact, request.user, request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass
                        o = form.save()
                        return HttpResponseRedirect('/close_window/')
        else:
                form = NewVacForm(p, vact, request.user) # An unbound form

        return render_to_response('popup_form.html', {
                'title': 'Add a Vac ',
                'form_action': '/vac/new/%d/%d/'%(pid,vtid),
                'form': form,
        },context_instance=RequestContext(request))

@login_required
def vac_edit_received(request,vid):
	from ocemr.models import Vac

	v = Vac.objects.get(pk=vid)
	if request.method == 'POST': # If the form has been submitted...
		form = EditVacReceivedForm(v,request.user, request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			v.receivedDate = form.cleaned_data['receivedDate']
			v.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = EditVacReceivedForm(v, request.user) # An unbound form
	return render_to_response('popup_form.html', {
		'title': 'Edit Vaccination Received Date',
		'form_action': '/vac/edit_received/%s/'%(vid),
		'form': form,
	},context_instance=RequestContext(request))

@login_required
def edit_visit_seen(request, id):
	from django.utils import formats
	from ocemr.models import Visit

	v = Visit.objects.get(pk=id)
