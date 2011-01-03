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
from mydbfields import EuDateField


class Village(models.Model):
	name = models.CharField(max_length=128)
	quick = models.BooleanField(default=False)
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
	birthYear = models.IntegerField("Year of Birth",help_text="approx. or actual year of birth")
	birthDate = EuDateField(blank=True, null=True)
	village = models.ForeignKey(Village)
	createdDateTime = models.DateTimeField(default=datetime.datetime.now)
	createdBy = models.ForeignKey(User)
	scratchNote = models.TextField(blank=True)
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
	fullName = property(_get_full_name)
	age = property(_get_age)
	def get_allergies(self):
		from models import Allergy
		return Allergy.objects.filter(patient=self)

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
	patient = models.ForeignKey(Patient)
	scheduledDate = EuDateField('Date scheduled')
	scheduledTime = models.TimeField('Time scheduled')
	scheduledBy = models.ForeignKey(User)
	status = models.CharField(max_length=4, choices=VISIT_STATUS_CHOICES, default='SCHE')
	reason = models.CharField(max_length=3, choices=VISIT_REASON_CHOICES, default='NEW')
	reasonDetail = models.TextField(default="")
	#followupTo = models.ForeignKey('self', null=True)
	def __unicode__(self):
		return "Visit %d: %s %s"%(self.id,self.patient,self.scheduledDate)
	def _get_displayStatus(self):
		for code, displayStatus in self.VISIT_STATUS_CHOICES:
			if code == self.status:
				return displayStatus
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

	displayStatus = property(_get_displayStatus)
	is_claimed = property(_is_claimed)
	is_checking_out = property(_is_checking_out)
	is_finished = property(_is_finished)
	get_num_meds = property(_get_num_meds)
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
		return "%s (%s)"%(self.title,self.unit)

class Vital(models.Model):
	type = models.ForeignKey(VitalType)
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	observedDateTime = models.DateTimeField(default=datetime.datetime.now)
	observedBy = models.ForeignKey(User)
	data = models.FloatField()
	def __unicode__(self):
		return "%f%s"%(self.data,self.type.unit)
	
class LabType(models.Model):
	title = models.CharField(max_length=128)
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
		return LabNote.objects.filter(lab=self)
	def __unicode__(self):
		return "%s"%(self.type.title)

class LabNote(models.Model):
	lab = models.ForeignKey(Lab)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	note = models.TextField(default="")


class DiagnosisType(models.Model):
	title = models.CharField(max_length=128)
	chronic = models.BooleanField(default=False)
	icpc2Code = models.CharField(max_length=5,default="")
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
	def __unicode__(self):
		return "%s"%(self.title)

class Med(models.Model):
	MED_STATUS_CHOICES = (
		('ORD','Ordered'),
		('DIS','Dispensed'),
		('SUB','Substituted'), # Substituted
		('NDI','Not Dispensed'), # 
	)
	type = models.ForeignKey(MedType)
	patient = models.ForeignKey(Patient)
	visit = models.ForeignKey(Visit)
	diagnosis = models.ForeignKey(Diagnosis)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)
	dosage = models.CharField(max_length=64) # 1x1x1
	dispenseAmount = models.FloatField() # 15 capsules or 2.5 ml ?
	status = models.CharField(max_length=3, choices=MED_STATUS_CHOICES)
	dispensedDateTime = models.DateTimeField(null=True)
	dispensedBy = models.ForeignKey(User,related_name='dispensedBy',null=True)
	def _get_displayStatus(self):
		for code, displayStatus in self.MED_STATUS_CHOICES:
			if code == self.status:
				return displayStatus
		return ""
	displayStatus = property(_get_displayStatus)

class MedNote(models.Model):
	prescription = models.ForeignKey(Med)
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

class ImmunizationLog(models.Model):
	patient = models.ForeignKey(Patient)
	description = models.TextField(blank=True)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)

class Allergy(models.Model):
	patient = models.ForeignKey(Patient)
	to = models.CharField(max_length=64)
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)

class CashLog(models.Model):
	patient = models.ForeignKey(Patient)
	description = models.TextField(blank=True)
	amount = models.FloatField()
	addedDateTime = models.DateTimeField(default=datetime.datetime.now)
	addedBy = models.ForeignKey(User)