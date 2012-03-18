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

from django.db.models import get_model, Q

@login_required
def vac_cancel(request,id):
        """
        """
        from ocemr.models import Vac, VacNote

        v = Vac.objects.get(pk=id)
        v.status = 'CAN'
        v.save()
	vn = VacNote( vac=v, addedBy=request.user, note="Canceled" )
	vn.save()
        return render_to_response('close_window.html', {})

@login_required
def vac_undo_cancel(request,id):
        """
        """
        from ocemr.models import Vac, VacNote

        v = Vac.objects.get(pk=id)
        v.status = 'COM'
        v.save()
	vn = VacNote( vac=v, addedBy=request.user, note="Undo Cancel" )
	vn.save()
        return render_to_response('close_window.html', {})

@login_required
def vac_notate(request, id):
        """
        """
        from ocemr.models import VacNote, Vac, Visit
        from ocemr.forms import NewVacNoteForm

        vacid=int(id)
        v=Vac.objects.get(pk=vacid)

        if request.method == 'POST': # If the form has been submitted...
                form = NewVacNoteForm(v, request.user, request.POST) # A form bound to the POST data
                if form.is_valid(): # All validation rules pass
                        o = form.save()
                        return HttpResponseRedirect('/close_window/')
        else:
                form = NewVacNoteForm(v, request.user) # An unbound form
        return render_to_response('popup_form.html', {
                'title': 'Add a Vac Note: %s'%(v.type.title),
                'form_action': '/vac/%d/notate/'%(v.id),
                'form': form,
        },context_instance=RequestContext(request))
