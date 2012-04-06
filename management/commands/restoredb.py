"""
 Command for database restore
"""

import os, time
from subprocess import Popen
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Restore database. Only Mysql and sqlite3 engines are implemented"

    def handle(self, *args, **options):
        from django.db import connection
        from django.conf import settings

        self.var_path = settings.VAR_PATH
        self.engine = settings.DATABASE_ENGINE
        self.db = settings.DATABASE_NAME
        self.user = settings.DATABASE_USER
        self.passwd = settings.DATABASE_PASSWORD
        self.host = settings.DATABASE_HOST
        self.port = settings.DATABASE_PORT

        self.encrypt = settings.DB_BACKUP_ENCRYPT
        self.encrypt_to = settings.DB_BACKUP_ENCRYPT_TO

        if len(args) < 1:
		raise Exception("restoredb called with insufficient args")
	elif len(args) > 2:
		raise Exception("restoredb called with too many args")
	infile = args[0]
        if not os.path.exists(infile):
		raise Exception("restoredb can't find file(%s)"%infile)
	if infile[-4:] == ".bz2":
		self.do_decompress_backup(infile)
		infile = infile[:-4]
	elif infile[-4:] == ".gpg":
		self.do_decrypt_backup(infile)
		infile = infile[:-4]
	else:
		raise Exception("restoredb doesn't understand file(%s)"%infile)
	if infile[-6:] == ".mysql":
		if self.engine != 'mysql':
			raise Exception("Backup from MySQL, but current engine is not!")
		print 'Doing MySQL restore to database %s from %s' % (self.db, infile)
		self.do_mysql_restore(infile)
	elif infile[-8:] == ".sqlite3":
		if self.engine != 'sqlite3':
			raise Exception("Backup from SqLite3, but current engine is not!")
		print 'Doing sqlite3 restore to database %s from %s' % (self.db, infile)
		self.do_sqlite3_restore
        else:
		raise Exception("restoredb doesn't understand file(%s)"%infile)

    def do_decompress_backup(self, infile):
	"""
	"""
	cmd = 'bunzip2 %s'%( infile )
	exit_status = os.system(cmd)
	if exit_status != 0:
		raise Exception("Encrypt command (%s) failed with %s."%(cmd,exit_status))

    def do_decrypt_backup(self, infile):
	"""
	"""

    def do_mysql_restore(self, infile):
	"""
	"""
    def do_sqlite3_restore(self, infile):
	"""
	"""
