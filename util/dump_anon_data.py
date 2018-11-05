#!/usr/bin/python
#
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


#
#  This dumps the database to CSV files scrubbing any personally
# identifying information for statistical analysis.
#

import sys, os, re

import util_conf
sys.path = [ util_conf.APP_PATH ] + sys.path

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ocemr.settings")

import django
django.setup()

#from ocemr.models import ###
from ocemr.models import Patient
from ocemr.models import Visit
from ocemr.models import VisitSymptom
from ocemr.models import Diagnosis
from ocemr.models import Med

from django.db.models import get_model, Q
from datetime import datetime

import csv

def cfr(row):
    new_row=[]
    for o in row:
        new_row.append(unicode(o).encode('utf-8'))
    return new_row
d_str=datetime.strftime(datetime.now(),"%Y%m%d-%H%M%S")
dir_name="stat_dump-%s"%(d_str)

os.mkdir(dir_name)


f_desc = open('%s/README.txt'%dir_name, mode='w')


f_desc.write("OCEMR Stat Dump Started %s\n\nContents:\n---\n"%(d_str))
f_desc.write("stat_patient.csv =\n\tPatient ID,\n\tGender,\n\tBirth Year,\n\tBirth Date,\n\tVillage Name\n\n")
f = open('%s/stat_patient.csv'%dir_name, mode='w')
w = csv.writer(f)
for p in Patient.objects.all():
    w.writerow(cfr([p.pk,p.gender,p.birthYear,p.birthDate,p.village.name]))

f_desc.write("stat_visit.csv =\n\tVisit ID,\n\tPatient ID,\n\tscheduledDate,\n\tstatus,\n\treason,\n\tReason Detail,\n\tFollowup To (Visit ID),\n\tSeen Date/Time,\n\tResolved Date/Time\n\n")
f = open('%s/stat_visit.csv'%dir_name,'w')
w = csv.writer(f)
for o in Visit.objects.all():
    w.writerow(cfr([o.pk,o.patient.pk,o.scheduledDate,o.status,o.reason,o.reasonDetail,o.followupTo,o.seenDateTime,o.resolvedDateTime]))


f_desc.write("stat_symptom.csv =\n\tSymptom ID,\n\tSymptom Name,\n\tVisit ID,\n\tNotes\n\n")
f = open('%s/stat_symptom.csv'%dir_name, mode='w')
w = csv.writer(f)
for o in VisitSymptom.objects.all():
    w.writerow(cfr([o.type.pk,o.type.title,o.visit.pk,o.notes]))

f_desc.write("stat_diagnosis.csv =\n\tDiagnosis ID,\n\tDiagnosis ICPC2 Code,\n\tDiagnosis Name,\n\tPatient ID,\n\tVisit ID,\n\tDiagnosis Status,\n\tNotes\n\n")
f = open('%s/stat_diagnosis.csv'%dir_name, mode='w')
w = csv.writer(f)
for o in Diagnosis.objects.all():
    w.writerow(cfr([o.type.pk,o.type.icpc2Code,o.type.title, o.patient.pk, o.visit.pk, o.status, o.notes]))

f_desc.write("stat_med.csv =\n\tMed ID,\n\tMed Name,\n\tPatient ID,\n\tVisit ID,\n\tDiagnosis ID,\n\tDosage,\n\tDispense Amount,\n\tStatus\n\n")
f = open('%s/stat_med.csv'%dir_name, mode='w')
w = csv.writer(f)
for o in Med.objects.all():
    w.writerow(cfr([o.pk, o.type.title, o.patient.pk, o.visit.pk, o.diagnosis.pk, o.dosage, o.dispenseAmount, o.status]))

#f_desc.write(" = ID,\n")
#f = open('%s/stat_.csv', mode='w')
#w = csv.writer(f)
#for o in .objects.all():
#    w.writerow(cfr([o.pk]))
d_str=datetime.strftime(datetime.now(),"%Y%m%d-%H%M%S")
f_desc.write("---\n\nOCEMR Stat Dump Finished @%s\n\n"%(d_str))
