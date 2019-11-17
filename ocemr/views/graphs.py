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
from datetime import datetime, timedelta

def test_matplotlib(request):
	"""
	"""
	from pylab import figure, axes, pie, title
	import matplotlib

	f = figure(figsize=(6,6))
	ax = axes([0.1, 0.1, 0.8, 0.8])
	labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
	fracs = [15,30,45, 100]
	explode=(0, 0.1, 0, 0)
	pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)
	title('Raining Hogs and Dogs', bbox={'facecolor':'0.8', 'pad':5})

	canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(f)    
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	matplotlib.pyplot.close(f)
	return response

def vitals_bp(request, id):
	"""
	"""
	from ocemr.models import Patient, VitalType, Vital

	p = Patient.objects.get(pk=id)
	vt_bpS= VitalType.objects.get(title="BP - Systolic")
	v_bpS=Vital.objects.filter(patient=p,type=vt_bpS)
	bpS_date_list=[]
	bpS_data_list=[]
	for v in v_bpS:
		bpS_date_list.append(v.observedDateTime)
		bpS_data_list.append(v.data)

	vt_bpD= VitalType.objects.get(title="BP - Diastolic")
	v_bpD=Vital.objects.filter(patient=p,type=vt_bpD)
	bpD_date_list=[]
	bpD_data_list=[]
	for v in v_bpD:
		bpD_date_list.append(v.observedDateTime)
		bpD_data_list.append(v.data)

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt

	fig = plt.figure(figsize=(10,5),dpi=75)
	fig.interactive = False
	
	plt.title('Blood Pressure History for %s'%(p))
	plt.grid(True)
	plt.axhspan(ymin=90, ymax=140, color='b',alpha=.2)
	plt.axhspan(ymin=60, ymax=90, color='g',alpha=.2)
	plt.axhline(y=120, color='b')
	plt.axhline(y=80, color='g')
	plt.plot(bpS_date_list, bpS_data_list, 'o-', color='r', label="systolic")
	plt.plot(bpD_date_list, bpD_data_list, 'o-', color='m', label="diastolic")
	plt.ylabel('mmHg')
	plt.legend(loc=0)
	fig.autofmt_xdate()

	fig.text(0.15, 0.33, 'OCEMR',
		fontsize=150, color='gray',
		alpha=0.07)

	plt.draw()
	canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)    
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	plt.close(fig)
	return response


def vitals_temp(request, id):
	"""
	"""
	from ocemr.models import Patient, VitalType, Vital
	p = Patient.objects.get(pk=id)
	vt_temp= VitalType.objects.get(title="Temp")
	v_temp=Vital.objects.filter(patient=p,type=vt_temp)
	temp_date_list=[]
	temp_data_list=[]
	for v in v_temp:
		temp_date_list.append(v.observedDateTime)
		temp_data_list.append(v.data)

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt

	fig = plt.figure(num=1,figsize=(10,5),dpi=75)
	fig.interactive = False
	plt.title('Temperature History for %s'%(p))
	plt.grid(True)
	plt.axhspan(ymin=36.3, ymax=37.3, color='g',alpha=.5)
	plt.axhline(y=37, color='g')
	plt.plot(temp_date_list,temp_data_list, 'o-', color='r', label="Temp")
	plt.ylabel('degrees C')
	plt.legend(loc=0)
	fig.autofmt_xdate()

	fig.text(0.15, 0.33, 'OCEMR',
		fontsize=150, color='gray',
		alpha=0.07)

	plt.draw()
	canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)    
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	matplotlib.pyplot.close(fig)
	return response


def vitals_hrrr(request, id):
	"""
	"""
	from ocemr.models import Patient, VitalType, Vital
	p = Patient.objects.get(pk=id)
	vt_hr= VitalType.objects.get(title="HR")
	v_hr=Vital.objects.filter(patient=p,type=vt_hr)
	hr_date_list=[]
	hr_data_list=[]
	for v in v_hr:
		hr_date_list.append(v.observedDateTime)
		hr_data_list.append(v.data)
	vt_rr= VitalType.objects.get(title="RR")
	v_rr=Vital.objects.filter(patient=p,type=vt_rr)
	rr_date_list=[]
	rr_data_list=[]
	for v in v_rr:
		rr_date_list.append(v.observedDateTime)
		rr_data_list.append(v.data)

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt

	fig = plt.figure(num=1,figsize=(10,5),dpi=75)
	fig.interactive = False
	plt.title('Heart / Resp Rate History for %s'%(p))
	plt.grid(True)
	plt.axhspan(ymin=60, ymax=80, color='b',alpha=.33)
	plt.axhspan(ymin=10, ymax=20, color='g',alpha=.33)
	plt.axhline(y=12, color='g')
	plt.plot(hr_date_list,hr_data_list, 'o-', color='r',label="Heart")
	plt.plot(rr_date_list,rr_data_list, 'o-', color='m',label="Resp")
	plt.ylabel('rate (bpm)')
	l = plt.legend(loc=0)
	fig.autofmt_xdate()

	fig.text(0.15, 0.33, 'OCEMR',
		fontsize=150, color='gray',
		alpha=0.07)

	plt.draw()
	canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)    
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	matplotlib.pyplot.close(fig)
	return response

def vitals_height_weight(request, id):
	"""
	"""
	from ocemr.models import Patient, VitalType, Vital
	p = Patient.objects.get(pk=id)
	vt_height= VitalType.objects.get(title="Height")
	v_height=Vital.objects.filter(patient=p,type=vt_height)
	height_date_list=[]
	height_data_list=[]
	for v in v_height:
		height_date_list.append(v.observedDateTime)
		height_data_list.append(v.data)
	vt_weight= VitalType.objects.get(title="Weight")
	v_weight=Vital.objects.filter(patient=p,type=vt_weight)
	weight_date_list=[]
	weight_data_list=[]
	for v in v_weight:
		weight_date_list.append(v.observedDateTime)
		weight_data_list.append(v.data)

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt

	fig = plt.figure(num=1,figsize=(10,5),dpi=75)
	fig.interactive = False
	plt.title('Height / Weight History for %s'%(p))
	plt.grid(True)
	#plt.axhspan(ymin=36.75, ymax=37.25, color='g',alpha=.5)
	plt.plot(height_date_list,height_data_list, 'o-', color='r',label="Height")
	plt.plot(weight_date_list,weight_data_list, 'o-', color='m',label="Weight")
	plt.ylabel('cm, kg')
	plt.legend(loc=0)
	fig.autofmt_xdate()

	fig.text(0.15, 0.33, 'OCEMR',
		fontsize=150, color='gray',
		alpha=0.07)

	plt.draw()
	canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)    
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	matplotlib.pyplot.close(fig)
	return response

def vitals_spo2_o2(request, id):
	"""
	"""
	from ocemr.models import Patient, VitalType, Vital
	p = Patient.objects.get(pk=id)
	vt= VitalType.objects.get(title="SpO2")
	vitals=Vital.objects.filter(patient=p,type=vt)
	date_list=[]
	data_list=[]
	for v in vitals:
		date_list.append(v.observedDateTime)
		data_list.append(v.data)
	vt2= VitalType.objects.get(title="Oxygen")
	vitals2=Vital.objects.filter(patient=p,type=vt2)
	date_list2=[]
	data_list2=[]
	for v in vitals2:
		date_list2.append(v.observedDateTime)
		data_list2.append(v.data)

	import matplotlib
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt

	fig = plt.figure(num=1,figsize=(10,5),dpi=75)
	fig.interactive = False
	plt.title('SpO2 / Oxygen History for %s'%(p))
	plt.grid(True)
	#plt.axhspan(ymin=36.75, ymax=37.25, color='g',alpha=.5)
	plt.plot(date_list,data_list, 'o-', color='r',label="SpO2")
	plt.plot(date_list2,data_list2, 'o-', color='m',label="Oxygen")
	plt.ylabel('percent')
	plt.legend(loc=0)
	fig.autofmt_xdate()

	fig.text(0.15, 0.33, 'OCEMR',
		fontsize=150, color='gray',
		alpha=0.07)

	plt.draw()
	canvas = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)
	response = HttpResponse(content_type='image/png')
	canvas.print_png(response)
	matplotlib.pyplot.close(fig)
	return response

def vitals_graphs_index(request, id):
	return render(request, 'popup_graphs_index.html', {'id': id, })
