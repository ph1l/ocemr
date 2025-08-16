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
from datetime import datetime, timedelta

def dump_table(request,field_names,headers,data_rows):
	"""
	"""
	out_txt="<TABLE>\n"
	out_txt += "<TR>"
	for f in field_names:
		out_txt += "<TH>" + headers[f]
	out_txt += "</TR>\n"
	for r in data_rows:
		out_txt += "<TR CLASS=results>"
		for f in field_names:
			out_txt += "<TD>%s</TD>"%r[f]
		out_txt += "</TR>\n"
	out_txt += "</TABLE>\n"

	return render(request, 'popup_table.html', {'table': out_txt})
	
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
	from wsgiref.util import FileWrapper

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

def download(filehandle, filename):
	response = HttpResponse(filehandle.read(), content_type='application/force-download')
	filehandle.close()
	response['Content-Disposition'] = 'inline; filename=%s' % filename
	return response

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)

@login_required
def index(request):
        """
        Reports Landing Page
        """
        return render(request, 'reports.html')

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
		return render(request, 'popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/lab/tally/',
	                'form': form,
	        })

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
		return dump_table(request, field_names, headers, summary_rows )

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
		return render(request, 'popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/med/tally/',
	                'form': form,
	        })

	dt_start = datetime(date_start_in.year,date_start_in.month,date_start_in.day,0,0,0)
	dt_end = datetime(date_end_in.year,date_end_in.month,date_end_in.day,23,59,59)
	q_this_day = (Q(addedDateTime__gte=dt_start) & Q(addedDateTime__lte=dt_end)) & (Q(status="DIS") | Q(status="SUB")| Q(status="CAN"))
	from ocemr.models import Med
	days_meds = Med.objects.filter(q_this_day)
	daily_index=0
	ordered={}
	dispensed={}
	units_dispensed={}
	substituted={}
	canceled={}
	for m in days_meds:
		if m.type.title not in ordered.keys():
			ordered[m.type.title] = 0
			dispensed[m.type.title] = 0
			units_dispensed[m.type.title] = 0
			substituted[m.type.title] = 0
			canceled[m.type.title] = 0
		ordered[m.type.title] += 1
		if m.status == "DIS":
			dispensed[m.type.title] += 1
			if not m.dispenseAmount is None:
				units_dispensed[m.type.title] += m.dispenseAmount
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
	field_names=[ 'med', 'ord', 'dis', 'udis', 'sub', 'can' ]
	headers={
		'med': 'Med Type',
		'ord': 'Number Ordered',
		'dis': 'Number Dispensed',
		'udis': 'Units Dispensed',
		'sub': 'Number Substituted',
		'can': 'Number Canceled',
		 }
	for m in sorted_keys:
		summary_rows.append(
			{
				'med': m,
				'ord': ordered[m],
				'dis': dispensed[m],
				'udis': units_dispensed[m],
				'sub': substituted[m],
				'can': canceled[m],
			})
	if dump_type == "CSV":
		return dump_csv( "med-tally-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(request, field_names, headers, summary_rows )

@login_required
def village_tally(request):
	"""
	"""
	from ocemr.forms import VillageTallyReportForm

	form_valid=0
	if request.method == 'POST':
		form = VillageTallyReportForm(request.POST)
		if form.is_valid():
			dump_type = form.cleaned_data['dump_type']

			form_valid=1
	else:
		form = VillageTallyReportForm()
	if not form_valid:
		return render(request, 'popup_form.html', {
	                'title': 'Enter type For Report',
	                'form_action': '/reports/village/tally/',
	                'form': form,
	        })
	from ocemr.models import Patient
	patients = Patient.objects.all()
	totals={}
	for p in patients:
		if p.village.name not in totals.keys():
			totals[p.village.name] = 0
		totals[p.village.name] += 1

	sorted_keys=sorted(totals,key=totals.__getitem__,reverse=True)

	if dump_type == "G_PIE":
		title="Village Tally"
		labels=[]
		data = []
		for key in sorted_keys:
			labels.append(key)
			data.append(totals[key])
		return dump_graph_pie(title, labels, data)

	summary_rows=[]
        field_names=[ 'village', 'num_patients', ]
	headers={ 'village': 'Village', 'num_patients': 'Number of Patients', }
	for village in sorted_keys:
		summary_rows.append({'village':village, 'num_patients':totals[village]})
	if dump_type == "CSV":
		return dump_csv( "village-tally-%s.csv"%(datetime.now().strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(request, field_names, headers, summary_rows )


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
		return render(request, 'popup_form.html', {
	                'title': 'Enter Date For Report',
	                'form_action': '/reports/clinician/tally/',
	                'form': form,
	        })
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
		return dump_table(request, field_names, headers, summary_rows )

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
	        return render(request, 'popup_form.html', {
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
		return dump_table(request, field_names, headers, summary_rows )
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
	        return render(request, 'popup_form.html', {
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
	        return render(request, 'popup_form.html', {
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
	        return render(request, 'popup_form.html', {
	                'title': 'Enter Date Range For Report',
	                'form_action': '/reports/accounts_outstanding/',
	                'form': form,
	        })


	from ocemr.models import Visit, CashLog
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
	for v in Visit.objects.filter(finishedDateTime__gte=dt_start,finishedDateTime__lte=dt_end):
		billed=v.cost
		collected=0
		for c in CashLog.objects.filter(visit=v):
			collected += c.amount
		if collected < v.cost:
			existing = filter(lambda person: person['patient'] == v.patient, summary_rows)
			if existing:
				summary_rows.remove(existing[0])
				billed += existing[0]['billed']
				collected += existing[0]['collected']
			summary_rows.append({'patient': v.patient, 'billed': billed, 'collected':collected, 'owed':billed-collected})
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
		return render(request, 'popup_form.html', {
			'title': 'Enter Details For Report',
			'form_action': '/reports/diagnosis_patient/',
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
		return dump_table(request, field_names, headers, summary_rows )
	else:
		raise "Invalid Dump Type"

@login_required
def hmis105(request):
	"""
	"""

	from ocemr.forms import Hmis105Form
	import re

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
		return render(request, 'popup_form.html', {
			'title': 'Enter Details For Report',
			'form_action': '/reports/hmis105/',
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
		'cat',
		'lt28dm',
		'lt28df',
		'lt4m',
		'lt4f',
		'gt4m',
		'gt4f',
		'gt9m',
		'gt9f',
		'gt19m',
		'gt19f',
		'visit_list',
		]
	headers={
		'cat': 'Category',
		'lt28dm': '0-28 days, Male',
		'lt28df': '0-28 days, Female',
		'lt4m': '0-4 years, Male',
		'lt4f': '0-4 years, Female',
		'gt4m': '5-9 years, Male',
		'gt4f': '5-9 years, Female',
		'gt9m': '10-19 years, Male',
		'gt9f': '10-19 years, Female',
		'gt19m': '19+ years, Male',
		'gt19f': '19+ years, Female',
		'visit_list': 'Visit List',
		}
	from ocemr.models import Visit, Referral, Diagnosis, DiagnosisType

	summary_rows=[]
	new_patient_visits=[0,0,0,0,0,0,0,0,0,0]
	old_patient_visits=[[],[],[],[],[],[],[],[],[],[]]
	total_visits=[0,0,0,0,0,0,0,0,0,0]
	referrals_from=[0,0,0,0,0,0,0,0,0,0]

	diagnoses = [
		{ 'NAME': "1.3.1 Epidemic-Prone Diseases" },
		{ 'NAME': "EP01a. Suspected fever", 'ICPC2': [] },
		{ 'NAME': "EP01b. Malaria Total", 'ICPC2': [ "A73" ] },
		{ 'NAME': "EP01c. Malaria Confirmed (B/s and RDT Positive)", 'ICPC2': [ "A73" ] },
		{ 'NAME': "EP01d. Malaria cases treated", 'ICPC2': [ "A73" ] },
		{ 'NAME': "EP02. Acute flaccid paralysis", 'ICPC2': [ "N70" ] },
		{ 'NAME': "EP03. Animal Bites (suspected rabies) (Manually review)", 'ICPC2': [ "S13" ] },
		{ 'NAME': "EP04. Cholera", 'ICPC2': [] },
		{ 'NAME': "EP05. Dysentery", 'DIAGNOSIS_TYPE': [ 84 ] },
		{ 'NAME': "EP06. Guinea worm", 'ICPC2': [] },
		{ 'NAME': "EP07. Measles", 'ICPC2': [ "A71" ] },
		{ 'NAME': "EP08. Bacterial meningitis (Manually review and remove viral caused cases)", 'ICPC2': [ "N71" ] },
		{ 'NAME': "EP09. Neonatal Tetanus", 'ICPC2': [ "N72" ], 'MAX_AGE_DAYS': 28 },
		{ 'NAME': "EP10. Plauge", 'ICPC2': [] },
		{ 'NAME': "EP11. Yellow Fever", 'ICPC2': [] },
		{ 'NAME': "EP12. Other Viral Haemorrhagic Fevers", 'ICPC2': [] },
		{ 'NAME': "EP13. Severe Acute Respiratory Infection (SARI)", 'ICPC2': [] },
		{ 'NAME': "EP14. Adverse Events Following Immunization (AEFI)", 'ICPC2': [] },
		{ 'NAME': "EP15. Typhoid Fever", 'DIAGNOSIS_TYPE': [ 27, 701 ] },
		{ 'NAME': "EP16. Presumptive MDR TB cases", 'ICPC2': [] },
		{ 'NAME': "Other Emerging Infectious Diseases, specify e.g. ILI, SARS", 'ICPC2': [] },

		{ 'NAME': "1.3.2 Other Infectious/Communicable Diseases" },
		{ 'NAME': "CD01. Diarrhea- Acute", 'ICPC2': [ "D11" ] },
		{ 'NAME': "CD02. Diarrhea- Persistent", 'ICPC2': [ "D94" ] },
		{ 'NAME': "CD03. Urethral discharges", 'ICPC2': [ "Y03" ] },
		{ 'NAME': "CD04. Genital ulcers", 'ICPC2': [ "X90", "Y72" ] },
		{ 'NAME': "CD05. Sexually Transmitted Infection due to SGBV (Manually track)", 'ICPC2': [] },
		{ 'NAME': "CD06. Other Sexually Transmitted Infections", 'ICPC2': [ "X70", "X71", "X73", "X74", "X90", "X91", "X92", "Y70", "Y71", "Y72", "Y73", "Y74", "Y76" ] },
		{ 'NAME': "CD07. Urinary Tract Infections (UTI)", 'ICPC2': [ "U70", "U71", "U72" ] },
		{ 'NAME': "CD08. Intestinal Worms", 'ICPC2': [ "D96" ] },
		{ 'NAME': "CD09. Hematological Meningitis (Manually review with CD10)", 'ICPC2': [ "N71" ] },
		{ 'NAME': "CD10. Other types of meningitis (Manually review with CD09)", 'ICPC2': [ "N71" ] },
		{ 'NAME': "CD11. No pneumonia Cough or Cold", 'ICPC2': [ "R05", "R71", "R74", "R75", "R77", "R78" ] },
		{ 'NAME': "CD12. Pneumonia (Manually review with CD13)", 'ICPC2': [ "R81" ] },
		{ 'NAME': "CD13. Severe Pneumonia (Manually review with CD12)", 'ICPC2': [ "R81" ] },
		{ 'NAME': "CD14. Skin Diseases", 'ICPC2': [ "S03", "S09", "S10", "S11", "S70", "S71", "S72", "S73", "S74", "S75", "S76", "S84", "S95" ] },
		{ 'NAME': "CD15. Tetanus (over 28 days age)", 'ICPC2': [ "N72" ], 'MIN_AGE_DAYS': 28 },
		{ 'NAME': "CD16. Sleeping sickness", 'ICPC2': [] },
		{ 'NAME': "CD17. Pelvic Inflammatory Disease (PID)", 'ICPC2': [ "X74" ] },
		{ 'NAME': "CD18. Brucellosis", 'DIAGNOSIS_TYPE': [ 29 ] },

		{ 'NAME': "1.3.3 Neonatal Diseases" },
		{ 'NAME': "ND01. Neonatal Sepsis (0-7days)", 'DIAGNOSIS_TYPE': [ 704 ], 'MAX_AGE_DAYS': 7 },
		{ 'NAME': "ND02. Neonatal Sepsis (8-28days)", 'DIAGNOSIS_TYPE': [ 704 ], 'MIN_AGE_DAYS': 8, 'MAX_AGE_DAYS': 28 },
		{ 'NAME': "ND03. Neonatal Pneumonia (0-7days)", 'DIAGNOSIS_TYPE': [ 705 ], 'MAX_AGE_DAYS': 7 },
		{ 'NAME': "ND04. Neonatal Pneumonia (8-28days)", 'DIAGNOSIS_TYPE': [ 705 ], 'MIN_AGE_DAYS': 8, 'MAX_AGE_DAYS': 28 },
		{ 'NAME': "ND05. Neonatal Meningitis", 'ICPC2': [ "N71" ] },
		{ 'NAME': "ND06. Neonatal Jaundice", 'ICPC2': [ "D13" ] },
		{ 'NAME': "ND06. Premature baby (as a condition for management)", 'ICPC2': [ "A93" ] },
		{ 'NAME': "ND07. Other Neonatal Conditions", 'DIAGNOSIS_TYPE': [ 709 ] },

		{ 'NAME': "1.3.4 Non Communicable Diseases/Conditions" },
		{ 'NAME': "NC01. Sickle Cell Anaemia", 'DIAGNOSIS_TYPE': [ 64, 65 ] },
		{ 'NAME': "NC02. Other types of Anaemia", 'DIAGNOSIS_TYPE': [ 63 ] },
		{ 'NAME': "NC03. Gastro-Intestinal Disorders (non-Infective) ",
			'ICPC2': [ "D0", "D10", "D12", "D14", "D15", "D16", "D17", "D18", "D2", "D74", "D75", "D76", "D77",
				"D78", "D79", "D80", "D81", "D84", "D85", "D86", "D87", "D88", "D89", "D9" ] },
		{ 'NAME': "NC04. Pain Requiring Pallative Care", 'ICPC2': [] },

		{ 'NAME': "1.3.5 Oral diseases" },
		{ 'NAME': "OD01. Dental Caries", 'ICPC2': [] },
		{ 'NAME': "OD02. Gingivitis", 'ICPC2': [] },
		{ 'NAME': "OD03. HIV-Oral lesions", 'ICPC2': [] },
		{ 'NAME': "OD04. Oral Cancers", 'ICPC2': [] },
		{ 'NAME': "OD05. Other Oral Conditions (Manually review)", 'ICPC2': [ "D19", "D20", "D82", "D83" ] },

		{ 'NAME': "1.3.6 ENT conditions" },
		{ 'NAME': "EN01. Otitis media acute and chronic", 'ICPC2': [ "H71", "H72", "H74" ] },
		{ 'NAME': "EN02. Mastoiditis (Manually review)", 'ICPC2': [ "H99" ] },
		{ 'NAME': "EN03. Hearing loss", 'ICPC2': [ "H28", "H77", "H83", "H84", "H85", "H86" ] },
		{ 'NAME': "EN04. Rhinitis", 'ICPC2': [ "R07", "R97" ] },
		{ 'NAME': "EN05. Sinusitis", 'ICPC2': [ "R75" ] },
		{ 'NAME': "EN06. Epixtasis", 'ICPC2': [ "R06" ] },
		{ 'NAME': "EN07. Adenoid Hypertrophy (Manually review with EN14)", 'ICPC2': [ "R90" ] },
		{ 'NAME': "EN08. Foreign Body in nose ear and aero- digestive system", 'ICPC2': [ "H76", "R87", "D79" ] },
		{ 'NAME': "EN09. Infected pre-auricular sinuses and abscess (Manually review)", 'ICPC2': [ "R73", "R75" ] },
		{ 'NAME': "EN10. Otitis external", 'ICPC2': [ "H70" ] },
		{ 'NAME': "EN11. Mastoid abscess (Manually review)", 'ICPC2': [ "H99" ] },
		{ 'NAME': "EN12. Vertigo", 'ICPC2': [ "H82", "N17" ] },
		{ 'NAME': "EN13. Tonsillitis", 'ICPC2': [ "R76" ] },
		{ 'NAME': "EN14. Tonsillar hypertrophy (Manually review with EN07)", 'ICPC2': [ "R90" ] },
		{ 'NAME': "EN15. Tinnitus", 'ICPC2': [ "H03" ] },
		{ 'NAME': "EN16. Head and neck cancers", 'ICPC2': [ "H75", "T71", "T72" ], 'DIAGNOSIS_TYPE': [ ] },
		{ 'NAME': "EN17. Other ENT conditions", 'ICPC2': [ "H", "R08", "R09", "R21", "R23", "R72", "T78" ], 'subtract': [
			"EN01. Otitis media acute and chronic", "EN02. Mastoiditis (Manually review)", "EN03. Hearing loss",
			"EN04. Rhinitis", "EN05. Sinusitis", "EN06. Epixtasis", "EN07. Adenoid Hypertrophy (Manually review with EN14)",
			"EN08. Foreign Body in nose ear and aero- digestive system",
			"EN09. Infected pre-auricular sinuses and abscess (Manually review)", "EN10. Otitis external",
			"EN11. Mastoid abscess (Manually review)", "EN12. Vertigo", "EN13. Tonsillitis",
			"EN14. Tonsillar hypertrophy (Manually review with EN07)", "EN15. Tinnitus", "EN16. Head and neck cancers" ] },

		{ 'NAME': "1.3.7 Eye conditions" },
		{ 'NAME': "EC01. Allergic conjunctivitis", 'ICPC2': [ "F71" ] },
		{ 'NAME': "EC02. Bacterial conjunctivitis", 'ICPC2': [ "F70" ] },
		{ 'NAME': "EC03. Ophthalmia neonatorum", 'DIAGNOSIS_TYPE': [ 706 ] },
		{ 'NAME': "EC04. Other forms of conjunctivitis (Manually review)", 'ICPC2': [ "F73" ] },
		{ 'NAME': "EC05. Corneal ulcers / Keratitis", 'ICPC2': [ "F85" ] },
		{ 'NAME': "EC06. Un Operable Cataract (>6/60) (Manually review)", 'ICPC2': [ "F92" ] },
		{ 'NAME': "EC07. Operable Cataract (<6/60) (Manually review)", 'ICPC2': [ "F92" ] },
		{ 'NAME': "EC08. Refractive errors", 'ICPC2': [ "F91" ] },
		{ 'NAME': "EC09. Glaucoma", 'ICPC2': [ "F93" ] },
		{ 'NAME': "EC10. Trachoma", 'ICPC2': [ "F86" ] },
		{ 'NAME': "EC11. Vitamin A Deficiency", 'ICPC2': [] },
		{ 'NAME': "EC12. Ocular trauma and burns (Manually review)", 'ICPC2': [ "F79", "S14" ] },
		{ 'NAME': "EC13. Diabetic Retinopathy (all stages) (Manually review)", 'ICPC2': [ "F83" ] },
		{ 'NAME': "EC14. Chorioretinal, Macular & Vitreous Disorders (Manually review)", 'ICPC2': [ "F84" ] },
		{ 'NAME': "EC15. Uveitis (Manually review with EC16)", 'ICPC2': [ "F73" ] },
		{ 'NAME': "EC16. Endophthalmitis (Manually review with EC15)", 'ICPC2': [ "F73" ] },
		{ 'NAME': "EC17. Corneal scars (non trachomatous) (Manually review)", 'ICPC2': [ "F79", "F99" ] },
		{ 'NAME': "EC18. Tumours", 'ICPC2': [ "F74" ] },
		{ 'NAME': "EC19. Strabismus (all types)", 'ICPC2': [ "F95" ] },
		{ 'NAME': "EC20. Ptosis and other lid disorders", 'ICPC2': [ "F16", "F72" ] },
		{ 'NAME': "EC21. Squamous Cell Carcinoma of Conjunctiva (Manually review with EC21-24)", 'ICPC2': [ "F74" ] },
		{ 'NAME': "EC22. Retinoblastoma (Manually review with EC21-24)", 'ICPC2': [ "F74", "F81" ] },
		{ 'NAME': "EC23. Other Malignant Tumours (Manually review with EC21-24)", 'ICPC2': [ "F74" ] },
		{ 'NAME': "EC24. Other Benign Tumours/Growths (Manually review with EC21-24)", 'ICPC2': [ "F74" ] },
		{ 'NAME': "EC25. Other Eye Disorders", 'ICPC2': [ "F" ], 'subtract': [
			"EC01. Allergic conjunctivitis", "EC02. Bacterial conjunctivitis", "EC03. Ophthalmia neonatorum",
			"EC04. Other forms of conjunctivitis (Manually review)", "EC05. Corneal ulcers / Keratitis",
			"EC06. Un Operable Cataract (>6/60) (Manually review)", "EC07. Operable Cataract (<6/60) (Manually review)",
			"EC08. Refractive errors", "EC09. Glaucoma", "EC10. Trachoma", "EC11. Vitamin A Deficiency",
			"EC12. Ocular trauma and burns (Manually review)", "EC13. Diabetic Retinopathy (all stages) (Manually review)",
			"EC14. Chorioretinal, Macular & Vitreous Disorders (Manually review)",
			"EC15. Uveitis (Manually review with EC16)", "EC16. Endophthalmitis (Manually review with EC15)",
			"EC17. Corneal scars (non trachomatous) (Manually review)", "EC18. Tumours",
			"EC19. Strabismus (all types)", "EC20. Ptosis and other lid disorders",
			"EC21. Squamous Cell Carcinoma of Conjunctiva (Manually review with EC21-24)",
			"EC22. Retinoblastoma (Manually review with EC21-24)", "EC23. Other Malignant Tumours (Manually review with EC21-24)",
			"EC24. Other Benign Tumours/Growths (Manually review with EC21-24)", "EC26. Blindness" ] },
		{ 'NAME': "EC26. Blindness", 'ICPC2': [ "F94" ] },
		{ 'NAME': "EC27. Other eye conditions", 'ICPC2': [] },
		{ 'NAME': "EC28. Spectacles Dispensed", 'ICPC2': [] },

		{ 'NAME': "1.3.8 Mental Health" },
		{ 'NAME': "MH01. Anxiety disorders (Manually review with MH02)", 'ICPC2': [ "P74" ] },
		{ 'NAME': "MH02. Anxiety disorders due to gender based violence (Manually review with MH01)", 'ICPC2': [ "P74" ] },
		{ 'NAME': "MH03. Unipolar Depressive Disorder", 'ICPC2': [ "P76" ] },
		{ 'NAME': "MH04. Bipolar disorders", 'ICPC2': [ "P73" ] },
		{ 'NAME': "MH05. Schizophrenia", 'ICPC2': [ "P72" ] },
		{ 'NAME': "MH06. Post Traumatic Stress Disorder", 'ICPC2': [ "P82" ] },
		{ 'NAME': "MH07. Epilepsy", 'ICPC2': [ "N88" ] },
		{ 'NAME': "MH08. HIV related psychosis (Manually review)", 'ICPC2': [ "B90" ] },
		{ 'NAME': "MH09. Alzheimer's disease (Manually review with MH09-MH13)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "MH10. HIV related dementia (Manually review MH09-MH13)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "MH11. Alcohol Related Dementia (Manually review MH09-MH13)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "MH12. Dementia due to stroke (diabetes, hypertension) (Manually review MH09-MH13)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "MH13. Other forms of dementia (Manually review MH09-MH13)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "MH14. Other Adult Mental Health Conditions", 'ICPC2': [
			"P0", "P10", "P12", "P13", "P17", "P18", "P20", "P25", "P26", "P27", "P28",
			"P29", "P71", "P75", "P77", "P78", "P79", "P80", "P81", "P86", "P99" ],
			'subtract': [ "MH18. Delirium", "MH19. Intellectual disability" ], 'MIN_AGE_DAYS': 6570 },
		{ 'NAME': "MH15. Internet addiction", 'ICPC2': [] },
		{ 'NAME': "MH16. Alcohol Use Disorder", 'ICPC2': [ "P15", "P16" ] },
		{ 'NAME': "MH17. Substance (Drug) use disorder", 'ICPC2': [ "P19" ] },
		{ 'NAME': "MH18. Delirium", 'ICPC2': [ "P71" ] },
		{ 'NAME': "MH19. Intellectual disability", 'ICPC2': [ "P85" ] },
		{ 'NAME': "MH20. Autism spectrum disorders", 'ICPC2': [] },

		{ 'NAME': "1.3.9 Neurological Disorders" },
		{ 'NAME': "NE01. Aphasia or Loss of Language due to Stroke", 'ICPC2': [] },
		{ 'NAME': "NE02. Dysarthria or Speech Disorder due to Stroke (Manually review with NE06)", 'ICPC2': [ "N19" ] },
		{ 'NAME': "NE03. Parkinson's disease", 'ICPC2': [ "N87" ] },
		{ 'NAME': "NE04. Dementia or excessive forgetfulness due to advanced age (Manually review)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "NE05. Amyotrophic Lateral Sclerosis (ALS) (Manually review)", 'ICPC2': [ "N99" ] },
		{ 'NAME': "NE06. Speech disorders due to Head Injuries(penetrating or closed) (Manually review with NE02)", 'ICPC2': [ "N19" ] },
		{ 'NAME': "NE07. Persons in Coma / Emergency Care", 'ICPC2': [ "A07"] },
		{ 'NAME': "NE08. Alzheimer Disease (Manually review with MH08-MH13, NE04)", 'ICPC2': [ "P70" ] },
		{ 'NAME': "NE09. Down Syndrome (DS)", 'ICPC2': [] },
		{ 'NAME': "NE10. CP / PMLD", 'ICPC2': [] },
		{ 'NAME': "NE11. Child abuse and Neglect (Manually review)", 'ICPC2': [ "Z" ], 'MAX_AGE_DAYS': 6570 },
		{ 'NAME': "NE12. Attention Deficit Hyperactivity disorder (ADHD) (Manually review)", 'ICPC2': [ "P22", "P23", "P24" ] },
		{ 'NAME': "NE13. Learning Disability", 'ICPC2': [ "P24" ] },
		{ 'NAME': "NE14. Conduct disorders (Manually review)", 'ICPC2': [ "P22", "P23" ] },
		{ 'NAME': "NE15. Eating disorders (anorexia, Bulimia, other feeding)", 'ICPC2': [ "P86" ] },
		{ 'NAME': "NE16. Somatoform disorders", 'ICPC2': [ "P75" ] },
		{ 'NAME': "NE17. Sleeping Disorders", 'ICPC2': [ "P06" ] },
		{ 'NAME': "NE18. Enuresis/Encopresis", 'ICPC2': [ "P12", "P13" ] },
		{ 'NAME': "NE19. Other Childhood Mental Disorders", 'ICPC2': [ ] },
		{ 'NAME': "NE20. Mental illness due other Medical/ surgical conditions", 'ICPC2': [] },
		{ 'NAME': "NE21. Attempted Suicide/Self-harm", 'ICPC2': [ "P77" ] },

		{ 'NAME': "1.3.10 Chronic respiratory diseases" },
		{ 'NAME': "CR01. Asthma", 'ICPC2': [ "R96" ] },
		{ 'NAME': "CR02. Chronic Obstructive Pulmonary Disease (COPD)", 'ICPC2': [ "R95" ] },

		{ 'NAME': "1.3.11 Cancers" },
		{ 'NAME': "CA01. Cervical Cancer", 'ICPC2': [ "X75" ] },
		{ 'NAME': "CA02. Prostate Cancer", 'ICPC2': [ "Y77" ] },
		{ 'NAME': "CA03. Breast Cancer", 'ICPC2': [ "X76" ] },
		{ 'NAME': "CA04. Lung Cancer", 'ICPC2': [ "R84" ] },
		{ 'NAME': "CA05. Liver Cancer", 'DIAGNOSIS_TYPE': [ ] },
		{ 'NAME': "CA06. Colon Cancer", 'ICPC2': [ "D75" ] },
		{ 'NAME': "CA07. Kaposis Sarcoma", 'DIAGNOSIS_TYPE': [ ] },
		{ 'NAME': "CA08. Other Cancers", 'ICPC2': ["A79", "B72", "B73", "B74", "D74", "D76",
			"D77", "F74", "H75", "K72", "L71", "N74", "N76", "R85", "R92", "T73", "S77",
			"U75", "U76", "U77", "U79", "W72", "X77", "X81", "Y78"],
			'subtract': [ "CA01. Cervical Cancer", "CA02. Prostate Cancer", "CA03. Breast Cancer",
			"CA04. Lung Cancer", "CA05. Liver Cancer", "CA06. Colon Cancer", "CA07. Kaposis Sarcoma" ] },

		{ 'NAME': "1.3.12 Physiotherapy" },
		{ 'NAME': "PT01. Muscular disorders (Manually review)", 'ICPC2': [ "L18", "L19"] },
		{ 'NAME': "PT02. Joint dysfunction", 'ICPC2': [ "L08", "L09", "L10", "L11",
			 "L12", "L13", "L14", "L15", "L16", "L17",  "L20", "L77", "L78", "L79",
			 "L80", "L81", "L87", "L88", "L89", "L90", "L91", "L92", "L93", "L96", ] },
		{ 'NAME': "PT03. Soft tissue injuries (Manually review)", 'ICPC2': [ "L18", "L19" ] },
		{ 'NAME': "PT04. Chronic respiratory diseases", 'ICPC2': [ "R95", "R96"] },
		{ 'NAME': "PT05. Chest trauma/Injury (Manually review)", 'ICPC2': [ "A80", "A81", "L04" ] },
		{ 'NAME': "PT06. Paralysis due to spinal cord injury and other diseases (Manually review)", 'ICPC2': [ "N18" ] },
		{ 'NAME': "PT07. Cerebral Palsy/Delayed motor or sensory developmental milestones (CP)", 'ICPC2': [] },
		{ 'NAME': "PT08. Upper Motor Neuron lesions (UMN)", 'ICPC2': [] },
		{ 'NAME': "PT09. Facial palsy", 'ICPC2': [ "N91" ] },
		{ 'NAME': "PT10. Lower motor neuron lesions (LMN)", 'ICPC2': [] },
		{ 'NAME': "PT11. Gynaecological, obstetric and urogenital conditions", 'ICPC2': [] },
		{ 'NAME': "PT12. Amputee", 'DIAGNOSIS_TYPE': [ ] },
		{ 'NAME': "PT13. Altered Posture and gait (Manually review)", 'ICPC2': [ "L28", "N28" ] },
		{ 'NAME': "PT14. Injection neuritis/Acute flaccid paralysis", 'DIAGNOSIS_TYPE': [ ] },
		{ 'NAME': "PT15. Congenital abnormalities", 'ICPC2': [ "L82" ] },
		{ 'NAME': "PT16. Spine disorders e.g neck, thoracic, lumber, coccygeal pains",
			'ICPC2': [ "L01", "L02", "L03", "L83", "L84", "L85", "L86" ] },
		{ 'NAME': "PT17. Lymph oedema", 'ICPC2': [ "K07" ] },
		{ 'NAME': "PT18. Patients prescribed with assistive devices", 'ICPC2': [] },
		{ 'NAME': "PT19. Others", 'ICPC2': [] },

		{ 'NAME': "1.3.13 Occupational therapy conditions" },
		{ 'NAME': "OT01. Neuro-developmental Disorders", 'ICPC2': [] },
		{ 'NAME': "OT02. Sensory Integration disorders", 'ICPC2': [] },
		{ 'NAME': "OT03. Adult Neurological Disorders", 'ICPC2': [ "N85", "N86", "N87", "N93", "N99",
			 "L28", "N28" ], 'MIN_AGE_DAYS': 6570 },
		{ 'NAME': "OT04. Burn injuries", 'ICPC2': [ "S14" ] },
		{ 'NAME': "OT05. Post-burns contractures", 'ICPC2': [] },
		{ 'NAME': "OT06. Orthopaedic Conditions", 'ICPC2': [ "L08", "L09", "L10", "L11", "L12", "L92", "L93" ] },
		{ 'NAME': "OT07. Mental Health Conditions", 'ICPC2': [] },
		{ 'NAME': "OT08. Birth Defects and Trauma (Manually review)", 'ICPC2': [ "A90", "A94" ] },
		{ 'NAME': "OT09. Arthrogryposis", 'ICPC2': [] },
		{ 'NAME': "OT10. HIV / AIDS", 'ICPC2': [ "B90" ] },
		{ 'NAME': "OT11. Diabetes", 'ICPC2': [ "T89", "T90" ] },
		{ 'NAME': "OT12. Cancer", 'ICPC2': [] },
		{ 'NAME': "OT13. Other chronic conditions", 'ICPC2': [] },
		{ 'NAME': "OT14. Cardiac Conditions", 'ICPC2': [] },
		{ 'NAME': "OT15. Patients prescribed with assistive devices", 'ICPC2': [] },

		{ 'NAME': "1.3.14 Speech and Language Therapy" },
		{ 'NAME': "SL01. Speech and language delay/ disorder (Manually review)", 'ICPC2': [ "N19" ] },
		{ 'NAME': "SL02. Motor speech disorders (Manually review)", 'ICPC2': [ "N19" ] },
		{ 'NAME': "SL03. Hearing impairments", 'ICPC2': [ "H83", "H84", "H85", "H86" ] },
		{ 'NAME': "SL04. Voice disorders", 'ICPC2': [ "R23" ] },
		{ 'NAME': "SL05. Dysfluency /stammering", 'ICPC2': [ "P10" ] },
		{ 'NAME': "SL06. Acquired neurological disorders", 'ICPC2': [] },
		{ 'NAME': "SL07. Cleft lip and palate", 'ICPC2': [] }, # D20 or D83?
		{ 'NAME': "SL08. Others", 'ICPC2': [] },

		# Do we add in deaf and blind for these, for example?
		{ 'NAME': "1.3.15 Disabilities" },
		{ 'NAME': "DS01. Individuals with Difficulty in seeing", 'ICPC2': [ "F28", "F82", "F83", "F84", "F86", "F91", "F92", "F93", "F94" ] },
		{ 'NAME': "** DS01 ** (Manually review and add to above line)", 'ICPC2': [ "F99" ] },
		{ 'NAME': "DS02. Individuals with Albinism", 'ICPC2': [] },
		{ 'NAME': "DS03. Individuals with Difficulty in hearing", 'ICPC2': [ "H83", "H84", "H85", "H86" ] },
		{ 'NAME': "DS04. Individuals with Speech Difficulties", 'ICPC2': [ "N19" ] },
		{ 'NAME': "DS05. Individuals with delayed age specific motor development", 'ICPC2': [] },
		{ 'NAME': "DS06. Individuals with Dwarfism", 'ICPC2': [] },
		{ 'NAME': "DS07. Individuals with Difficulty understanding", 'ICPC2': [ "P24", "P28", "P85" ] },
		{ 'NAME': "DS08. Individuals with Difficulty in remembering", 'ICPC2': [ "P20", "P70" ] },
		{ 'NAME': "DS09. Individuals with Difficulty in reading", 'ICPC2': [] },
		{ 'NAME': "DS10. Individuals with Difficulty in writing", 'ICPC2': [] },
		{ 'NAME': "DS11. Individuals with Difficulty in self-care", 'ICPC2': [] },
		{ 'NAME': "DS12. Individuals with Mentally impairment", 'ICPC2': [] },
		{ 'NAME': "DS13. Individuals with Emotionally impairment", 'ICPC2': [] },

		{ 'NAME': "1.3.16 Cardiovascular diseases" },
		{ 'NAME': "CV01. Stroke/ Cardiovascular Accident(CVA)", 'ICPC2': [ "K90" ] },
		{ 'NAME': "CV02. Hypertension", 'ICPC2': [ "K86", "K87" ] },
		{ 'NAME': "CV03. Heart failure", 'ICPC2': [ "K77" ] },
		{ 'NAME': "CV04. Ischemic Heart Diseases", 'ICPC2': [ "K74", "K76" ] },
		{ 'NAME': "CV05. Rheumatic Heart Diseases", 'ICPC2': [ "K71" ] },
		{ 'NAME': "CV06. Chronic Heart Diseases", 'ICPC2': [ "K78", "K79", "K80", "K81", "K82", "K83", "K84" ] },
		{ 'NAME': "CV07. Other Cardiovascular Diseases", 'ICPC2': [ "K88", "K89", "K90", "K91", "K92", "K93", "K94", "K95", "K99" ] },

		{ 'NAME': "1.3.17 Endocrine and Metabolic Disorders" },
		{ 'NAME': "EM01. Diabetes mellitus", 'ICPC2': [ "T89", "T90", "W85" ] },
		{ 'NAME': "EM02. Thyroid Disease", 'ICPC2': [ "T81", "T85", "T86" ] },
		{ 'NAME': "EM03. Other Endocrine and Metabolic Diseases", 'ICPC2': [ "T07", "T08", "T70", "T80", "T82", "T83", "T87", "T91", "T92", "T93", "T99" ] },

		{ 'NAME': "1.3.18 Injuries" },
		{ 'NAME': "IN01. Jaw injuries (Manually review)", 'ICPC2': [ "L07" ] },
		{ 'NAME': "IN02a. Road Traffic Injuries Motor Vehicle (Manually review A80, A81)", 'ICPC2': [ "A80", "A81" ] },
		{ 'NAME': "IN02b. Road Traffic Injuries Motor Cycle (Manually review A80, A81)", 'ICPC2': [ "A80", "A81" ] },
		{ 'NAME': "IN02c. Road Traffic Injuries Bicycles (Manually review A80, A81)", 'ICPC2': [ "A80", "A81" ] },
		{ 'NAME': "IN02d. Road Traffic Injuries Others (Manually review A80, A81)", 'ICPC2': [ "A80", "A81" ] },
		{ 'NAME': "IN03. Injuries due to Gender based violence (Manually review A80, A81)", 'ICPC2': [ "A80", "A81" ] },
		{ 'NAME': "IN04. Injuries (Trauma due to other causes) (Manually review A80, A81)", 'ICPC2': [ "A80", "A81" ] },
		{ 'NAME': "IN05a. Animal bites Domestic (Manually reivew S13)", 'ICPC2': [ "S13" ] },
		{ 'NAME': "IN05b. Animal bites Wild (Manually reivew S13)", 'ICPC2': [ "S13" ] },
		{ 'NAME': "IN06. Snake bites (Manually reivew S13)", 'ICPC2': [ "S13" ] },
		{ 'NAME': "IN07. Insect bites", 'ICPC2': [ "S12" ] },

		{ 'NAME': "1.3.19 Minor Operations in OPD" },
		{ 'NAME': "MN01. Tooth extractions", 'ICPC2': [] },
		{ 'NAME': "MN02. Dental Fillings", 'ICPC2': [] },
		{ 'NAME': "MN03. Other Minor Operations", 'ICPC2': [] },

		{ 'NAME': "1.3.20 Neglected Tropical Diseases (NTDs)" },
		{ 'NAME': "NT01. Leishmaniasis (Manually review A78)", 'ICPC2': [ "A78" ] },
		{ 'NAME': "NT02. Lymphatic Filariasis (hydrocele) (Manually review A78)", 'ICPC2': [ "A78" ] },
		{ 'NAME': "NT03. Lymphatic Filariasis (Lympoedema) (Manually review A78)", 'ICPC2': [ "A78" ] },
		{ 'NAME': "NT04. Urinary Schistosomiasis (Manually review A78)", 'ICPC2': [ "A78" ] },
		{ 'NAME': "NT05. Intestinal Schistosomiasis (Manually review A78)", 'ICPC2': [ "A78" ] },
		{ 'NAME': "NT06. Onchocerciasis (Manually review A78)", 'ICPC2': [ "A78" ] },

		{ 'NAME': "1.3.21 Maternal conditions" },
		{ 'NAME': "MC01. Abortions due to Gender-Based Violence (GBV) (Manually review W82 W83)", 'ICPC2': [ "W82", "W83" ] },
		{ 'NAME': "MC02. Abortions due to other causes (Manually review W82 W83)", 'ICPC2': [ "W82", "W83" ] },
		{ 'NAME': "MC03. Number of Post Abortion women who received FP (Manually review W82 W83)", 'ICPC2': [ "W82", "W83" ] },
		{ 'NAME': "MC04. Malaria in pregnancy", 'DIAGNOSIS_TYPE': [ 18, 20 ] },
		{ 'NAME': "MC05. High blood pressure in pregnancy", 'DIAGNOSIS_TYPE': [ 216 ] },
		{ 'NAME': "MC06. Obstructed labour (Manually review W82 W83)", 'ICPC2': [ "W82", "W83" ] },
		{ 'NAME': "MC07. Puerperal sepsis", 'ICPC2': [ "W70" ] },
		{ 'NAME': "MC08. Haemorrhage related to pregnancy (APH)", 'ICPC2': [ "W03" ] },
		{ 'NAME': "MC09. Haemorrhage related to pregnancy (PPH)", 'ICPC2': [ "W17" ] },
		{ 'NAME': "MC10a. Breast cancer Total Screened", 'ICPC2': [] },
		{ 'NAME': "MC10b. Breast cancer Number with breast cancer", 'ICPC2': [ "X76" ] },
		{ 'NAME': "MC11a. Cervical cancer Total Screened", 'ICPC2': [] },
		{ 'NAME': "MC11b. Cervical cancer Number with cervical cancer (Manually review)", 'ICPC2': [ "X75" ] },

		{ 'NAME': "1.3.23 Risky Behaviours" },
		{ 'NAME': "RB01. Alcohol use", 'ICPC2': [ "P15", "P16" ] },
		{ 'NAME': "RB02. Tobacco use", 'ICPC2': [ "P17" ] },
		{ 'NAME': "RB03. Tobacco exposure", 'ICPC2': [] },

		{ 'NAME': "1.3.24 Emergency Medical Services" },
		{ 'NAME': "ES01. Number of emergency cases at the facility", 'ICPC2': [] },
		{ 'NAME': "ES02. Patients that receive care at the scene of emergency", 'ICPC2': [] },
		{ 'NAME': "ES03. Emergency cases that arrive at the facility using an Ambulance", 'ICPC2': [] },
		{ 'NAME': "ES04. Number of patients assessed for level of consciousness using GCS/ other comma score", 'ICPC2': [] },
		{ 'NAME': "ES05. Number of patients accessing care within 1hr in an emergency unit", 'ICPC2': [] },
		{ 'NAME': "ES06. Number of patients who develop complications within 24 hours", 'ICPC2': [] },
		{ 'NAME': "after management/care", 'ICPC2': [] },
		{ 'NAME': "ES07. Number of patients with hypoxemia administered with oxygen", 'ICPC2': [] },
		{ 'NAME': "ES08. Number of patients with external haemorrhages controlled", 'ICPC2': [] },
		{ 'NAME': "ES09a. Medical emergencies", 'ICPC2': [] },
		{ 'NAME': "ES09b. Obstetrics gynaecology emergencies (Manually tracking)", 'ICPC2': [] },
		{ 'NAME': "ES09c. Paediatric emergencies (Manually tracking)", 'ICPC2': [] },
		{ 'NAME': "ES09d. Surgical emergencies", 'ICPC2': [] },
		{ 'NAME': "ES09e. Road traffic Injuries (Manually sum IN02a-d)", 'ICPC2': [] },
		{ 'NAME': "ES09f. Burns", 'ICPC2': [ "S14" ] },
		{ 'NAME': "ES09g. Poisoning", 'ICPC2': [ "A84" ] },
		{ 'NAME': "ES10. Total number of Death in Emergency Unit (Manually tracking)", 'ICPC2': [] },
		{ 'NAME': "ES11. Number of Patients receiving vaccination for", 'ICPC2': [] },
		{ 'NAME': "ES11a.Tetanus", 'ICPC2': [] },
		{ 'NAME': "ES11b. Rabies", 'ICPC2': [] },
		{ 'NAME': "ES11c. Others", 'ICPC2': [] },
		]
	diag_map = {}
	for d in diagnoses:
		diag_map[d['NAME']] = [0,0,0,0,0,0,0,0,0,0,[]]
	visits = Visit.objects.filter(Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end) & (Q(status="CHOT") | Q(status="RESO")) )
	for v in visits:
		if not v.finishedDateTime:
			print "Warning: skipping unfinished visit: %s"%v
		index = 0
		if v.patient.birthDate:
			if v.patient.birthDate > (v.finishedDateTime - timedelta(days=28)).date():
				index = 0
			elif v.patient.birthDate > yearsago(5, v.finishedDateTime).date():
				index += 2
			elif v.patient.birthDate > yearsago(10, v.finishedDateTime).date():
				index += 4
			elif v.patient.birthDate > yearsago(20, v.finishedDateTime).date():
				index += 6
                        else:
				index += 8
		else:
			if v.patient.birthYear >= v.finishedDateTime.year - 4:
				index += 2
			elif v.patient.birthYear >= v.finishedDateTime.year - 9:
				index += 4
			elif v.patient.birthYear >= v.finishedDateTime.year - 19:
				index += 6
			else:
				index += 8
		if v.patient.gender == "F":
			index += 1
		total_visits[index] += 1
		if Visit.objects.filter(Q(patient=v.patient) & Q(finishedDateTime__gte=dt_start) & Q(finishedDateTime__lte=dt_end)).count() > 1:
			old_patient_visits[index].append(v.patient.id)
		if Visit.objects.filter(Q(patient=v.patient) & Q(finishedDateTime__lte=dt_start)).count() < 1:
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
				diag_map[d['NAME']][10].append("<A HREF=\"#%(diag_name)s_%(visit_id)s\" onclick=\"window.opener.location.href='/visit/%(visit_id)s/plan/';\">%(visit_id)s</A>"%{'visit_id': v.id, 'diag_name': d['NAME']})


	summary_rows.append({	'cat': "1.1 Outpatient Attendance",
				'lt28dm': "", 'lt28df': "",
				'lt4m': "", 'lt4f': "",
				'gt4m': "", 'gt4f': "",
				'gt9m': "", 'gt9f': "",
				'gt19m': "", 'gt19f': "",
				'visit_list': "",
				})
	summary_rows.append({	'cat': "New Attendance",
				'lt28dm': new_patient_visits[0],
				'lt28df': new_patient_visits[1],
				'lt4m': new_patient_visits[2],
				'lt4f': new_patient_visits[3],
				'gt4m': new_patient_visits[4],
				'gt4f': new_patient_visits[5],
				'gt9m': new_patient_visits[6],
				'gt9f': new_patient_visits[7],
				'gt19m': new_patient_visits[8],
				'gt19f': new_patient_visits[9],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "Re-Attendance",
				'lt28dm': len(old_patient_visits[0])-len(set(old_patient_visits[0])),
				'lt28df': len(old_patient_visits[1])-len(set(old_patient_visits[1])),
				'lt4m': len(old_patient_visits[2])-len(set(old_patient_visits[2])),
				'lt4f': len(old_patient_visits[3])-len(set(old_patient_visits[3])),
				'gt4m': len(old_patient_visits[4])-len(set(old_patient_visits[4])),
				'gt4f': len(old_patient_visits[5])-len(set(old_patient_visits[5])),
				'gt9m': len(old_patient_visits[6])-len(set(old_patient_visits[6])),
				'gt9f': len(old_patient_visits[7])-len(set(old_patient_visits[7])),
				'gt19m': len(old_patient_visits[8])-len(set(old_patient_visits[8])),
				'gt19f': len(old_patient_visits[9])-len(set(old_patient_visits[9])),
				'visit_list': "",
				})
	summary_rows.append({	'cat': "Total Attendance",
				'lt28dm': total_visits[0],
				'lt28df': total_visits[1],
				'lt4m': total_visits[2],
				'lt4f': total_visits[3],
				'gt4m': total_visits[4],
				'gt4f': total_visits[5],
				'gt9m': total_visits[6],
				'gt9f': total_visits[7],
				'gt19m': total_visits[8],
				'gt19f': total_visits[9],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "1.2 Outpatient Referrals",
				'lt28dm': "", 'lt28df': "",
				'lt4m': "", 'lt4f': "",
				'gt4m': "", 'gt4f': "",
				'gt9m': "", 'gt9f': "",
				'gt19m': "", 'gt19f': "",
				'visit_list': "",
				})
	summary_rows.append({   'cat': "Referrals to unit",
		                'lt28dm': "", 'lt28df': "",
				'lt4m': "-", 'lt4f': "-",
				'gt4m': "-", 'gt4f': "-",
				'gt9m': "", 'gt9f': "",
				'gt19m': "", 'gt19f': "",
				'visit_list': "",
				})
	summary_rows.append({   'cat': "Referrals from unit",
				'lt28dm': referrals_from[0],
				'lt28df': referrals_from[1],
				'lt4m': referrals_from[2],
				'lt4f': referrals_from[3],
				'gt4m': referrals_from[4],
				'gt4f': referrals_from[5],
				'gt9m': referrals_from[6],
				'gt9f': referrals_from[7],
				'gt19m': referrals_from[8],
				'gt19f': referrals_from[9],
				'visit_list': "",
				})
	summary_rows.append({	'cat': "1.3 Outpatient Diagnoses",
				'lt28dm': "", 'lt28df': "",
				'lt4m': "", 'lt4f': "",
				'gt4m': "", 'gt4f': "",
				'gt9m': "", 'gt9f': "",
				'gt19m': "", 'gt19f': "",
				'visit_list': "",
				})
	for d in diagnoses:
		if d.has_key("types") and len(d["types"]) == 0:
			summary_rows.append({
				'cat': d['NAME'],
				'lt28dm': "", 'lt28df': "",
				'lt4m': "-", 'lt4f': "-",
				'gt4m': "-", 'gt4f': "-",
				'gt9m': "", 'gt9f': "",
				'gt19m': "", 'gt19f': "",
				'visit_list': "-",
				})
		else:
			if d.has_key("subtract"):
				for subtraction in d['subtract']:
					for i in range(0,7):
						diag_map[d['NAME']][i]-=diag_map[subtraction][i]
					for v in diag_map[subtraction][10]:
                                                id_match = re.match(".*>(\d+)<", v)
                                                if id_match:
						    for i in diag_map[d['NAME']][10]:
                                                        if i.find(">" + id_match.group(1) + "<") > 0:
							    diag_map[d['NAME']][10].remove(i)
			summary_rows.append({
				'cat': d['NAME'],
				'lt28dm':  diag_map[d['NAME']][0],
				'lt28df':  diag_map[d['NAME']][1],
				'lt4m':  diag_map[d['NAME']][2],
				'lt4f':  diag_map[d['NAME']][3],
				'gt4m':  diag_map[d['NAME']][4],
				'gt4f':  diag_map[d['NAME']][5],
				'gt9m':  diag_map[d['NAME']][6],
				'gt9f':  diag_map[d['NAME']][7],
				'gt19m':  diag_map[d['NAME']][8],
				'gt19f':  diag_map[d['NAME']][9],
				'visit_list': ", ".join(diag_map[d['NAME']][10])
				})

	if dump_type == "CSV":
		return dump_csv( "hmis-105-%s-%s.csv"%(dt_start.strftime("%Y%m%d"),dt_end.strftime("%Y%m%d")), field_names, headers, summary_rows )
	elif dump_type == "TABLE":
		return dump_table(request, field_names, headers, summary_rows )
	else:
		raise "Invalid Dump Type"

@login_required
def med_pricelist(request):
	"""
	Download a PDF of the current price list
	"""
	# Gather the data
	data = list()
	import textwrap
	from ocemr.models import MedType
	for m in MedType.objects.all().order_by('title'):
		data.append([textwrap.fill(m.title, width=32, expand_tabs=False), m.cost])

	# Build the PDF
	from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Table
	from reportlab.lib.styles import getSampleStyleSheet
	import io

	# Per-page header
	def header(canvas, doc):
		canvas.saveState()
		canvas.setTitle("Medication Price List")
		P = Paragraph("Engeye Medication Price List as of %s" % today, styles['Heading1'])
		w, h = P.wrap(doc.width, doc.bottomMargin)
		P.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin)
		canvas.restoreState()

	# Initialize some basic elements and an in-memory file
	elements = []
	fh = io.BytesIO()
	styles = getSampleStyleSheet()
	doc = BaseDocTemplate(fh,showBoundary=1)
	today = datetime.today().strftime("%Y-%m-%d")

	# Make 2 columns
	frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width/2-6, doc.height, id='col1')
	frame2 = Frame(doc.leftMargin+doc.width/2+6, doc.bottomMargin, doc.width/2-6, doc.height, id='col2')

	# Add the data
	elements.append(Table(data))
	doc.addPageTemplates([PageTemplate(id='TwoCol',frames=[frame1,frame2], onPage=header), ])
	doc.build(elements)

	# Force the download
	fh.seek(0)
	return download(fh, "med_price_list_%s.pdf" % today)
