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
        self.engine = settings.DATABASES['default']['ENGINE']
        self.db = settings.DATABASES['default']['NAME']
        self.user = settings.DATABASES['default']['USER']
        self.passwd = settings.DATABASES['default']['PASSWORD']
        self.host = settings.DATABASES['default']['HOST']
        self.port = settings.DATABASES['default']['PORT']

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
		outfile = infile[:-4]
		print "Decompressing \"%s\" to \"%s\"..."%(infile, outfile)
		self.do_decompress_backup(infile, outfile)
		print "\tdone."
		infile = outfile
	elif infile[-4:] == ".gpg":
		outfile = infile[:-4]
		print "Decrypting \"%s\" to \"%s\" ..."%(infile, outfile)
		self.do_decrypt_backup(infile, outfile)
		infile = outfile
		print "\tdone."

	if infile[-6:] == ".mysql":
		if self.engine != 'mysql':
			raise Exception("Backup from MySQL, but current engine is not!")
		print 'Doing MySQL restore to database %s from %s...' % (self.db, infile)
		self.do_mysql_restore(infile)
		print "\tdone."
	elif infile[-8:] == ".sqlite3":
		if self.engine != 'sqlite3':
			raise Exception("Backup from SqLite3, but current engine is not!")
		print 'Doing sqlite3 restore to database %s from %s' % (self.db, infile)
		self.do_sqlite3_restore
		print "\tdone."
        else:
		raise Exception("restoredb doesn't understand file(%s)"%infile)

    def do_decompress_backup(self, infile, outfile):
	"""
	"""
	cmd = 'bunzip2 -c "%s" > "%s"'%( infile, outfile )
	exit_status = os.system(cmd)
	if exit_status != 0:
		raise Exception("Encrypt command (%s) failed with %s."%(cmd,exit_status))

    def do_decrypt_backup(self, infile, outfile):
	"""
	"""
	args = ["--decrypt", "--batch", "--yes",
		"--homedir", "%s/gnupg"%(self.var_path),
		"--output", "%s"%(outfile), infile
		]
	cmd = 'gpg %s'%(' '.join(args))
	exit_status = os.system(cmd)
	if exit_status != 0:
		raise Exception("Decrypt command (%s) failed with %s."%(cmd,exit_status))


    def do_mysql_restore(self, infile):
	"""
	"""
	args = []
	if self.user:
		args += ["--user=%s" % self.user]
	if self.passwd:
		args += ["--password=%s" % self.passwd]
	if self.host:
		args += ["--host=%s" % self.host]
	if self.port:
		args += ["--port=%s" % self.port]
	args += [self.db]

	cmd = 'mysql %s < %s' % (' '.join(args), infile)
	exit_status = os.system(cmd)
	os.unlink(infile)
	if exit_status != 0:
		raise Exception("restore command (%s) failed with %s."%(cmd,exit_status))


    def do_sqlite3_restore(self, infile):
	"""
	"""
	cmd = 'sqlite3 %s < %s' % (self.db, infile)
	exit_status = os.system(cmd)
	if exit_status != 0:
		raise Exception("Restore command (%s) failed with %s."%(cmd,exit_status))
