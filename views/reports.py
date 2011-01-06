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
from django.db.models import get_model, Q
from datetime import datetime

def dump_csv(filename,field_names,headers,data_rows):
	"""
	return dump_csv(
		"filename.csv",
		["field_one","field_two"],
		{'field_one': "Field One", 'field_two': "Field Two"},
		(
		{'field_one': "data r1c1", 'field_two': "data r1c2"},
		{'field_one': "data r2c1", 'field_two': "data r2c2"},
		...
		)
	) 
	dump_csv - given a set of data provide a csv file for download
	"""
        out=[]
        row=[]
        for field in field_names:
                row.append(headers[field])
        out.append(row)
        for data_row in data_rows:
                row=[]
                for field in field_names:
                        if data_row.has_key(field):
                                row.append(data_row[field])
                        else:
                                row.append(None)
                out.append(row)

        import csv, StringIO
	from django.core.servers.basehttp import FileWrapper

        temp=StringIO.StringIO()
        out_writer = csv.writer(temp,dialect='excel')
        out_writer.writerows(out)

        response = HttpResponse(temp.getvalue(),content_type='text/csv')
        response['Content-Length'] = len(temp.getvalue())
	temp.close()
        response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
        return response

@login_required
def index(request):
        """
        Reports Landing Page
        """
        return render_to_response('reports.html',context_instance=RequestContext(request))

@login_required
def legacy_patient_daily(request):
	"""
	"""
	from ocemr.forms import SelectDateForm

	form_valid=0
        if request.method == 'POST':
                form = SelectDateForm(request.POST)
                if form.is_valid():
                        date_in = form.cleaned_data['date']
			form_valid=1
        else:
                form = SelectDateForm()
	if not form_valid:
	        return render_to_response('popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/legacy/patient/daily/',
	                'form': form,
	        })


	from ocemr.models import Visit, Diagnosis, Med, Referral
	field_names=[
		'pt_daily_index',
		'pt_name',
		'pt_monthly_index',
		'sex',
		'age',
		'village',
		'diagnosis',
		'prescription',
		'referral'
			]
	headers={
		'pt_daily_index': 'Pt # of Day',
		'pt_name': 'Patient Name',
		'pt_monthly_index': 'Pt # of Month',
		'sex': 'Sex',
		'age': 'Age',
		'village': 'Village',
		'diagnosis': 'Diagnosis',
		'prescription': 'Prescription',
		'referral': 'Referral',
	}
	data_rows = []
	d_today = date_in
	q_this_month = (Q(scheduledDate__month=d_today.month) & Q(scheduledDate__lt=d_today)) & (Q(status="CHOT") | Q(status="RESO"))
	q_this_day = Q(scheduledDate=d_today) & (Q(status="CHOT") | Q(status="RESO"))
	months_visits = Visit.objects.filter(q_this_month)
	pt_monthly_index = len(months_visits)
	days_visits = Visit.objects.filter(q_this_day)
	q_dignosis_active = (Q(status="NEW") | Q(status="FOL"))
	daily_index=0	
	summary_rows=[]
	for v in days_visits:
		daily_index += 1
		pt_monthly_index += 1
		referral = ""
		for r in Referral.objects.filter(visit=v):
			referral += "%s - %s; "%(r.to,r.reason)
		summary_rows.append( {
			'pt_daily_index': daily_index, 
			'pt_name': v.patient.fullName,
			'pt_monthly_index': pt_monthly_index,
			'sex': v.patient.gender,
			'age': v.patient.age,
			'village': v.patient.village.name,
			'diagnosis': '',
			'prescription': '',
			'referral': referral,
		})
		for d in Diagnosis.objects.filter(visit=v).filter(q_dignosis_active):
			diagnosis = d.type.title
			summary_rows.append( {
				'pt_daily_index': '', 
				'pt_name': '',
				'pt_monthly_index': '',
				'sex': '',
				'age': '',
				'village': '',
				'diagnosis': diagnosis,
				'prescription': '',
				'referral': '',
			})
			for m in Med.objects.filter(diagnosis=d,status='DIS'):
				prescription = m.type.title
				summary_rows.append( {
					'pt_daily_index': '', 
					'pt_name': '',
					'pt_monthly_index': '',
					'sex': '',
					'age': '',
					'village': '',
					'diagnosis': diagnosis,
					'prescription': prescription,
					'referral': '',
				})
	return dump_csv( "patient-daily-%s.csv"%(date_in.strftime("%Y%m%d")), field_names, headers, summary_rows )

