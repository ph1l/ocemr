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
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest

from django.db.models import Q

from ocemr.views.visit import get_visit_menu


@login_required
def pregnancy(request, id):
    """
        Pregnancy Index
        """
    from ocemr.models import Visit, Patient, Pregnancy

    v = Visit.objects.get(pk=id)
    p = Patient.objects.get(pk=v.patient.id)
    pregnancy = Pregnancy.objects.filter(patient=p).order_by('deliveryDate')
    menu = get_visit_menu('preg', p)
    return render(request, 'visit_preg.html', {
        'menu': menu,
        'p': p,
        'pregnancy': pregnancy,
        'v': v,
    })


@login_required
def pregnancy_new(request, id):
    """
	"""
    from ocemr.models import Visit, Patient, Pregnancy
    from ocemr.forms import NewPregnancyForm
    vid = int(id)
    v = Visit.objects.get(pk=vid)
    p = Patient.objects.get(pk=v.patient.id)

    if request.method == 'POST':  # If the form has been submitted...
        form = NewPregnancyForm(p, request.user,
                                request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            pr = Pregnancy(
                patient=form.cleaned_data['patient'],
                deliveryDate=form.cleaned_data['deliveryDate'],
                gestationalAge=form.cleaned_data['gestationalAge'],
                gestationalAgePlusDays=form.
                cleaned_data['gestationalAgePlusDays'],
                deliveryMode=form.cleaned_data['deliveryMode'],
                gender=form.cleaned_data['gender'],
                presentation=form.cleaned_data['presentation'],
                laborLength=form.cleaned_data['laborLength'],
                complications=form.cleaned_data['complications'],
                referral=form.cleaned_data['referral'],
                referralOutcome=form.cleaned_data['referralOutcome'],
                postpartumFollowUp=form.cleaned_data['postpartumFollowUp'],
                postpartumComplications=form.
                cleaned_data['postpartumComplications'],
                breastfeedingProblems=form.
                cleaned_data['breastfeedingProblems'],
                pmtct=form.cleaned_data['pmtct'],
                tetanusBoosterDate=form.cleaned_data['tetanusBoosterDate'],
                addedDateTime=form.cleaned_data['addedDateTime'],
                addedBy=form.cleaned_data['addedBy']).save()
            return HttpResponseRedirect('/close_window/')
    else:
        form = NewPregnancyForm(p, request.user)  # An unbound form
    return render(
        request, 'popup_form.html', {
            'title': 'Add Pregnancy',
            'form_action': '/visit/%s/preg/new/' % (id),
            'form': form,
        })


@login_required
def pregnancy_edit(request, id, pregid):
    """
	"""
    from ocemr.models import Visit, Patient, Pregnancy
    from ocemr.forms import NewPregnancyForm
    v = Visit.objects.get(pk=int(id))
    patient_id = v.patient.id
    p = Patient.objects.get(pk=patient_id)
    pr = Pregnancy.objects.get(pk=int(pregid))

    if request.method == 'POST':  # If the form has been submitted...
        form = NewPregnancyForm(p, request.user,
                                request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            pr.patient = form.cleaned_data['patient']
            pr.deliveryDate = form.cleaned_data['deliveryDate']
            pr.gestationalAge = form.cleaned_data['gestationalAge']
            pr.gestationalAgePlusDays = form.cleaned_data[
                'gestationalAgePlusDays']
            pr.deliveryMode = form.cleaned_data['deliveryMode']
            pr.gender = form.cleaned_data['gender']
            pr.presentation = form.cleaned_data['presentation']
            pr.laborLength = form.cleaned_data['laborLength']
            pr.complications = form.cleaned_data['complications']
            pr.referral = form.cleaned_data['referral']
            pr.referralOutcome = form.cleaned_data['referralOutcome']
            pr.postpartumFollowUp = form.cleaned_data['postpartumFollowUp']
            pr.postpartumComplications = form.cleaned_data[
                'postpartumComplications']
            pr.breastfeedingProblems = form.cleaned_data[
                'breastfeedingProblems']
            pr.pmtct = form.cleaned_data['pmtct']
            pr.tetanusBoosterDate = form.cleaned_data['tetanusBoosterDate']
            pr.addedDateTime = form.cleaned_data['addedDateTime']
            pr.addedBy = form.cleaned_data['addedBy']
            pr.save()
            return HttpResponseRedirect('/close_window/')
    else:
        form = NewPregnancyForm(
            p,
            request.user,
            initial={
                'patient': p,
                'deliveryDate': pr.deliveryDate,
                'gestationalAge': pr.gestationalAge,
                'gestationalAgePlusDays': pr.gestationalAgePlusDays,
                'gender': pr.gender,
                'presentation': pr.presentation,
                'laborLength': pr.laborLength,
                'complications': pr.complications,
                'referral': pr.referral,
                'referralOutcome': pr.referralOutcome,
                'postpartumFollowUp': pr.postpartumFollowUp,
                'postpartumComplications': pr.postpartumComplications,
                'breastfeedingProblems': pr.breastfeedingProblems,
                'pmtct': pr.pmtct,
                'tetanusBoosterDate': pr.tetanusBoosterDate,
                'addedDateTime': pr.addedDateTime,
                'addedBy': pr.addedBy,
            })  # An unbound form
    return render(
        request, 'popup_form.html', {
            'title': 'Edit Pregnancy',
            'form_action': '/visit/%s/preg/edit/%s/' % (id, pregid),
            'form': form,
        })
