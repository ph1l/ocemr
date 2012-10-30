#!/usr/bin/python -u
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
#       Copyright 2012 Philip Freeman <philip.freeman@gmail.com>
##########################################################################

"""Database Check

This utility scans the OCEMR database for inconsistencies and
optionally clean them up where possible.
"""

import sys, getopt
import util_conf
sys.path.append( util_conf.APP_PATH )

import settings
from django.core.management import setup_environ

setup_environ( settings )

def usage():
	"""
	Print Usage
	"""
	print """
Usage Summary: %(PROGNAME)s [ OPTS ]

%(DESCRIPTION)s

OPTS:
	-f	force cleanup. don't ask for confirmation.
	-n	dry-run. print only.
""" % { 'DESCRIPTION': __doc__, 'PROGNAME': sys.argv[0], }

try:
	opts, args = getopt.getopt(sys.argv[1:],
			"hfn",
			[
				"help",
				"force",
				"dry-run",
				]
			)

except getopt.GetoptError, err:
	print str(err)
	usage()
	sys.exit(2)

OPT_FORCE	= False
OPT_DRY		= False

for o, a in opts:
	if o in ( "-h", "--help" ):
		usage()
		sys.exit()
	elif o in ( "-f", "--force" ):
		OPT_FORCE=True
	elif o in ( "-n", "--dry-run" ):
		OPT_DRY=True
	else:
		assert False, "unhandled option"

def ask_do( question, default= True, force= False, dry_run= False ):
	"""promt the user to see if we should do something...
	"""
	if force:
		print "Forced: %s" %( question )
		if dry_run:
			return False
		else:
			return True

	if default: choices="Y/n"
	else: choices="y/N"

	while True:
		print "%s (%s)" %( question, choices ),
		answer = sys.stdin.readline()
		if answer[0].lower() == '\n':
			return default
		if answer[0].lower() == 'y':
			if dry_run:
				return False
			else:
				return True
		if answer[0].lower() == 'n':
			return False
		print "invalid answer '%s', use %s" %( answer.strip(), choices )

	
	
# Scan Tables
# ==== ======
#  First Stage is to scan the tables in the database and find inconsistencies

print "\nStage One: Scanning Tables\n===== ==== ======== ======\n"

#
# Diagnosis

sys.stdout.write( " Diagnosis [" )
from ocemr.models import Diagnosis
from ocemr.models import DiagnosisType
from ocemr.models import Visit

keys_visit_type = {}
ids_no_visit = []
ids_no_diagnosis_type = []

# Iterate through all the Diagnosis records
for d in Diagnosis.objects.all():

	# Check that the Visit Foreign Key is valid.
	try:
		visit_id = d.visit.id

	except Visit.DoesNotExist:

		sys.stdout.write( "v" )
		ids_no_visit.append( d.id )
		continue

	# Check that the Diagnosis Type Foreign Key is Valid
	try:
		diagnosis_type_id = d.type.id

	except DiagnosisType.DoesNotExist:

		sys.stdout.write( "t" )
		ids_no_diagnosis_type.append( d.id )
		continue

	# Check for duplicate Diagnosis records
	key = "%d_%d" %( d.visit.id, d.type.id )

	if key in keys_visit_type.keys():

		sys.stdout.write( "d" )
	else:

		keys_visit_type[ key ] = []

	keys_visit_type[ key ].append( d.id )

sys.stdout.write( "]\n" )

# Cleanup Tables
# ======= ======
#  print info about inconsistencies and cleanup if OPT_FORCE
#

print "\nStage Two: Cleanup\n===== ==== =======\n"

# Diagnosis

print "  Diagnosis Table\n  --------- -----"

# diagnosis records orphaned from their visits
#
num_diagnosis_orphan_from_visits = len( ids_no_visit )

if num_diagnosis_orphan_from_visits > 0:

	print "Found %d orphan diagnosis records from missing visits." %(
			num_diagnosis_orphan_from_visits
		)
	for i in ids_no_visit:

		d= Diagnosis.objects.get( pk= i )

		if ask_do("remove orphan diag: %s"%( d ),force=OPT_FORCE,dry_run=OPT_DRY):
			d.delete()

# diagnosis records orphaned from a diagnosis type
#
num_diagnosis_orphan_from_diagnosis_type= len( ids_no_diagnosis_type )

if num_diagnosis_orphan_from_diagnosis_type > 0:

	print "Found %d orphan diagnosis records from missing types." %(
			num_diagnosis_orphan_from_diagnosis_type
		)
	for i in ids_no_diagnosis_type:

		d= Diagnosis.objects.get( pk= i )

		if ask_do("remove orphan diag: %s"%( d ),force=OPT_FORCE,dry_run=OPT_DRY):
			d.delete()

# diagnosis records in duplicate
#
num_duplicate_diagnosis= 0

for k in keys_visit_type.keys():

	if len( keys_visit_type[ k ] ) > 1:

		num_duplicate_diagnosis+= 1
	else:
		keys_visit_type.pop(k)

if num_duplicate_diagnosis > 0:

	print "Found %d duplicate diagnosis keys" %( num_duplicate_diagnosis )
	for k in keys_visit_type.keys():

		d_primary = None
		all_meds = []
		d_dupes = []

		for i in keys_visit_type[ k ]:

			d= Diagnosis.objects.get( pk= i )

			if d_primary == None:

				print "Parent Diag: %s"%( d )
				d_primary= d
			else:
				d_dupes.append(d)

			all_meds.extend( d.get_meds() )

		for m in all_meds:

			if m.diagnosis != d_primary:

				if ask_do("reparent med: %s"%( m ),force=OPT_FORCE,dry_run=OPT_DRY):

					m.diagnosis = d_primary
					m.save()
		for d in d_dupes:

			if ask_do("remove dupe diag: %s"%( d ),force=OPT_FORCE,dry_run=OPT_DRY):
				d.delete()
#__EOF__
