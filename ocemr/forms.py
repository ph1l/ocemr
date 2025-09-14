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

from django import forms
from django.apps import apps

from django.contrib.auth.models import User


import widgets

class EditPatientNoteForm(forms.Form):
	from models import Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	NoteText = forms.CharField(widget=forms.Textarea,required=False)
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
				'/autospel_name/ocemr/Village/'
				)
			)
	def clean_village(self):
		data = self.cleaned_data['village']
		from models import Village
		v, is_new = Village.objects.get_or_create(name=data)
		if is_new:
			v.save()
		return v

class EditPatientPhoneForm(forms.Form):
	phone = forms.CharField(label='Phone')

class EditPatientEmailForm(forms.Form):
	email = forms.EmailField(label='e-mail')

class EditPatientAltContactNameForm(forms.Form):
	alt_contact_name = forms.CharField(label='Name')

class EditPatientAltContactPhoneForm(forms.Form):
	alt_contact_phone = forms.CharField(label='Phone')

class NewScheduledVisitForm(forms.ModelForm):
	from models import Patient
	from models import Visit
        scheduledDate = forms.DateField(required=False,widget=widgets.CalendarWidget)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	scheduledBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	type = forms.CharField(widget=forms.HiddenInput)
	status = forms.CharField(widget=forms.HiddenInput)

	def __init__(self, user, p, *args, **kwargs):
		
		super(NewScheduledVisitForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['scheduledBy'].initial=user.id
		self.fields['patient'].initial=p.id
		self.fields['type'].initial='OUT'
		self.fields['status'].initial='SCHE'
		

        class Meta:
                model = apps.get_model('ocemr','Visit')
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

class EditVisitTypeForm(forms.Form):
    from models import Visit
    visit_type = forms.ChoiceField(label='Visit Type',choices=Visit.VISIT_TYPE_CHOICES)

class NewWalkinVisitForm(forms.ModelForm):
	from models import Patient
	from models import Visit
        scheduledDate = forms.DateField(widget=forms.HiddenInput)
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	scheduledBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
        seenDateTime = forms.DateTimeField(widget=forms.HiddenInput)
	type = forms.CharField(widget=forms.HiddenInput)
	status = forms.CharField(widget=forms.HiddenInput)
	reason = forms.CharField(widget=forms.HiddenInput)

	def __init__(self, user, p, *args, **kwargs):
		
		super(NewWalkinVisitForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['scheduledBy'].initial=user.id
		self.fields['patient'].initial=p.id
		self.fields['type'].initial='OUT'
		self.fields['status'].initial='WAIT'
		self.fields['reason'].initial='NEW'
		from datetime import datetime
		self.fields['scheduledDate'].initial=datetime.today().date()
		self.fields['seenDateTime'].initial=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		

        class Meta:
                model = apps.get_model('ocemr','Visit')
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
				'/autospel_name/ocemr/Village/'
				)
			)
	createdBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	
	def __init__(self, user, *args, **kwargs):
		
		super(NewPatientForm, self).__init__(*args, **kwargs)
		#raise(" | ".join(dir(self.fields['createdBy'])))
		self.fields['createdBy'].initial=user.id
		

        class Meta:
                model = apps.get_model('ocemr','Patient')
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
				'/autospel_name/ocemr/Village/'
				),
			required=False,
			)
	pid = forms.IntegerField(label='Patient ID#', required=False)


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
                model = apps.get_model('ocemr','VisitSymptom')
                fields = "__all__"
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
		help_text="in mmHg.",
required=False
		)
	bloodPressureDiastolic = forms.IntegerField(
		label="BP-Diastolic",
		help_text="in mmHg.",
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
	spo2_in = forms.CharField(
		label="SpO2",
		help_text="in percent. (valid examples \"80\" or \"98%\".)",
		required=False
		)
	oxygen_in = forms.CharField(
		label="% Oxygen",
		help_text="in percent. (valid examples \"20\" or \"30%\".)",
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
		message="Must be a number followed by a unit (c or f)."
		data = str(self.cleaned_data['temp_in']).strip()
		if len(data) == 0:
			return ""
		if len(data) >= 2:
			if data[-1].lower() == 'f':
				try:
					d = (float(data[0:-1])-32.0)*(5.0/9.0)
				except:
					raise forms.ValidationError(message)
			elif data[-1].lower() == 'c':
				try:
					d = float(data[0:-1])
				except:
					raise forms.ValidationError(message)
			else:
				raise forms.ValidationError(message)
		else:
			raise forms.ValidationError(message)
		return d
	def clean_height_in(self):
		message="Must be a number followed by a unit (cm or in)."
		data = str(self.cleaned_data['height_in']).strip()
		if len(data) == 0:
			return ""
		if len(data) >= 3:
			if data[-2].lower() == 'i':
				try:
					d = float(data[0:-2])*2.54
				except:
					raise forms.ValidationError(message)
			elif data[-2].lower() == 'c':
				try:
					d = float(data[0:-2])
				except:
					raise forms.ValidationError(message)
			else:
				raise forms.ValidationError(message)
		else:
			raise forms.ValidationError(message)
		return d
	def clean_weight_in(self):
		message="Must be a number followed by a unit (kg or lb)."
		data = str(self.cleaned_data['weight_in']).strip()
		if len(data) == 0:
			return ""
		if len(data) >= 3:
			if data[-2].lower() == 'l':
				try:
					d = float(data[0:-2])/2.205
				except:
					raise forms.ValidationError(message)
			elif data[-2].lower() == 'k':
				try:
					d = float(data[0:-2])
				except:
					raise forms.ValidationError(message)
			else:
				raise forms.ValidationError(message)
		else:
			raise forms.ValidationError(message)
		return d
	def clean_spo2_in(self):
		message="Must be a percentage."
		data = str(self.cleaned_data['spo2_in']).strip()
		if len(data) == 0:
			return ""
		else:
			if data[-1].lower() == '%':
				try:
					d = float(data[0:-1])
				except:
					raise forms.ValidationError(message)
			else:
				try:
					d = float(data)
				except:
					raise forms.ValidationError(message)
		return d
	def clean_oxygen_in(self):
		message="Must be a percentage."
		data = str(self.cleaned_data['oxygen_in']).strip()
		if len(data) == 0:
			return ""
		else:
			if data[-1].lower() == '%':
				try:
					d = float(data[0:-1])
				except:
					raise forms.ValidationError(message)
			else:
				try:
					d = float(data)
				except:
					raise forms.ValidationError(message)
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
#		model = apps.get_model('ocemr','Vital')
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

class NewPregnancyForm(forms.Form):
	from models import Pregnancy, Patient
	patient = forms.ModelChoiceField(queryset=Patient.objects.all(),widget=forms.HiddenInput)
	addedBy = forms.ModelChoiceField(queryset=User.objects.all(),widget=forms.HiddenInput)
	addedDateTime = forms.DateTimeField(widget=forms.HiddenInput,required=False)

	deliveryDate = forms.DateTimeField(
		label="Delivery Date",
		required=True,
                help_text="Format: 'YYYY-MM-DD HH:MM'<br>Time can be omitted.",
                widget=widgets.CalendarWidget
		)
	gestationalAge = forms.IntegerField(
		label="Gestational Age",
		help_text="Weeks (wga)",
                min_value=0,
                max_value=100,
		required=True
                )
	gestationalAgePlusDays = forms.IntegerField(
		label="Gestational Age Days",
                help_text="Optional: Days to add to Weeks Gestational Age",
                min_value=0,
                max_value=6,
                initial=0,
		required=False
                )
	deliveryMode = forms.ChoiceField(
		label="Delivery Mode",
                choices=Pregnancy.PREGNANCY_DELIVERY_MODES,
		required=True
                )
	gender = forms.ChoiceField(
                label='Gender',
                required=True,
                choices=Pregnancy.GENDER_CHOICES
                )
	presentation = forms.CharField(
		label="Presentation",
		help_text="Vertex / Breech / other",
		required=False
		)
	laborLength = forms.CharField(
		label="Labor Length",
                help_text="Time 'HH:MM'",
		required=True
		)
	complications = forms.CharField(
		label="Complications",
                help_text="Optional: Problems during pregnancy, labor, or delivery",
		required=False,
                widget=forms.Textarea
		)
	referral = forms.CharField(
		label="Referral",
                help_text="Optional: Referral to outside Doctor/Hospital/Specialist",
		required=False
		)
	referralOutcome = forms.CharField(
		label="Referral Outcome",
                help_text="Optional: Outcome from referral",
		required=False,
                widget=forms.Textarea
		)
	postpartumFollowUp = forms.NullBooleanField(
		label="PP Follow Up",
                help_text="Did mom get the recommended care after delivery?",
		required=False,
                widget=forms.NullBooleanSelect
		)
	postpartumComplications = forms.CharField(
		label="PP Complications",
                help_text="Optional: Postpartum problems after delivery",
		required=False,
                widget=forms.Textarea
		)
	breastfeedingProblems = forms.NullBooleanField(
                label="Breastfeeding Problems",
                required=False,
                widget=forms.NullBooleanSelect
                )
	pmtct = forms.NullBooleanField(
                label="PMTCT",
                help_text="HIV prophylaxis given during pregnancy",
                required=False,
                widget=forms.NullBooleanSelect
                )
	tetanusBoosterDate = forms.DateTimeField(
		label="Tetanus Toxoid",
                help_text="Optional: Date of TT Booster",
		required=False,
                widget=widgets.CalendarWidget
		)

	def __init__(self, patient, user, *args, **kwargs):
		super(NewPregnancyForm, self).__init__(*args, **kwargs)
		self.fields['patient'].initial=patient.id
		self.fields['addedBy'].initial=user.id

	def clean_addedDateTime(self):
		from datetime import datetime
		return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
		model = apps.get_model('ocemr','ExamNote')
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
		model = apps.get_model('ocemr','Referral')
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
		model = apps.get_model('ocemr','Allergy')
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
		model = apps.get_model('ocemr','LabNote')
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
                model = apps.get_model('ocemr','Diagnosis')
                exclude = [ 'diagnosedDateTime' ]

	def clean_type(self):
		data = self.cleaned_data['type']
		from models import DiagnosisType
		try:
			d = DiagnosisType.objects.get(title=data)
		except DiagnosisType.DoesNotExist:
			raise forms.ValidationError("The DiagnosisType must exist!")
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
                model = apps.get_model('ocemr','Med')
                exclude = [ 'addedDateTime', 'dispensedDateTime', 'dispensedBy' ]

	def clean_type(self):
		data = self.cleaned_data['type']
		from models import MedType
		try:
			d = MedType.objects.get(title=data)
		except MedType.DoesNotExist:
			raise forms.ValidationError("The MedType must exist!")
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
		model = apps.get_model('ocemr','MedNote')
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
		model = apps.get_model('ocemr','CashLog')
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

class TallyReportForm(forms.Form):
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

class VillageTallyReportForm(forms.Form):
	dump_type = forms.ChoiceField(choices=(
				('TABLE', 'display'),
				('CSV', 'csv'),
				('G_PIE', 'Pie Graph'),
			)
		)

class DiagnosisPatientReportForm(forms.Form):
	from models import DiagnosisType
	diagnosis = forms.ModelMultipleChoiceField(
		queryset=DiagnosisType.objects.all().order_by("title"))
	date_start = forms.DateField(widget=widgets.CalendarWidget)
	date_end = forms.DateField(widget=widgets.CalendarWidget)
	age_min = forms.IntegerField(required=False)
	age_max = forms.IntegerField(required=False)
	dump_type = forms.ChoiceField(choices=(
				('TABLE', 'display'),
				('CSV', 'csv'),
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
		try:
			d = MedType.objects.get(title=data)
		except MedType.DoesNotExist:
			raise forms.ValidationError("The MedType must exist!")
		return d

class MergePatientForm(forms.Form):
	duplicateID = forms.IntegerField()

class MergeVillageForm(forms.Form):
        villageIncorrect = forms.CharField(label="Incorrect Village",
			widget=widgets.JQueryAutoComplete(
				'/autospel_name/ocemr/Village/'
				)
			)
        villageCorrect = forms.CharField(label="Correct Village",
			widget=widgets.JQueryAutoComplete(
				'/autospel_name/ocemr/Village/'
				)
			)
	def clean_villageIncorrect(self):
		data = self.cleaned_data['villageIncorrect']
		from models import Village
		v, is_new = Village.objects.get_or_create(name=data)
		if is_new:
			raise forms.ValidationError("The Incorrect Village name must exist!")
		return v
	def clean_villageCorrect(self):
		data = self.cleaned_data['villageCorrect']
		from models import Village
		v, is_new = Village.objects.get_or_create(name=data)
		if is_new:
			v.save()
		return v

class UploadBackupForm(forms.Form):
    file  = forms.FileField()


class ChangePasswordForm(forms.Form):

	oldPassword = forms.CharField(
			widget=forms.PasswordInput,
			label='Old Password'
		)
	newPassword = forms.CharField(
			widget=forms.PasswordInput,
			label='New Password'
		)
	newPasswordAgain = forms.CharField(
			widget=forms.PasswordInput,
			label='New Password Again'
		)


	def __init__(self, user, *args, **kwargs):

		super(ChangePasswordForm, self).__init__(*args, **kwargs)
		self.user=user


	def clean(self):

		cleaned_data = super(ChangePasswordForm, self).clean()

		# Check the old Password

		if not self.user.check_password(cleaned_data['oldPassword']):
			raise forms.ValidationError("Old password incorrect")

		# Check Length of new password

		if len(cleaned_data['newPassword']) < 6:
			raise forms.ValidationError("New password must be greater than 6 characters.")

		# Check that new passwords match.

		if cleaned_data['newPassword'] != cleaned_data['newPasswordAgain']:
			raise forms.ValidationError("new passwords didn't match.")

		return cleaned_data

class Hmis105Form(forms.Form):
	date_start = forms.DateField(widget=widgets.CalendarWidget)
	date_end = forms.DateField(widget=widgets.CalendarWidget)
	dump_type = forms.ChoiceField(choices=(
				('TABLE', 'display'),
				('CSV', 'csv'),
			)
		)
