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
#       Copyright 2012 Philip Freeman <elektron@halo.nu>
##########################################################################

"""Database Check

This utility scans the OCEMR database for inconsistencies and
optionally clean them up where possible.
"""

import sys, getopt
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
	help= "check database for inconsistencies and optionally clean them up where possible."
	option_list = BaseCommand.option_list + (
        make_option('--force',
		action='store_true',
      		dest='force',
        	default=False,
        	help='Don\'t ask just do'),
	make_option('--dry-run',
		action='store_true',
		dest='dry-run',
		default=False,
		help='Don\'t do just print'),
        )

	def ask_do( self, question, default= True ):
		"""promt the user to see if we should do something...
		"""
		if self.OPT_FORCE:
			print "Forced: %s" %( question )
			if self.OPT_DRY:
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

	def handle(self, *args, **options):
		from django.db import connection
		from django.conf import settings

		self.OPT_FORCE	= options['force']
		self.OPT_DRY	= options['dry-run']

		# Scan Tables
		# ==== ======
		#  First Stage is to scan the tables in the database and
		#find inconsistencies

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

				if ask_do("remove orphan diag: %s"%( d )):
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

				if ask_do("remove orphan diag: %s"%( d )):
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

						if ask_do("reparent med: %s"%( m )):

							m.diagnosis = d_primary
							m.save()
				for d in d_dupes:

					if ask_do("remove dupe diag: %s"%( d )):
						d.delete()
