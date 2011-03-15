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

from django import forms
from django.db.models import get_model

from django.contrib.auth.models import User


import widgets

class EditPatientNoteForm(forms.Form):
	from models import Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	NoteText = forms.CharField(widget=forms.Textarea)
	def __init__(self, p, *args, **kwargs):
		
		super(EditPatientNoteForm, self).__init__(*args, **kwargs)
		self.fields['patient'].initial=p.id
		self.fields['NoteText'].initial=p.scratchNote
		
class EditPatientNameForm(forms.Form):
	familyName = forms.CharField(label='Last Name')
	givenName = forms.CharField(label='First Name')
	middleName = forms.CharField(label='Middle Name',required=False)

class EditPatientGenderForm(forms.Form):
	from models import Patient
	gender = forms.ChoiceField(label='Gender',choices=Patient.GENDER_CHOICES)

class EditPatientAgeForm(forms.Form):
	birthYear = forms.IntegerField(required=False)
	birthDate = forms.DateField(required=False,widget=widgets.CalendarWidget)
	def clean_birthYear(self):
		import datetime
		MAX_AGE=160
		CURRENT_YEAR=datetime.datetime.now().year
		data = self.cleaned_data['birthYear']
		if data < MAX_AGE:
			new_data = CURRENT_YEAR - data
		elif data > (CURRENT_YEAR-MAX_AGE):
			new_data = data
		else:
			raise forms.ValidationError("Birth Year must be less than %d or greater than %d."%(MAX_AGE, CURRENT_YEAR-MAX_AGE))
		return new_data
		

class EditPatientVillageForm(forms.Form):
        village = forms.CharField(
			widget=widgets.JQueryAutoComplete(
				'/autocomplete_name/ocemr/Village/'
				)
			)
	def clean_village(self):
		data = self.cleaned_data['village']
		from models import Village
		v, is_new = Village.objects.get_or_create(name=data)
		if is_new:
			v.save()
		return v



class NewScheduledVisitForm(forms.ModelForm):
	from models import Patient
	from models import Visit
        scheduledDate = forms.DateField(required=False,widget=widgets.CalendarWidget)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	scheduledBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	status = forms.CharField(widget=forms.HiddenInput)

	def __init__(self, user, p, *args, **kwargs):
		
		super(NewScheduledVisitForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['scheduledBy'].initial=user.id
		self.fields['patient'].initial=p.id
		self.fields['status'].initial='SCHE'
		

        class Meta:
                model = get_model('ocemr','Visit')
                exclude = [ 'followupTo',
				'seenDateTime',
				'claimedDateTime', 'claimedBy',
				'finishedDateTime', 'finishedBy',
				'resolvedDateTime', 'resolvedBy',
				'cost',
				 ]

	def clean_scheduledDate(self):
		data = self.cleaned_data['scheduledDate']
		if data == "" or data == None:
			from datetime import datetime
			return datetime.now().date()
		return data

class EditScheduledVisitForm(forms.Form):
	scheduledBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
        scheduledDate = forms.DateField()
        reasonDetail = forms.CharField(widget=forms.Textarea)

	def __init__(self, v, user, *args, **kwargs):
		
		super(EditScheduledVisitForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['scheduledBy'].initial=user.id
		self.fields['scheduledDate'].initial=v.scheduledDate
		self.fields['reasonDetail'].initial=v.reasonDetail

class EditVisitSeenForm(forms.Form):
        seenDate = forms.DateField()
        seenTime = forms.TimeField()


class EditVisitReasonForm(forms.Form):
        reasonDetail = forms.CharField(widget=forms.Textarea)

	def __init__(self, v, *args, **kwargs):
		
		super(EditVisitReasonForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['reasonDetail'].initial=v.reasonDetail
		
class NewWalkinVisitForm(forms.ModelForm):
	from models import Patient
	from models import Visit
        scheduledDate = forms.DateField(widget=forms.HiddenInput)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	scheduledBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
        seenDateTime = forms.DateTimeField(widget=forms.HiddenInput)
	status = forms.CharField(widget=forms.HiddenInput)
	reason = forms.CharField(widget=forms.HiddenInput)

	def __init__(self, user, p, *args, **kwargs):
		
		super(NewWalkinVisitForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['scheduledBy'].initial=user.id
		self.fields['patient'].initial=p.id
		self.fields['status'].initial='WAIT'
		self.fields['reason'].initial='NEW'
		from datetime import datetime
		self.fields['scheduledDate'].initial=datetime.today().date()
		self.fields['seenDateTime'].initial=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		

        class Meta:
                model = get_model('ocemr','Visit')
                exclude = [ 'followupTo',
				'claimedDateTime', 'claimedBy',
				'finishedDateTime', 'finishedBy',
				'resolvedDateTime', 'resolvedBy',
				'cost',
				 ]

	def clean_scheduledDate(self):
		data = self.cleaned_data['scheduledDate']
		if data == "" or data == None:
			from datetime import datetime
			return datetime.now().date()
		return data

class NewPatientForm(forms.ModelForm):
        birthDate = forms.DateField(required=False,widget=widgets.CalendarWidget)
        village = forms.CharField(
			widget=widgets.JQueryAutoComplete(
				'/autocomplete_name/ocemr/Village/'
				)
			)
	createdBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	
	def __init__(self, user, *args, **kwargs):
		
		super(NewPatientForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['createdBy'].initial=user.id
		

        class Meta:
                model = get_model('ocemr','Patient')
                exclude = [ 'createdDateTime', 'status', 'scratchNote',]

	def clean_birthYear(self):
		import datetime
		MAX_AGE=160
		CURRENT_YEAR=datetime.datetime.now().year
		data = self.cleaned_data['birthYear']
		if data < MAX_AGE:
			new_data = CURRENT_YEAR - data
		elif data > (CURRENT_YEAR-MAX_AGE):
			new_data = data
		else:
			raise forms.ValidationError("Birth Year must be less than %d or greater than %d."%(MAX_AGE, CURRENT_YEAR-MAX_AGE))
		return new_data
		
	def clean_village(self):
		data = self.cleaned_data['village']
		from models import Village
		v, is_new = Village.objects.get_or_create(name=data)
		if is_new:
			v.save()
		return v

class PatientSearchForm(forms.Form):
	name = forms.CharField(label='Name', required=False)
        village = forms.CharField(
			widget=widgets.JQueryAutoComplete(
				'/autocomplete_name/ocemr/Village/'
				),
			required=False,
			)


class NewVisitSymptomForm(forms.ModelForm):
	from models import Visit, SymptomType
        notes = forms.CharField(widget=forms.Textarea)
	type = forms.ModelChoiceField(queryset=SymptomType.objects.all(),widget=forms.HiddenInput)
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	def __init__(self, v, st, *args, **kwargs):
		
		super(NewVisitSymptomForm, self).__init__(*args, **kwargs)
		self.fields['type'].initial=st
		self.fields['visit'].initial=v
		

        class Meta:
                model = get_model('ocemr','VisitSymptom')
class EditVisitSymptomForm(forms.Form):
	notes = forms.CharField(widget=forms.Textarea)

class ConfirmDeleteForm(forms.Form):
	doDelete = forms.BooleanField(
		label="Really Delete it?",
		widget=forms.Select(
			choices=(
				(False,'No'),
				(True,'Yes'),
				)
			),
		required=False
	)

class NewVitalsForm(forms.Form):
	from models import Visit, Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	observedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	observedDateTime = forms.DateTimeField(widget=forms.HiddenInput,required=False)

	temp_in = forms.CharField(
		label="Temp",
		help_text="in celcius or fahrenheit. (valid examples \"98.7f\" or \"37 c\".)",
		required=False
		)
	bloodPressureSystolic = forms.IntegerField(
		label="BP-Systolic",
		help_text="in hhmg.",
required=False
		)
	bloodPressureDiastolic = forms.IntegerField(
		label="BP-Diastolic",
		help_text="in hhmg.",
		required=False
		)
	heartRate = forms.IntegerField(
		label="Heart Rate",
		help_text="in beats per minute.",
		required=False
		)
	respiratoryRate = forms.IntegerField(
		label="Respiratory Rate",
		help_text="in breaths per minute.",
		required=False
		)
	height_in = forms.CharField(
		label="Height",
		help_text="in centimeters or inches. (valid examples \"177 cm\" or \"70.25in\".)",
		required=False
		)
	weight_in = forms.CharField(
		label="Weight",
		help_text="in kilograms or pounds. (valid examples \"77.5 kg\" or \"150lb\".)",
		required=False
		)

	def __init__(self, v, user, *args, **kwargs):
		
		super(NewVitalsForm, self).__init__(*args, **kwargs)
		self.fields['visit'].initial=v.id
		self.fields['patient'].initial=v.patient.id
		self.fields['observedBy'].initial=user.id

	def clean_observedDateTime(self):
		from datetime import datetime
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	def clean_temp_in(self):
		data = str(self.cleaned_data['temp_in'])
		if len(data) > 0:
			if data.strip()[-1].lower() == 'f':
				d = (float(data.strip()[0:-1])-32.0)*(5.0/9.0)
			elif data.strip()[-1].lower() == 'c':
				d = float(data.strip()[0:-1])
			else:
				raise forms.ValidationError("Please include a unit (c or f).")
		else:
			return ""
		return d
	def clean_height_in(self):
		data = str(self.cleaned_data['height_in'])
		if len(data) > 0:
			if data.strip()[-2].lower() == 'i':
				d = float(data.strip()[0:-2])*2.54
			elif data.strip()[-2].lower() == 'c':
				d = float(data.strip()[0:-2])
			else:
				raise forms.ValidationError("Please include a unit (cm or in).")
		else:
			return ""
		return d
	def clean_weight_in(self):
		data = str(self.cleaned_data['weight_in'])
		if len(data) > 0:
			if data.strip()[-2].lower() == 'l':
				d = float(data.strip()[0:-2])/2.205
			elif data.strip()[-2].lower() == 'k':
				d = float(data.strip()[0:-2])
			else:
				raise forms.ValidationError("Please include a unit (kg or lb).")
		else:
			return ""
		return d

#class NewVitalForm(forms.ModelForm):
#	from models import Visit, VitalType, Patient
#	type = forms.ModelChoiceField(queryset=VitalType.objects.all(),widget=forms.HiddenInput)
#	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
#	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
#	observedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
#	data_in = forms.CharField()
#	def __init__(self, v, vt, user, *args, **kwargs):
#		
#		super(NewVitalForm, self).__init__(*args, **kwargs)
#		self.fields['type'].initial=vt.id
#		self.fields['visit'].initial=v.id
#		self.fields['patient'].initial=v.patient.id
#		self.fields['observedBy'].initial=user.id
#
#	class Meta:
#		model = get_model('ocemr','Vital')
#                exclude = [ 'observedDateTime', 'data']
#
#	def clean_data_in(self):
#		data = str(self.cleaned_data['data_in'])
#		#raise forms.ValidationError("DATA:%s"%(data))
#		from models import VitalType
#		vt = self.cleaned_data['type']
#		if vt.title == "Temp":
#			if data.strip()[-1].lower() == 'f':
#				d = (float(data.strip()[0:-1])-32.0)*(5.0/9.0)
#			elif data.strip()[-1].lower() == 'c':
#				d = float(data.strip()[0:-1])
#			else:
#				raise forms.ValidationError("Please include a unit (c or f).")
#		elif vt.title == "Weight":
#			if data.strip()[-2].lower() == 'l':
#				d = float(data.strip()[0:-2])/2.205
#			elif data.strip()[-2].lower() == 'k':
#				d = float(data.strip()[0:-2])
#			else:
#				raise forms.ValidationError("Please include a unit (kg or lb).")
#		elif vt.title == "Height":
#			if data.strip()[-2].lower() == 'i':
#				d = float(data.strip()[0:-2])*2.54
#			elif data.strip()[-2].lower() == 'c':
#				d = float(data.strip()[0:-2])
#			else:
#				raise forms.ValidationError("Please include a unit (cm or in).")
#		else:
#			try:
#				d = float(data.strip())
#			except:
#				raise forms.ValidationError("Please enter a number only.")
#		self.instance.data=d
#		return d
#
#
class NewExamNoteForm(forms.ModelForm):
	from models import Visit, ExamNoteType, Patient
	type = forms.ModelChoiceField(queryset=ExamNoteType.objects.all(),widget=forms.HiddenInput)
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, v, ent, user, *args, **kwargs):
		
		super(NewExamNoteForm, self).__init__(*args, **kwargs)
		self.fields['type'].initial=ent.id
		self.fields['visit'].initial=v.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','ExamNote')
                exclude = [ 'addedDateTime']

class NewReferralForm(forms.ModelForm):
	from models import Visit, Patient
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, v, user, *args, **kwargs):
		
		super(NewReferralForm, self).__init__(*args, **kwargs)
		self.fields['visit'].initial=v.id
		self.fields['patient'].initial=v.patient.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','Referral')
                exclude = [ 'addedDateTime']

class EditReferralForm(forms.Form):
	to = forms.CharField()
	reason = forms.CharField(widget=forms.Textarea)

class EditExamNoteForm(forms.Form):
	note = forms.CharField(widget=forms.Textarea)

class NewAllergyForm(forms.ModelForm):
	from models import Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, v, user, *args, **kwargs):
		
		super(NewAllergyForm, self).__init__(*args, **kwargs)
		self.fields['patient'].initial=v.patient.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','Allergy')
                exclude = [ 'addedDateTime']

class NewImmunizationLogForm(forms.ModelForm):
	from models import Visit, Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, v, user, *args, **kwargs):
		
		super(NewImmunizationLogForm, self).__init__(*args, **kwargs)
		self.fields['patient'].initial=v.patient.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','ImmunizationLog')
                exclude = [ 'addedDateTime']

class NewLabNoteForm(forms.ModelForm):
	from models import Visit, Lab
	lab = forms.ModelChoiceField(queryset=Lab.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, l, user, *args, **kwargs):
		
		super(NewLabNoteForm, self).__init__(*args, **kwargs)
		self.fields['lab'].initial=l.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','LabNote')
                exclude = [ 'addedDateTime']

class CompleteLabForm(forms.Form):
	result = forms.CharField()

class NewDiagnosisForm(forms.ModelForm):
	from models import Patient, Visit
        type = forms.CharField(
			widget=widgets.JQueryAutoContains(
				'/autosearch_title/ocemr/DiagnosisType/'
				)
			)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	diagnosedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	status = forms.CharField(widget=forms.HiddenInput)
	
	def __init__(self, visit, user, *args, **kwargs):
		
		super(NewDiagnosisForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['diagnosedBy'].initial=user.id
		self.fields['patient'].initial=visit.patient.id
		self.fields['visit'].initial=visit.id
		self.fields['status'].initial='NEW'
		

        class Meta:
                model = get_model('ocemr','Diagnosis')
                exclude = [ 'diagnosedDateTime' ]

	def clean_type(self):
		data = self.cleaned_data['type']
		from models import DiagnosisType
		d = DiagnosisType.objects.get(title=data)
		return d

class EditDiagnosisNotesForm(forms.Form):
	notes = forms.CharField(widget=forms.Textarea)
	def __init__(self, d, *args, **kwargs):
		from datetime import datetime
		super(EditDiagnosisNotesForm, self).__init__(*args, **kwargs)
		self.fields['notes'].initial=d.notes

class NewMedForm(forms.ModelForm):
	from models import Diagnosis, Patient, Visit
        type = forms.CharField(
			widget=widgets.JQueryAutoContains(
				'/autosearch_title/ocemr/MedType/'
				)
			)
	diagnosis = forms.ModelChoiceField(queryset=Diagnosis.objects.all(),widget=forms.HiddenInput)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	status = forms.CharField(widget=forms.HiddenInput)
	
	def __init__(self, diagnosis, user, *args, **kwargs):
		
		super(NewMedForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['addedBy'].initial=user.id
		self.fields['diagnosis'].initial=diagnosis.id
		self.fields['patient'].initial=diagnosis.patient.id
		self.fields['visit'].initial=diagnosis.visit.id
		self.fields['status'].initial='ORD'
		

        class Meta:
                model = get_model('ocemr','Med')
                exclude = [ 'addedDateTime', 'dispensedDateTime', 'dispensedBy' ]

	def clean_type(self):
		data = self.cleaned_data['type']
		from models import MedType
		d = MedType.objects.get(title=data)
		return d

class NewMedNoteForm(forms.ModelForm):
	from models import Med
	med = forms.ModelChoiceField(queryset=Med.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, m, user, *args, **kwargs):
		
		super(NewMedNoteForm, self).__init__(*args, **kwargs)
		self.fields['med'].initial=m.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','MedNote')
                exclude = [ 'addedDateTime']

class NewCashLogForm(forms.ModelForm):
	from models import Visit, Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	visit = forms.ModelChoiceField(queryset=Visit.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	def __init__(self, v, user, *args, **kwargs):
		
		super(NewCashLogForm, self).__init__(*args, **kwargs)
		self.fields['patient'].initial=v.patient.id
		self.fields['visit'].initial=v.id
		self.fields['addedBy'].initial=user.id

	class Meta:
		model = get_model('ocemr','CashLog')
                exclude = [ 'addedDateTime']

class EditBillAmountForm(forms.Form):
	amount = forms.FloatField(widget=forms.TextInput)

	def __init__(self, a, *args, **kwargs):
		super(EditBillAmountForm, self).__init__(*args, **kwargs)
		self.fields['amount'].initial = a

class SelectDateForm(forms.Form):
	date = forms.DateField(required=False,widget=widgets.CalendarWidget)

class SelectDateRangeForm(forms.Form):
	date_start = forms.DateField(required=False,widget=widgets.CalendarWidget)
	date_end = forms.DateField(required=False,widget=widgets.CalendarWidget)

class ClinicianTallyReportForm(forms.Form):
	date_start = forms.DateField(required=False,widget=widgets.CalendarWidget)
	date_end = forms.DateField(required=False,widget=widgets.CalendarWidget)
	dump_type = forms.ChoiceField(choices=(
				('TABLE', 'display'),
				('CSV', 'csv'),
				('G_PIE', 'Pie Graph'),
			)
		)

class DiagnosisTallyReportForm(forms.Form):
	date_start = forms.DateField(required=False,widget=widgets.CalendarWidget)
	date_end = forms.DateField(required=False,widget=widgets.CalendarWidget)
	age_min = forms.IntegerField(required=False)
	age_max = forms.IntegerField(required=False)
	dump_type = forms.ChoiceField(choices=(
				('TABLE', 'display'),
				('CSV', 'csv'),
				('G_PIE', 'Pie Graph'),
			)
		)

class EditMedForm(forms.Form):
        type = forms.CharField(
			widget=widgets.JQueryAutoContains(
				'/autosearch_title/ocemr/MedType/'
				)
			)
	dosage = forms.CharField()
	dispenseAmount = forms.CharField(required=False)
		
	def clean_type(self):
		data = self.cleaned_data['type']
		from models import MedType
		d = MedType.objects.get(title=data)
		return d

class MergePatientForm(forms.Form):
	duplicateID = forms.IntegerField()
