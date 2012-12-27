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
		out_txt += "<TH>" + headers[f]
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

def dump_graph_pie(title,labels,data):
        """
        """


	#
	total = 0
	other = 0
	for x in data:
		total += x
	todelete=[]
	for i in range(0,len(labels)):
		if float(data[i])/float(total) <= .02:
			other += data[i]
			todelete.append(i)
	todelete.reverse()
	for i in todelete:
		labels.pop(i)
		data.pop(i)
	if other > 0:
		labels.append('Other ( < 2% )')
		data.append(other)

        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

	fig = plt.figure(figsize=(5,5),dpi=75)
	fig.interactive = False

        plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True)
        plt.title(title, bbox={'facecolor':'0.8', 'pad':5})

        plt.draw()
        canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)
        response = HttpResponse(content_type='image/png')
        canvas.print_png(response)
        matplotlib.pyplot.close(fig)
        return response

@login_required
def index(request):
        """
        Reports Landing Page
        """
        return render_to_response('reports.html',context_instance=RequestContext(request))

@login_required
def lab_tally(request):
	"""
	"""
	from ocemr.forms import TallyReportForm

	form_valid=0
	if request.method == 'POST':
		form = TallyReportForm(request.POST)
		if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			dump_type = form.cleaned_data['dump_type']

			form_valid=1
	else:
		form = TallyReportForm()
	if not form_valid:
		return render_to_response('popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/lab/tally/',
	                'form': form,
	        },context_instance=RequestContext(request))

	dt_start = datetime(date_start_in.year,date_start_in.month,date_start_in.day,0,0,0)
	dt_end = datetime(date_end_in.year,date_end_in.month,date_end_in.day,23,59,59)
	q_this_day = (Q(orderedDateTime__gte=dt_start) & Q(orderedDateTime__lte=dt_end)) & (Q(status="CAN") | Q(status="COM")| Q(status="FAI"))
	from ocemr.models import Lab
	days_labs = Lab.objects.filter(q_this_day)
	ordered={}
	canceled={}
	complete={}
	failed={}
	for l in days_labs:
		if l.type.title not in ordered.keys():
			ordered[l.type.title] = 0
			canceled[l.type.title] = 0
			complete[l.type.title] = 0
			failed[l.type.title] = 0
		ordered[l.type.title] += 1
		if l.status == "COM":
			complete[l.type.title] += 1
		elif l.status == "CAN":
			canceled[l.type.title] += 1
		elif l.status == "FAI":
			failed[l.type.title] += 1

	sorted_keys=sorted(ordered,key=ordered.__getitem__,reverse=True)

	if dump_type == "G_PIE":
		title="Lab Tally %s -> %s"%(dt_start.strftime("%Y-%m-%d"),dt_end.strftime("%Y-%m-%d"))
		labels=[]
		data = []
		for key in sorted_keys:
			labels.append(key)
			data.append(ordered[key])
		return dump_graph_pie(title, labels, data)

	summary_rows=[]
	field_names=[ 'lab', 'ordered', 'complete', 'canceled', 'failed' ]
	headers={
		'lab': 'Lab Type',
		'ordered': 'Number Ordered',
		'complete': 'Number Complete',
		'canceled': 'Number Canceled',
		'failed': 'Number Failed',
		 }
	for l in sorted_keys:
		summary_rows.append(
			{
				'lab': l,
				'ordered': ordered[l],
				'complete': complete[l],
				'canceled': canceled[l],
				'failed': failed[l],
			})
	if dump_type == "CSV":
		return dump_csv( "lab-tally-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(field_names, headers, summary_rows )

@login_required
def med_tally(request):
	"""
	"""
	from ocemr.forms import TallyReportForm

	form_valid=0
	if request.method == 'POST':
		form = TallyReportForm(request.POST)
		if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			dump_type = form.cleaned_data['dump_type']

			form_valid=1
	else:
		form = TallyReportForm()
	if not form_valid:
		return render_to_response('popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/med/tally/',
	                'form': form,
	        },context_instance=RequestContext(request))

	dt_start = datetime(date_start_in.year,date_start_in.month,date_start_in.day,0,0,0)
	dt_end = datetime(date_end_in.year,date_end_in.month,date_end_in.day,23,59,59)
	q_this_day = (Q(addedDateTime__gte=dt_start) & Q(addedDateTime__lte=dt_end)) & (Q(status="DIS") | Q(status="SUB")| Q(status="CAN"))
	from ocemr.models import Med
	days_meds = Med.objects.filter(q_this_day)
	daily_index=0
	ordered={}
	dispensed={}
	substituted={}
	canceled={}
	for m in days_meds:
		if m.type.title not in ordered.keys():
			ordered[m.type.title] = 0
			dispensed[m.type.title] = 0
			substituted[m.type.title] = 0
			canceled[m.type.title] = 0
		ordered[m.type.title] += 1
		if m.status == "DIS":
			dispensed[m.type.title] += 1
		elif m.status == "SUB":
			substituted[m.type.title] += 1
		elif m.status == "CAN":
			canceled[m.type.title] += 1

	sorted_keys=sorted(ordered,key=ordered.__getitem__,reverse=True)

	if dump_type == "G_PIE":
		title="Med Tally %s -> %s"%(dt_start.strftime("%Y-%m-%d"),dt_end.strftime("%Y-%m-%d"))
		labels=[]
		data = []
		for key in sorted_keys:
			labels.append(key)
			data.append(ordered[key])
		return dump_graph_pie(title, labels, data)

	summary_rows=[]
	field_names=[ 'med', 'ord', 'dis', 'sub', 'can' ]
	headers={
		'med': 'Med Type',
		'ord': 'Number Ordered',
		'dis': 'Number Dispensed',
		'sub': 'Number Substituted',
		'can': 'Number Canceled',
		 }
	for m in sorted_keys:
		summary_rows.append(
			{
				'med': m,
				'ord': ordered[m],
				'dis': dispensed[m],
				'sub': substituted[m],
				'can': canceled[m],
			})
	if dump_type == "CSV":
		return dump_csv( "med-tally-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(field_names, headers, summary_rows )

@login_required
def clinician_tally(request):
	"""
	"""
	from ocemr.forms import TallyReportForm

	form_valid=0
	if request.method == 'POST':
		form = TallyReportForm(request.POST)
		if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			dump_type = form.cleaned_data['dump_type']

			form_valid=1
	else:
		form = TallyReportForm()
	if not form_valid:
		return render_to_response('popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/clinician/tally/',
	                'form': form,
	        },context_instance=RequestContext(request))
	from ocemr.models import Visit
	dt_start = datetime(date_start_in.year,date_start_in.month,date_start_in.day,0,0,0)
	dt_end = datetime(date_end_in.year,date_end_in.month,date_end_in.day,23,59,59)
	q_this_day = (Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end)) & (Q(status="CHOT") | Q(status="RESO"))
	days_visits = Visit.objects.filter(q_this_day)
	daily_index=0
	totals={}
	for v in days_visits:
		if v.finishedBy not in totals.keys():
			totals[v.finishedBy] = 0
		totals[v.finishedBy] += 1

	sorted_keys=sorted(totals,key=totals.__getitem__,reverse=True)

	if dump_type == "G_PIE":
		title="Clinician Visit Tally %s -> %s"%(dt_start.strftime("%Y-%m-%d"),dt_end.strftime("%Y-%m-%d"))
		labels=[]
		data = []
		for key in sorted_keys:
			labels.append(key)
			data.append(totals[key])
		return dump_graph_pie(title, labels, data)

	summary_rows=[]
	field_names=[ 'clinician', 'num_patients', ]
	headers={ 'clinician': 'Clinician', 'num_patients': 'Number of Patients', }
	for clinician in sorted_keys:
		summary_rows.append({'clinician':clinician, 'num_patients':totals[clinician]})
	if dump_type == "CSV":
		return dump_csv( "clinician-visit-tally-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(field_names, headers, summary_rows )

@login_required
def diagnosis_tally(request):
	"""
	"""
	from ocemr.forms import DiagnosisTallyReportForm
	form_valid=0
        if request.method == 'POST':
                form = DiagnosisTallyReportForm(request.POST)
                if form.is_valid():
                        date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
                        	date_end_in = form.cleaned_data['date_start']
			else:
                        	date_end_in = form.cleaned_data['date_end']
			age_min = form.cleaned_data['age_min']
			age_max = form.cleaned_data['age_max']
			dump_type = form.cleaned_data['dump_type']
			form_valid=1
        else:
                form = DiagnosisTallyReportForm()
	if not form_valid:
	        return render_to_response('popup_form.html', {
	                'title': 'Enter Date Range For Report',
	                'form_action': '/reports/diagnosis/tally/',
	                'form': form,
	        },context_instance=RequestContext(request))
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
	headers={
		'diag': 'Diagnosis',
		'tally': 'Tally',
		}
	from ocemr.models import Visit, Diagnosis
	q_this_day = ( Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end) ) & (Q(status="CHOT") | Q(status="RESO"))
	days_visits = Visit.objects.filter(q_this_day)
	currentYear = datetime.now().year
	if age_min != None:
		maxYear = currentYear-age_min
		q_age_range = Q(patient__birthYear__lte=maxYear)
		days_visits = days_visits.filter(q_age_range)
	if age_max != None:
		minYear = currentYear-age_max
		q_age_range = Q(patient__birthYear__gte=minYear)
		days_visits = days_visits.filter(q_age_range)
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

	if dump_type == "G_PIE":
		title="Diagnosis Tally %s -> %s"%(dt_start.strftime("%Y-%m-%d"),dt_end.strftime("%Y-%m-%d"))
		labels=[]
		data = []
		for key in sorted_keys:
			labels.append(key)
			data.append(s[key])
		return dump_graph_pie(title, labels, data)

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
	if dump_type == "CSV":
		return dump_csv( "diagnosis-tally-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(field_names, headers, summary_rows )
	else:
		raise "Invalid Dump Type"
		
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
	        },context_instance=RequestContext(request))


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
	if date_in.month == 12:
		next_month=1
		next_year=date_in.year+1
	else:
		next_month=date_in.month+1
		next_year=date_in.year
	dt_month_start = datetime(date_in.year,date_in.month,1,0,0,0)
	dt_month_end = datetime(next_year,next_month,1,0,0,0)
	dt_start = datetime(date_in.year,date_in.month,date_in.day,0,0,0)
	dt_end = datetime(date_in.year,date_in.month,date_in.day,23,59,59)
	q_this_month = ( Q(finishedDateTime__gte=dt_month_start) &
				Q(finishedDateTime__lt=dt_month_end ) &
				Q(finishedDateTime__lt=dt_start)
			) & (Q(status="CHOT") | Q(status="RESO"))
	q_this_day = ( Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end ) ) & (Q(status="CHOT") | Q(status="RESO"))
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
	if not request.user.is_staff:
		return HttpResponse( "Permission Denied." )

	
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
	        },context_instance=RequestContext(request))

	
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
	        },context_instance=RequestContext(request))


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

@login_required
def diagnosis_patient(request):
	"""
	"""
	from ocemr.forms import DiagnosisPatientReportForm
	form_valid=0
	if request.method == 'POST':
		form = DiagnosisPatientReportForm(request.POST)
		if form.is_valid():
			diagnosis_types = form.cleaned_data['diagnosis']
			date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
				date_end_in = form.cleaned_data['date_start']
			else:
				date_end_in = form.cleaned_data['date_end']
			age_min = form.cleaned_data['age_min']
			age_max = form.cleaned_data['age_max']
			dump_type = form.cleaned_data['dump_type']
			form_valid=1
	else:
		form = DiagnosisPatientReportForm()
	if not form_valid:
		return render_to_response('popup_form.html', {
			'title': 'Enter Details For Report',
			'form_action': '/reports/diagnosis_patient/',
			'form': form,
		},context_instance=RequestContext(request))
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
		'pid',
		'pname',
		'diag',
		'diagdate',
		]
	headers={
		'pid': 'Id',
		'pname': 'Name',
		'diag': 'Diagnosis',
		'diagdate': 'Diagnosis Date',
		}
	from ocemr.models import Diagnosis
	q = ( Q(diagnosedDateTime__gte=dt_start) & Q(diagnosedDateTime__lte=dt_end) ) & Q(status="NEW")
	diags = Diagnosis.objects.filter(q)
	subq=Q(type__in=diagnosis_types)
	diags = diags.filter( subq )
	currentYear = datetime.now().year
	if age_min != None:
		maxYear = currentYear-age_min
		q_age_range = Q(patient__birthYear__lte=maxYear)
		diags = diags.filter(q_age_range)
	if age_max != None:
		minYear = currentYear-age_max
		q_age_range = Q(patient__birthYear__gte=minYear)
		diags = diags.filter(q_age_range)
	summary_rows=[]
	summary_rows.append(headers)
	for d in diags:
		summary_rows.append({
			'pid': d.patient.id,
			'pname': d.patient,
			'diag': d.type,
			'diagdate': d.diagnosedDateTime,
			})
	if dump_type == "CSV":
		return dump_csv( "diagnosis-patient-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(field_names, headers, summary_rows )
	else:
		raise "Invalid Dump Type"

@login_required
def hmis105(request):
	"""
	"""

	from ocemr.forms import Hmis105Form

	form_valid=0
	if request.method == 'POST':
		form = Hmis105Form(request.POST)
		if form.is_valid():
			date_start_in = form.cleaned_data['date_start']
			if form.cleaned_data['date_end']==None:
				date_end_in = form.cleaned_data['date_start']
			else:
				date_end_in = form.cleaned_data['date_end']
			dump_type = form.cleaned_data['dump_type']
			form_valid=1
	else:
		form = Hmis105Form()
	if not form_valid:
		return render_to_response('popup_form.html', {
			'title': 'Enter Details For Report',
			'form_action': '/reports/hmis105/',
			'form': form,
		},context_instance=RequestContext(request))
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
		'cat',
		'lt4m',
		'lt4f',
		'gt4m',
		'gt4f',
		'visit_list',
		]
	headers={
		'cat': 'Category',
		'lt4m': '0-4 years, Male',
		'lt4f': '0-4 years, Female',
		'gt4m': '5 and over, Male',
		'gt4f': '5 and over, Female',
		'visit_list': 'Visit List',
		}
	from ocemr.models import Visit, Referral, Diagnosis, DiagnosisType

	summary_rows=[]
	new_patient_visits=[0,0,0,0]
	old_patient_visits=[0,0,0,0]
	total_visits=[0,0,0,0]
	referrals_from=[0,0,0,0]

	diagnoses = [
		{ 'NAME': "1.3.1 Epidemic-Prone Diseases"},
		{ 'NAME': "01 Acute flaccid paralysis", 'ICPC2': [ "N70", ], },
		{ 'NAME': "02 Cholera", 'ICPC2': [ ], },
		{ 'NAME': "03 Dysentery", 'ICPC2': [ "D11", ], },
		{ 'NAME': "04 Guinea worm", 'ICPC2': [ ], },
		{ 'NAME': "05 Bacterial meningitis", 'ICPC2': [ "N71", ], },
		{ 'NAME': "06 Measles", 'ICPC2': [ "A71", ], },
		{ 'NAME': "07 Tetanus (Neonatal)", 'ICPC2': [ "N72", ], },
		{ 'NAME': "08 Plauge", 'ICPC2': [ ], },
		{ 'NAME': "09 Rabies", 'ICPC2': [ ], },
		{ 'NAME': "10 Yellow Fever", 'ICPC2': [ ], },
		{ 'NAME': "11 Other Viral Haemorrhagic Fevers", 'ICPC2': [ ], },
		{ 'NAME': "12 Severe Acute Respiratory Infection (SARI)", 'ICPC2': [ ], },
		{ 'NAME': "13 Adverse Events Following Immunization (AEFI)", 'ICPC2': [ ], },
		{ 'NAME': "14 Other Emerging Infectious Diseases, specify e.g. small pox, ILI, SARS", 'ICPC2': [ ], },
		{ 'NAME': "1.3.2 Other Infectious/Communicable Diseases"},
		{ 'NAME': "15 Diarrhea- Acute", 'ICPC2': [ "D11", ], },
		{ 'NAME': "16 Diarrhea- Persistent", 'ICPC2': [ ], },
		{ 'NAME': "17 Ear Nose and Throat (ENT) conditions", 'ICPC2': [ "H", "R06", "R07", "R08", "R09", "R1", "R20", "R21", "R72", "R73", "R87", "R90", "R97" ], },
		{ 'NAME': "18 Ophthalmia neonatorum", 'ICPC2': [ "F03", "F70", "F73", "F80" ], 'MAX_AGE_DAYS': 21},
		{ 'NAME': "19 Other Eye conditions (subtract line 18)", 'ICPC2': [ "F", ], },
		{ 'NAME': "20 Urethral discharges", 'ICPC2': [ "Y03", ], },
		{ 'NAME': "21 Genital ulcers", 'ICPC2': [ ], },
		{ 'NAME': "22 Sexually Transmitted Infection due to SGBV", 'ICPC2': [ ], },
		{ 'NAME': "23 Other Sexually Transmitted Infections", 'ICPC2': [ "X70", "X71", "X72", "X73", "X74", "X90", "X91", "X92", "Y70", "Y71", "Y72", "Y73", "Y74", "Y75", "Y76" ], },
		{ 'NAME': "24 Urinary Tract Infections (UTI)", 'ICPC2': [ "U70", "U71", "U72" ], },
		{ 'NAME': "25 Intestinal Worms", 'ICPC2': [ "D96", ], },
		{ 'NAME': "26 Leprosy (Manually Review S76, S99)", 'ICPC2': [ "S76", "S99" ], },
		{ 'NAME': "27 Malaria", 'ICPC2': [ "A73", ], },
		{ 'NAME': "28 Other types of meningitis", 'ICPC2': [ ], },
		{ 'NAME': "29 No pneumonia Cough or Cold", 'ICPC2': [ "R05", "R71", "R74" ], },
		{ 'NAME': "30 Pneumonia", 'ICPC2': [ "R81", ], },
		{ 'NAME': "31 Skin Diseases", 'ICPC2': [ "S", ], },
		{ 'NAME': "32 Tuberculosis (New smear positive cases)", 'ICPC2': [ ], },
		{ 'NAME': "33 Other Tuberculosis", 'ICPC2': [ "A70", ], },
		{ 'NAME': "34 Typhoid Fever", 'ICPC2': [ "A78", ], },
		{ 'NAME': "35 Tetanus (over 28 days age)", 'ICPC2': [ "N72", ], 'MIN_AGE_DAYS': 28 },
		{ 'NAME': "36 Sleeping sickness", 'ICPC2': [ ], },
		{ 'NAME': "37 Pelvic Inflammatory Disease (PID)", 'ICPC2': [ "X74", ], },
		{ 'NAME': "1.3.3 Maternal and Perinatal Conditions"},
		{ 'NAME': "38 Abortions due to Gender-Based Violence (GBV)", 'ICPC2': [ ], },
		{ 'NAME': "39 Abortions due to other causes", 'ICPC2': [ "W82", "W83" ], },
		{ 'NAME': "40 Malaria in pregnancy", 'DIAGNOSIS_TYPE': [ 18, 20 ], },
		{ 'NAME': "41 High blood pressure in pregnancy", 'DIAGNOSIS_TYPE': [ 216, ], },
		{ 'NAME': "42 Obstructed labor", 'ICPC2': [ ], },
		{ 'NAME': "43 Puerperial Sepsis", 'ICPC2': [ "W70", ], },
		{ 'NAME': "44 Haemorrhage in pregnancy (APH and/or PPH)", 'ICPC2': [ "W03", "W17" ], },
		{ 'NAME': "1.3.4 Maternal and Perinatal Diseases"},
		{ 'NAME': "45 Neonatal septicemia (Manually Review A94)", 'ICPC2': [ "A94", ], },
		{ 'NAME': "46 Perinatal conditions in newborns (0-7 days) (Manually Review A94)", 'ICPC2': [ "A94", ], },
		{ 'NAME': "47 Neonatal conditions in newborns (8-28 days) (Manually Review A94)", 'ICPC2': [ "A94", ], },
		{ 'NAME': "1.3.5 Non Communicable Diseases"},
		{ 'NAME': "48 Anaemia", 'ICPC2': [ "B82", ], },
		{ 'NAME': "49 Asthma", 'ICPC2': [ "R96", ], },
		{ 'NAME': "50 Periodontal diseases", 'ICPC2': [ "D19", ], },
		{ 'NAME': "51 Diabetes mellitus", 'ICPC2': [ "T90", "W85" ], },
		{ 'NAME': "52 Bipolar disorders", 'ICPC2': [ "P73" ], },
		{ 'NAME': "53 Hypertension", 'ICPC2': [ "K86", "K87" ], },
		{ 'NAME': "54 Depression", 'ICPC2': [ "P76", ], },
		{ 'NAME': "55 Schizophrenia", 'ICPC2': [ "P72", ], },
		{ 'NAME': "56 HIV related psychosis (Manually Review B90)", 'ICPC2': [ "B90", ], },
		{ 'NAME': "57 Anxiety disorders", 'ICPC2': [ "P74", ], },
		{ 'NAME': "58 Alcohol abuse", 'ICPC2': [ "P15", "P16" ], },
		{ 'NAME': "59 Drug abuse", 'ICPC2': [ "P19", ], },
		{ 'NAME': "60 Childhood Mental Disorders", 'ICPC2': [ ], },
		{ 'NAME': "61 Epilepsy", 'ICPC2': [ "N88", ], },
		{ 'NAME': "62 Dementia", 'ICPC2': [ "P70", ], },
		{ 'NAME': "63 Other forms of mental illness", 'ICPC2': [
			"P71", "P72", "P73", "P74", "P75", "P76", "P77", "P78",
			"P79", "P8", "P9"
			 ], },
		{ 'NAME': "64 Cardiovascular diseases", 'ICPC2': [ "K", ], },
		{ 'NAME': "65 Gastro-Intestinal Disorders (non-Infective) ",
			'ICPC2': [ "D0", "D1", "D2", "D74", "D75", "D76", "D77",
				"D78", "D79", "D8", "D9" ], },
		{ 'NAME': "66 Severe Acute Malnutrition (Marasmus, Kwashiorkor, Marasmic-kwash)", 'ICPC2': [ "T91", ], },
		{ 'NAME': "67 Jaw injuries", 'ICPC2': [ "L07", ], },
		{ 'NAME': "68 Injuries- Road traffic Accidents (Manually Review A80, A81)", 'ICPC2': [ "A80", "A81" ], },
		{ 'NAME': "69 Injuries due to Gender based violence (Manually Review A80, A81)", 'ICPC2': [ "A80", "A81" ], },
		{ 'NAME': "70 Injuries (Trauma due to other causes) (Manually Review A80, A81)", 'ICPC2': [ "A80", "A81" ], },
		{ 'NAME': "71 Animal bites (Manually Review S13)", 'ICPC2': [ "S13", ], },
		{ 'NAME': "72 Snake bites (Manually Review S13)", 'ICPC2': [ "S13", ], },
		{ 'NAME': "1.3.6 Minor operations in OPD"},
		{ 'NAME': "73 Tooth extractions", 'ICPC2': [ ], },
		{ 'NAME': "74 Dental Fillings", 'ICPC2': [ ], },
		{ 'NAME': "1.3.7 Neglegted Tropical Diseases"},
		{ 'NAME': "75 Leishmaniasis (Manually Review A78)", 'ICPC2': [ "A78", ], },
		{ 'NAME': "76 Lymphatic Filariasis (hydrocele) (Manually Review A78)", 'ICPC2': [ "A78", ], },
		{ 'NAME': "77 Lymphatic Filariasis (Lymphoedema) (Manually Review A78)", 'ICPC2': [ "A78", ], },
		{ 'NAME': "78 Urinary Schistosomiasis (Manually Review A78)", 'ICPC2': [ "A78", ], },
		{ 'NAME': "79 Intestinal Schistosomiasis (Manually Review A78)", 'ICPC2': [ "A78", ], },
		{ 'NAME': "80 Onchocerciasis (Manually Review A78)", 'ICPC2': [ "A78", ], },
		{ 'NAME': "81 Other diagnoses (specify priority for District)", 'ICPC2': [ ], },
		{ 'NAME': "82 Deaths in OPD", 'ICPC2': [ ], },
		{ 'NAME': "83 All others", 'ICPC2': [ ], },
		]
	diag_map = {}
	for d in diagnoses:
		diag_map[d['NAME']] = [0,0,0,0,[]]
	visits = Visit.objects.filter(Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end) & (Q(status="CHOT") | Q(status="RESO")) )
	for v in visits:
		if not v.finishedDateTime:
			print "Warning: skipping unfinished visit: %s"%v
		index = 0
		if v.patient.birthYear < v.finishedDateTime.year - 4:
			index += 2
		if v.patient.gender == "F":
			index += 1
		total_visits[index] += 1
		if Visit.objects.filter(Q(patient=v.patient) & Q(finishedDateTime__lte=dt_end)).count() > 1:
			old_patient_visits[index] += 1
		else:
			new_patient_visits[index] += 1
		referrals = Referral.objects.filter(visit=v)
		referrals_from[index] += len(referrals)

		for d in diagnoses:
			if not d.has_key("types"):
				d["types"] = []
				if d.has_key('ICPC2'):
					for icpc2type in d['ICPC2']:
						for dt in DiagnosisType.objects.filter(Q(icpc2Code__startswith=icpc2type)):
							d["types"].append(dt.id)
				if d.has_key('DIAGNOSIS_TYPE'):
					for id in d['DIAGNOSIS_TYPE']:
						d["types"].append(id)

			if d.has_key("MAX_AGE_DAYS"):
				if  not v.patient.birthDate:
					continue
				delta = v.finishedDateTime.date() - v.patient.birthDate
				if delta.days > d['MAX_AGE_DAYS']:
					continue

			if d.has_key("MIN_AGE_DAYS"):
				if  not v.patient.birthDate:
					if v.patient.birthYear <= v.finishedDateTime.year:
						continue
				else:
					delta = v.finishedDateTime.date() - v.patient.birthDate
					if delta.days < d['MIN_AGE_DAYS']:
						continue

			my_d = Diagnosis.objects.filter(Q(visit=v) & Q(status="NEW") & Q(type__in=d["types"]))
			my_count = my_d.count()
			if my_count > 0:
				diag_map[d['NAME']][index] += my_count
				diag_map[d['NAME']][4].append("<A HREF=\"#%(diag_name)s_%(visit_id)s\" onclick=\"window.opener.location.href='/visit/%(visit_id)s/plan/';\">%(visit_id)s</A>"%{'visit_id': v.id, 'diag_name': d['NAME']})


	summary_rows.append({	'cat': "1.1 Outpatient Attendance",
				'lt4m': "", 'lt4f': "", 'gt4m': "", 'gt4f': "",
				'visit_list': "",
				})
	summary_rows.append({	'cat': "New Attendance",
				'lt4m': new_patient_visits[0],
				'lt4f': new_patient_visits[1],
				'gt4m': new_patient_visits[2],
				'gt4f': new_patient_visits[3],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "Re-Attendance",
				'lt4m': old_patient_visits[0],
				'lt4f': old_patient_visits[1],
				'gt4m': old_patient_visits[2],
				'gt4f': old_patient_visits[3],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "Total Attendance",
				'lt4m': total_visits[0],
				'lt4f': total_visits[1],
				'gt4m': total_visits[2],
				'gt4f': total_visits[3],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "1.2 Outpatient Referrals",
				'lt4m': "", 'lt4f': "", 'gt4m': "", 'gt4f': "",
				'visit_list': "",
				})
	summary_rows.append({   'cat': "Referrals to unit",
				'lt4m': "-",
				'lt4f': "-",
				'gt4m': "-",
				'gt4f': "-",
				'visit_list': "",
				})
	summary_rows.append({   'cat': "Referrals from unit",
				'lt4m': referrals_from[0],
				'lt4f': referrals_from[1],
				'gt4m': referrals_from[2],
				'gt4f': referrals_from[3],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "1.3 Outpatient Diagnoses",
				'lt4m': "", 'lt4f': "", 'gt4m': "", 'gt4f': "",
				'visit_list': "",
				})
	for d in diagnoses:
		if len(d["types"]) == 0:
			summary_rows.append({
				'cat': d['NAME'],
				'lt4m': "-",
				'lt4f': "-",
				'gt4m': "-",
				'gt4f': "-",
				'visit_list': "-",
				})
		else:
			summary_rows.append({
				'cat': d['NAME'],
				'lt4m':  diag_map[d['NAME']][0],
				'lt4f':  diag_map[d['NAME']][1],
				'gt4m':  diag_map[d['NAME']][2],
				'gt4f':  diag_map[d['NAME']][3],
				'visit_list': ", ".join(diag_map[d['NAME']][4])
				})

	if dump_type == "CSV":
		return dump_csv( "hmis-105-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(field_names, headers, summary_rows )
	else:
		raise "Invalid Dump Type"
