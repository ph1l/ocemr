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

from ocemr.models import *
from django.contrib import admin

class PatientAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'familyName', 'givenName', 'age', 'village', 'numVisits', ]
	search_fields = [ 'familyName', 'givenName' ]

admin.site.register(Patient, PatientAdmin)

class VillageAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'name' ]
	search_fields = [ 'name' ]

admin.site.register(Village, VillageAdmin)

class VisitAdmin(admin.ModelAdmin):
	list_display = [
		'id', 'patient', 'scheduledDate', 'status', 'seenDateTime',
		'claimedDateTime', 'finishedDateTime', 'resolvedDateTime'
		]
	search_fields = [ 'patient__fullName' ]

admin.site.register(Visit, VisitAdmin)

class SymptomTypeAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'title' ]
	search_fields = [ 'title' ]

admin.site.register(SymptomType,SymptomTypeAdmin)

class VitalTypeAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'title', 'unit', 'minValue', 'maxValue' ]
	search_fields = [ 'title' ]

admin.site.register(VitalType,VitalTypeAdmin)


class LabTypeAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'title', 'cost', 'active' ]
	search_fields = [ 'title' ]

admin.site.register(LabType,LabTypeAdmin)

class DiagnosisTypeAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'icpc2Code', 'title', 'active' ]
	search_fields = [ 'icpc2Code', 'title' ]

admin.site.register(DiagnosisType, DiagnosisTypeAdmin)

class MedTypeAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'title', 'cost', 'active' ]
	search_fields = [ 'title' ]

admin.site.register(MedType,MedTypeAdmin)

class ExamNoteTypeAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'title' ]
	search_fields = [ 'title' ]

admin.site.register(ExamNoteType,ExamNoteTypeAdmin)

class DBVerisionAdmin(admin.ModelAdmin):
	list_display = [ 'id', 'major', 'minor', 'addedDateTime' ]

admin.site.register(DBVersion,DBVerisionAdmin)

#admin.site.register(Referral)
#admin.site.register(VisitSymptom)
#admin.site.register(Vital)
#admin.site.register(Lab)
#admin.site.register(LabNote)
#admin.site.register(Diagnosis)
#admin.site.register(Med)
#admin.site.register(MedNote)
#admin.site.register(ExamNote)
#admin.site.register(Allergy)
#admin.site.register(CashLog)
