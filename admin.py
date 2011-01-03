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

from ocemr.models import *
from django.contrib import admin

#admin.site.register()

admin.site.register(Village)
admin.site.register(Patient)
admin.site.register(Visit)
admin.site.register(SymptomType)
admin.site.register(VisitSymptom)
admin.site.register(VitalType)
admin.site.register(Vital)
admin.site.register(LabType)
admin.site.register(Lab)
admin.site.register(DiagnosisType)
admin.site.register(Diagnosis)
admin.site.register(MedType)
admin.site.register(Med)
admin.site.register(ExamNoteType)
admin.site.register(ExamNote)
admin.site.register(Referral)
