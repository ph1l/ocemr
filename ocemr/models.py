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

#############################################################################
# OCEMR - Open Clinic Electronic Medical Records
#############################################################################
#
# models.py - This describes the Data Models for the system. 
#
#############################################################################


from django.db import models

import datetime

from django.contrib.auth.models import User


class Village(models.Model):
	name = models.CharField(max_length=128)
	quick = models.BooleanField(default=False)
	active = models.BooleanField(default=True)
	def __unicode__(self):
		return self.name
	
class Patient(models.Model):
	GENDER_CHOICES = (
		('M', 'Male'),
		('F', 'Female'),
	    )

	familyName = models.CharField("Last Name",max_length=128)
	givenName = models.CharField("First Name",max_length=128)
	middleName = models.CharField("Middle Name",max_length=128, blank=True)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	birthYear = models.IntegerField("Year of Birth",help_text="Year of Birth or Age")
	birthDate = models.DateField(blank=True, null=True, help_text="If Available, Not Required")
	village = models.ForeignKey(Village)
	createdDateTime = models.DateTimeField(default=datetime.datetime.now)
	createdBy = models.ForeignKey(User)
	scratchNote = models.TextField(blank=True)
	phone = models.CharField(max_length=32, blank=True)
	email = models.EmailField(blank=True)
	altContactName = models.CharField(max_length=32, blank=True)
	altContactPhone = models.CharField(max_length=32, blank=True)
	def __unicode__(self):
		return '%s (%s-%d) %s' % (self.fullName, self.gender, self.age, self.village.name)
	def _get_age(self):
		"Returns the patient's age"
		if self.birthDate:
			age=datetime.date.today() - self.birthDate
			return age.days/365
		else:
			return datetime.datetime.now().year - self.birthYear
	def _get_full_name(self):
		"Returns the patient's full name."
		if self.middleName != "":
			return '%s %s %s' % (self.familyName, self.givenName, self.middleName)
		else:
			return '%s %s' % (self.familyName, self.givenName)
	def _get_num_visits(self):
		from models import Visit
		visits = Visit.objects.filter(patient=self)
		return len(visits)

	fullName = property(_get_full_name)
	age = property(_get_age)
	numVisits = property(_get_num_visits)
	def get_allergies(self):
		from models import Allergy
		return Allergy.objects.filter(patient=self)
	def get_account_balance(self):
		from models import Visit, CashLog
		bal=0
		for v in Visit.objects.filter(patient=self):
			bal = bal - v.cost
		for c in CashLog.objects.filter(patient=self):
			bal = bal + c.amount
		return bal
	def isNegative(self):
		if self.get_account_balance() < 0:
			return True
		return False

class Visit(models.Model):
	VISIT_REASON_CHOICES = (
		('NEW', 'New'),
		('FOL', 'Followup'),
	)
	VISIT_STATUS_CHOICES = (
		('SCHE', 'Scheduled'),
		('WAIT', 'Waiting'),
		('INPR', 'In Progress'),
		('CHOT',  'Checking Out'),
		('RESO',  'Resolved'),
		('MISS',  'Missed'),
	)
	VISIT_TYPE_CHOICES = (
		('OUT', 'Outpatient'),
		('IN',  'Inpatient'),
		('MAT',  'Maternity'),
	)
	patient = models.ForeignKey(Patient)
	scheduledDate = models.DateField('Date scheduled')
	scheduledBy = models.ForeignKey(User, related_name="visit_scheduled_by")
	type = models.CharField(max_length=3, choices=VISIT_TYPE_CHOICES, default='OUT')
	status = models.CharField(max_length=4, choices=VISIT_STATUS_CHOICES, default='SCHE')
	reason = models.CharField(max_length=3, choices=VISIT_REASON_CHOICES, default='NEW')
	reasonDetail = models.TextField('Reason for Visit',default="")
	followupTo = models.ForeignKey('self', null=True, blank=True)
	#
	seenDateTime = models.DateTimeField('Seen',null=True,blank=True)
	claimedDateTime = models.DateTimeField('Claimed',null=True,blank=True)
	claimedBy = models.ForeignKey(User,null=True,blank=True, related_name="visit_claimed_by")
	finishedDateTime = models.DateTimeField('Finished',null=True,blank=True)
	finishedBy = models.ForeignKey(User,null=True,blank=True, related_name="visit_finished_by")
	resolvedDateTime = models.DateTimeField('Resolved',null=True,blank=True)
	resolvedBy = models.ForeignKey(User,null=True,blank=True, related_name="visit_resolved_by")
	cost = models.FloatField(default=0)
	def __unicode__(self):
		return "Visit %d: %s %s"%(self.id,self.patient,self.scheduledDate)
	def _get_displayType(self):
		for code, displayType in self.VISIT_TYPE_CHOICES:
			if code == self.type:
				return displayType
		return ""
	def _get_displayStatus(self):
		for code, displayStatus in self.VISIT_STATUS_CHOICES:
			if code == self.status:
				return displayStatus
		return ""
	def _get_displayReason(self):
		for code, displayReason in self.VISIT_REASON_CHOICES:
			if code == self.reason:
				return displayReason
		return ""
	def _is_claimed(self):
		if self.status == 'SCHE' or self.status == 'WAIT':
			return False
		return True
	def _is_checking_out(self):
		if self.status == 'CHOT':
			return True
		return False
	def _is_finished(self):
		if self.status == 'RESO' or self.status == 'MISS':
			return True
		return False
	def _get_num_meds(self):
		from models import Med
		meds = Med.objects.filter(visit=self)
		return len(meds)

	displayType = property(_get_displayType)
	displayStatus = property(_get_displayStatus)
	displayReason = property(_get_displayReason)
	is_claimed = property(_is_claimed)
	is_checking_out = property(_is_checking_out)
	is_finished = property(_is_finished)
	get_num_meds = property(_get_num_meds)

	def get_estimated_visit_cost_detail(self):
		"""
		Returns an array of estimated cost items
		each array item is a list:
			( description, base cost, quantity, total )
		"""
		cost_detail =[]
		labs = Lab.objects.filter(visit=self)
		if len(labs) > 0:
			for l in labs:
				if l.status != "COM":
					continue
				cost_detail.append( (
					( "Lab: %s"%(l.type.title), l.type.cost , float(1), l.type.cost)
					) )
		meds = Med.objects.filter(visit=self)
		if len(meds) > 0:
			for m in meds:
				if m.status == "DIS":
					#Set m_dispenseAmount to zero if it's not valid
					try:
						m_dispenseAmount=float(m.dispenseAmount)
					except:
						m_dispenseAmount=float(0)
					cost_detail.append(
						( "Med: %s"%(m.type.title), m.type.cost, m.dispenseAmount, m.type.cost * m_dispenseAmount )
						)
		return cost_detail

	def get_estimated_visit_cost(self):
		cost_estimate = float(0)
		cost_detail = self.get_estimated_visit_cost_detail()
		for row in cost_detail:
			cost_estimate += row[3]
		return cost_estimate

	def get_lab_status(self):
		"""
			returns an INT indicated the following statuses:
	
			0 = no labs ordered
			1 = labs ordered but incomplete
			2 = labs ordered and completed
		"""
		from models import Lab
		
		labs = Lab.objects.filter(visit=self)
		if len(labs) > 0:
			for l in labs:
				if l.status == 'ORD' or l.status == 'PEN':
					return 1
			return 2
		else:
			return 0

	def get_meds_order_datetime(self):
		if self.get_num_meds < 1:
			return None
		from models import Med
		m=Med.objects.filter(visit=self).order_by('-addedDateTime')
		return m[0].addedDateTime
		
	def get_meds(self):
		from models import Med
		m=Med.objects.filter(visit=self).order_by('-addedDateTime')
		return m
		
	def get_med_status(self):
		"""
			returns an INT indicated the following statuses:
	
			0 = no meds ordered
			1 = meds ordered but incomplete
			2 = meds ordered and completed
		"""
		from models import Med
		
		meds = Med.objects.filter(visit=self)
		if len(meds) > 0:
			for m in meds:
				if m.status == 'ORD':
					return 1
			return 2
		else:
			return 0
		
	def get_active_diags(self):
		from models import Diagnosis
		diags=Diagnosis.objects.filter(visit=self)
		return diags
	def get_inactive_diag_types(self):
		#
		# TODO: Optimize Me !!!
		#
		from models import Diagnosis, Visit
		diags=Diagnosis.objects.filter(patient=self.patient)
		check_list=[]
		for d in diags:
			if not d.type in check_list:
				check_list.append(d.type)
		diags=self.get_active_diags()
		for d in diags:
			if d.type in check_list:
				check_list.remove(d.type)
		return check_list

	def has_collected(self):
		"""
		"""
		from models import CashLog
		
		c = CashLog.objects.filter(visit=self)
		if len(c) > 0: return 1
		return 0

	def has_collected_multiple(self):
		"""
		"""
		from models import CashLog
		
		c = CashLog.objects.filter(visit=self)
		if len(c) > 1: return 1
		return 0

	def collected(self):
		"""
		"""
		from models import CashLog
		total = float(0)
		for c in CashLog.objects.filter(visit=self):
			total = total + c.amount
		return total

	def get_cashlog(self):
		"""
		"""
		from models import CashLog
		total = float(0)
		return CashLog.objects.filter(visit=self)
	def get_past_visits(self):
		from models import Visit
		past_visits = Visit.objects.filter(patient=self.patient).exclude(pk=self.id).order_by('-scheduledDate')
		return past_visits
	def get_summary_text(self):
		"""
		return a text summary of the Visit
		"""

		from models import VisitSymptom, Vital, ExamNote

		out_txt="S:\n"
		
		symptoms = VisitSymptom.objects.filter(visit=self)
		for symptom in symptoms:
			out_txt += "\t%s: %s\n"%(symptom.type.title,symptom.notes)
		vitals = Vital.objects.filter(visit=self)
		out_txt += "O:"
		for vital in vitals:
			out_txt += "\t%s: %s" %(vital.type.title, vital.get_display_data())
		out_txt += "\n"
		examNotes = ExamNote.objects.filter(visit=self)
		for examNote in examNotes:
			out_txt += "\t%s: %s\n"%(examNote.type.title, examNote.note)
		diagnoses = Diagnosis.objects.filter(visit=self)
		for diagnosis in diagnoses:
			out_txt +="AP: %s:%s - %s\n"%(diagnosis.displayStatus,diagnosis.type.title, diagnosis.notes)
			meds = Med.objects.filter(diagnosis=diagnosis, status='DIS')
			for med in meds:
				out_txt +="\tMed: %s - %s\n"%(med.type.title,med.dosage)
		referrals = Referral.objects.filter(visit=self)
		for referral in referrals:
			out_txt +="Referral: %s - %s"%(referral.to, referral.reason)
		if self.claimedBy:
			out_txt += "\n\nSeen By: %s %s\n\n" %( self.claimedBy.first_name, self.claimedBy.last_name)
		return out_txt

	def can_modify_visit_type(self):
		"""
		limit situations where visit type can change

		during first day, while claimed, any type shift okay

		during subsequent days none is
		"""

		if self.is_claimed and self.seenDateTime.date() == datetime.date.today():
			return True

class SymptomType(models.Model):
	title = models.CharField(max_length=128)
	def __unicode__(self):
		return self.title

class VisitSymptom(models.Model):
	type = models.ForeignKey(SymptomType)
	visit = models.ForeignKey(Visit)
	notes = models.TextField(default="")
	def __unicode__(self):
		return "Visit#%s:%s"%(self.visit.id,self.type)

class VitalType(models.Model):
	title = models.CharField(max_length=128)
	unit = models.CharField(max_length=32,default="")
	minValue = models.FloatField(default=-1024)
	maxValue = models.FloatField(default=1024)
	def __unicode__(self):
		return "%s"%(self.title)

class Vital(models.Model):
	type = models.ForeignKey(VitalType)
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	observedDateTime = models.DateTimeField(default=datetime.datetime.now)
	observedBy = models.ForeignKey(User)
	data = models.FloatField()

	def __unicode__(self):
		return "%f%s"%(self.data,self.type.unit)

	def get_display_data(self):
		if self.type.title == "Temp":
			return "%.2fc (%.1ff)"%(self.data, round( ((self.data*9/5)+32), 2) )
		elif self.type.title == "Weight":
			return "%.2fkg (%.1flb)"%(self.data, round( self.data*2.205,2))
		elif self.type.title == "Height":
			return "%.1fcm (%.2fin)"%(self.data, round( self.data/2.54,2))
		else:
			return "%.2f"%(self.data)

class LabType(models.Model):
	title = models.CharField(max_length=128)
	cost = models.FloatField(default=0)
	active = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s"%(self.title)

class Lab(models.Model):
	LAB_STATUS_CHOICES = (
		('ORD', 'Ordered'),
		('PEN', 'Pending'),
		('CAN', 'Canceled'),
		('COM', 'Complete'),
		('FAI', 'Failed'),
	)
	type = models.ForeignKey(LabType)
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	orderedDateTime = models.DateTimeField(default=datetime.datetime.now)
	orderedBy = models.ForeignKey(User,related_name='orderedBy')
	status = models.CharField(max_length=3, choices=LAB_STATUS_CHOICES)
	result = models.CharField(max_length=32,default="")
	def _get_displayStatus(self):
		for code, displayStatus in self.LAB_STATUS_CHOICES:
			if code == self.status:
				return displayStatus
		return ""
	displayStatus = property(_get_displayStatus)
	def get_notes(self):
		"""
		"""
		from models import LabNote
		return LabNote.objects.filter(lab=self).order_by('-addedDateTime')
	def __unicode__(self):
		return "%s"%(self.type.title)

class LabNote(models.Model):
	lab = models.ForeignKey(Lab)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	note = models.TextField(default="")

class Pregnancy(models.Model):
	GENDER_CHOICES = (
		('M', 'Male'),
		('F', 'Female'),
	)
	PREGNANCY_DELIVERY_MODES = (
		('NVD', 'Normal Vaginal Delivery'),
		('C/S', 'C-Section'),
		('VAVD', 'Vacuum Assisted Vaginal Delivery'),
		('FAVD', 'Forceps Assisted Vaginal Delivery'),
	)
	patient = models.ForeignKey(Patient)
	deliveryDate = models.DateTimeField(default=datetime.datetime.now)
	gestationalAge = models.IntegerField(default=40)
	gestationalAgePlusDays = models.IntegerField(default=0)
	deliveryMode = models.CharField(max_length=4, choices=PREGNANCY_DELIVERY_MODES, default='NVD')
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
	presentation = models.CharField(max_length=32,default="")
	laborLength = models.CharField(max_length=6,default="00:00")
	complications = models.TextField(default="")
	referral =  models.CharField(max_length=128, default="")
	referralOutcome = models.TextField(default="")
	postpartumFollowUp = models.NullBooleanField(default=None, null=True)
	postpartumComplications = models.TextField(default="")
	breastfeedingProblems = models.NullBooleanField(default=None, null=True)
	pmtct = models.NullBooleanField(default=None, null=True)
	tetanusBoosterDate = models.DateTimeField(blank=True, null=True)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	def __unicode__(self):
		return "%s"%(self.type.title)

class DiagnosisType(models.Model):
	title = models.CharField(max_length=128)
	chronic = models.BooleanField(default=False)
	icpc2Code = models.CharField(max_length=5,default="")
	active = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s {%s}"%(self.title,self.icpc2Code)

class Diagnosis(models.Model):
	DIAGNOSIS_STATUS_CHOICES = (
		('NEW', 'New'),
		('FOL', 'Followup'),
		('NOT', 'Not Addressed'),
		('RES', 'Resolved'),
	)
	type = models.ForeignKey(DiagnosisType)
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	diagnosedDateTime = models.DateTimeField(default=datetime.datetime.now)
	diagnosedBy = models.ForeignKey(User,null=True)
	status = models.CharField(max_length=3, choices=DIAGNOSIS_STATUS_CHOICES, default='FOL')
	notes = models.TextField(default="")
	def _get_displayStatus(self):
		for code, displayStatus in self.DIAGNOSIS_STATUS_CHOICES:
			if code == self.status:
				return displayStatus
		return ""
	displayStatus = property(_get_displayStatus)
	def __unicode__(self):
		return "%s:%s"%(self.id,self.type.title)
	def get_meds(self):
		"""
		"""
		from models import Med
		meds = Med.objects.filter(diagnosis=self)
		return meds


class MedType(models.Model):
	title = models.CharField(max_length=128)
	cost = models.FloatField(default=0)
	active = models.BooleanField(default=True)
	def __unicode__(self):
		return "%s"%(self.title)

class Med(models.Model):
	MED_STATUS_CHOICES = (
		('ORD','Ordered'),
		('DIS','Dispensed'),
		('SUB','Substituted'),
		('CAN','Canceled'),
	)
	type = models.ForeignKey(MedType)
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	diagnosis = models.ForeignKey(Diagnosis)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	dosage = models.CharField(max_length=64) # 1x1x1
	dispenseAmount = models.FloatField(null=True,blank=True) # 15 capsules or 2.5 ml ?
	status = models.CharField(max_length=3, choices=MED_STATUS_CHOICES)
	dispensedDateTime = models.DateTimeField(null=True,blank=True)
	dispensedBy = models.ForeignKey(User,related_name='dispensedBy',null=True,blank=True)
	def _get_displayStatus(self):
		for code, displayStatus in self.MED_STATUS_CHOICES:
			if code == self.status:
				return displayStatus
		return ""
	displayStatus = property(_get_displayStatus)
	def get_notes(self):
		"""
		"""
		from models import MedNote
		return MedNote.objects.filter(med=self).order_by('-addedDateTime')
	def __unicode__(self):
		return "%s: %s"%(self.id, self.type.title)

class MedNote(models.Model):
	med = models.ForeignKey(Med)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	note = models.TextField(default="")

class ExamNoteType(models.Model):
	title = models.CharField(max_length=128)
	def __unicode__(self):
		return "%s"%(self.title)
	
class ExamNote(models.Model):
	type = models.ForeignKey(ExamNoteType)
	visit = models.ForeignKey(Visit)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	note = models.TextField(default="")
	def __unicode__(self):
		return "%s"%(self.type)
	
class Referral(models.Model):
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	to = models.CharField(max_length=64,help_text="Doctor/Hospital/Specialist")
	reason = models.TextField(blank=True)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	def __unicode__(self):
		return "%s: %s"%(self.id, self.to)

class Allergy(models.Model):
	patient = models.ForeignKey(Patient)
	to = models.CharField(max_length=64)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	def __unicode__(self):
		return "%s: %s"%(self.id, self.to)

class CashLog(models.Model):
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	amount = models.FloatField()
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	def __unicode__(self):
		return "%s: CashLog"%(self.id)

class DBVersion(models.Model):
	major = models.IntegerField()
	minor = models.IntegerField()
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	def __unicode__(self):
		return "Version %d.%d.x"%(self.major,self.minor)

class CustomizedTextField(models.Model):
	fieldName = models.CharField(max_length=64, primary_key=True)
	content = models.TextField(default="")
	def __unicode__(self):
		return "%s: %s"%(self.fieldName,self.content)
