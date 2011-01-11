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
from datetime import datetime, timedelta

def dump_table(field_names,headers,data_rows):
	"""
	"""
	out_txt="<TABLE>\n"
	out_txt += "<TR>"
	for f in field_names:
		out_txt += "<TH>" + f
	out_txt += "</TR>\n"
	for r in data_rows:
		out_txt += "<TR>"
		for f in field_names:
			out_txt += "<TD>%s</TD>"%r[f]
		out_txt += "</TR>\n"
	out_txt += "</TABLE>\n"

	return render_to_response('popup_table.html', {'table': out_txt})
	
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
	if headers:
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
def clinician_daily(request):
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
	                'form_action': '/reports/clinician/daily/',
	                'form': form,
	        })
	from ocemr.models import Visit, Diagnosis, Med, Referral
	field_names=[
		'clinician',
		'num_patients_day',
		'num_patients_month',
		]
	headers={
		'clinician': 'Clinician',
		'num_patients_day': 'Number of Patients per Day',
		'num_patients_month': 'Number of Patients per Month',
		}
	d_today = date_in
	q_this_month = (Q(scheduledDate__month=d_today.month) & Q(scheduledDate__lt=d_today)) & (Q(status="CHOT") | Q(status="RESO"))
	q_this_day = Q(scheduledDate=d_today) & (Q(status="CHOT") | Q(status="RESO"))
	months_visits = Visit.objects.filter(q_this_month)
	pt_monthly_index = len(months_visits)
	days_visits = Visit.objects.filter(q_this_day)
	daily_index=0
	totals={}
	for v in months_visits:
		if v.finishedBy not in totals.keys():
			totals[v.finishedBy] = {'day': 0, 'month': 0}
		totals[v.finishedBy]['month'] += 1
	for v in days_visits:
		if v.finishedBy not in totals.keys():
			totals[v.finishedBy] = {'day': 0, 'month': 0}
		totals[v.finishedBy]['day'] += 1
	summary_rows=[]
	for clinician in totals.keys():
		summary_rows.append({'clinician':clinician, 'num_patients_day':totals[clinician]['day'],'num_patients_month': totals[clinician]['month']})
	return dump_table( field_names, headers, summary_rows )

@login_required
def diagnosis_tally(request):
	"""
	"""
	
	from ocemr.forms import SelectDateRangeForm
	form_valid=0
        if request.method == 'POST':
                form = SelectDateRangeForm(request.POST)
                if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			form_valid=1
        else:
                form = SelectDateRangeForm()
	if not form_valid:
	        return render_to_response('popup_form.html', {
	                'title': 'Enter Date Range For Report',
	                'form_action': '/reports/diagnosis/tally/',
	                'form': form,
	        })
	dt_start = datetime(
		date_start_in.year,date_start_in.month,date_start_in.day,
		0,0,0
		)
	dt_end = datetime(
		date_end_in.year,date_end_in.month,date_end_in.day,
		23,59,59
		)
	#(Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end))

	field_names=[
		'diag',
		'tally',
		]
	headers={}
	#	'diag': 'Diagnosis',
	#	'tally': 'Tally',
	#	}
	from ocemr.models import Visit, Diagnosis
	q_this_day = ( Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end) ) & (Q(status="CHOT") | Q(status="RESO"))
	days_visits = Visit.objects.filter(q_this_day)
	q_dignosis_active = (Q(status="NEW") | Q(status="FOL"))
	s={}
	num_visits=0
	for v in days_visits:
		num_visits += 1
		for d in Diagnosis.objects.filter(visit=v).filter(q_dignosis_active):
			diagnosis = d.type.title
			if diagnosis not in s.keys():
				s[diagnosis]=1
			else:
				s[diagnosis] += 1
	sorted_keys=sorted(s, key=s.get)
	sorted_keys.reverse()

	summary_rows=[]
	summary_rows.append({'diag':'Dates:', 'tally': "%s-%s-%s -> %s-%s-%s"%(
		dt_start.day, dt_start.month, dt_start.year,
		dt_end.day, dt_end.month, dt_end.year,
		 )} )
	summary_rows.append({'diag':'Total Patients:', 'tally':num_visits})
	summary_rows.append({'diag':'', 'tally':''})
	summary_rows.append({'diag':'Diagnosis', 'tally':'Tally'})
	for key in sorted_keys:
		summary_rows.append({'diag': key, 'tally': s[key]})
	return dump_csv( "diagnosis-tally-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
		
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


@login_required
def cashflow(request):
	"""
	"""
	
	from ocemr.forms import SelectDateRangeForm
	form_valid=0
        if request.method == 'POST':
                form = SelectDateRangeForm(request.POST)
                if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			form_valid=1
        else:
                form = SelectDateRangeForm()
	if not form_valid:
	        return render_to_response('popup_form.html', {
	                'title': 'Enter Date Range For Report',
	                'form_action': '/reports/cashflow/',
	                'form': form,
	        })

	
	field_names=[
		'date',
		'totbill',
		'totcoll',
		'diff',
		]
	headers={
		'date': 'Date',
		'totbill': 'Total Billed',
		'totcoll': 'Total Collected',
		'diff': 'Total Difference',
		}
	summary_rows=[]
	from ocemr.models import Visit, CashLog
	curdate = date_start_in
	total_billed = 0
	total_collected = 0
	while curdate <= date_end_in:
		billed=0
		collected=0
		dt_start = datetime(curdate.year,curdate.month,curdate.day,0,0,0)
		dt_end = datetime(curdate.year,curdate.month,curdate.day,23,59,59)
		for v in Visit.objects.filter(finishedDateTime__gte=dt_start,finishedDateTime__lte=dt_end):
			billed += v.cost
		for c in CashLog.objects.filter(addedDateTime__gte=dt_start,addedDateTime__lte=dt_end):
			collected += c.amount
		summary_rows.append({'date':curdate,'totbill':billed,'totcoll':collected,'diff':billed-collected})
		total_billed += billed
		total_collected +=  collected
		curdate = curdate + timedelta(1)
	summary_rows.append({'date':'Total','totbill':total_billed, 'totcoll':total_collected,'diff':total_billed-total_collected})

	return dump_csv( "cashflow-%s-%s.csv"%(date_start_in.strftime("%Y%m%d"), date_end_in.strftime("%Y%m%d")), field_names, headers, summary_rows )


@login_required
def accounts_outstanding(request):
	"""
	"""

	from ocemr.forms import SelectDateRangeForm
	form_valid=0
        if request.method == 'POST':
                form = SelectDateRangeForm(request.POST)
                if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			form_valid=1
        else:
                form = SelectDateRangeForm()
	if not form_valid:
	        return render_to_response('popup_form.html', {
	                'title': 'Enter Date Range For Report',
	                'form_action': '/reports/accounts_outstanding/',
	                'form': form,
	        })


	from ocemr.models import Patient, Visit, CashLog

	field_names=[
		'patient',
		'billed',
		'collected',
		'owed',
		]
	headers={
		'patient': 'Patient',
		'billed': 'Total Billed',
		'collected': 'Total Collected',
		'owed': 'Amount Owed',
		}
	dt_start = datetime(date_start_in.year,date_start_in.month,date_start_in.day,0,0,0)
	dt_end = datetime(date_end_in.year,date_end_in.month,date_end_in.day,23,59,59)
	summary_rows=[]
	for p in Patient.objects.all(  ):
		billed=0
		collected=0
		for v in Visit.objects.filter(patient=p,finishedDateTime__gte=dt_start,finishedDateTime__lte=dt_end):
			billed += v.cost
			for c in CashLog.objects.filter(visit=v):
				collected += c.amount
		if collected < billed:
			summary_rows.append({'patient': p, 'billed': billed, 'collected':collected, 'owed':billed-collected})
	return dump_csv( "outstanding_accounts-%s-%s.csv"%(date_start_in.strftime("%Y%m%d"), date_end_in.strftime("%Y%m%d")),field_names, headers, summary_rows )
