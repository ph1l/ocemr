"""
 Command for backup database
"""

import os, time
from subprocess import Popen
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Backup database. Only Mysql and Postgresql engines are implemented"

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

        if len(args) == 0:
                backup_dir = '%s/backups'%(self.var_path)
                if not os.path.exists(backup_dir):
                        os.makedirs(backup_dir)
                outfile = os.path.join(backup_dir, 'backup_%s.%s' % (time.strftime('%y%m%d-%H%M%S'),self.engine))
        elif len(args) == 1:
                outfile = args[0]
        else:
                raise Exception("backupdb: Too many args.")
        if self.engine == 'mysql':
            print 'Doing Mysql backup to database %s into %s' % (self.db, outfile)
            self.do_mysql_backup(outfile)
        #elif self.engine in ('postgresql_psycopg2', 'postgresql'):
        #    print 'Doing Postgresql backup to database %s into %s' % (self.db, outfile)
        #    self.do_postgresql_backup(outfile)
        elif self.engine =='sqlite3':
	    print 'Doing sqlite3 backup to database %s into %s' % (self.db, outfile)
	    self.do_sqlite3_backup(outfile)
        else:
            print 'Backup in %s engine not implemented' % self.engine
        if self.encrypt:
            print 'Encrypting %s to %s %s.gpg'%(outfile, self.encrypt_to, outfile)
            self.do_encrypt_backup(outfile)
	else:
	    print 'Compressing %s to %s.bz2'%(outfile, outfile)
            self.do_compress_backup(outfile)

    def do_sqlite3_backup(self, outfile):
        args = [self.db, ".dump"]

        cmd = 'sqlite3 %s > %s' % (' '.join(args), outfile)
        exit_status = os.system(cmd)
        if exit_status != 0:
                raise Exception("Dump command (%s) failed with %s."%(cmd,exit_status))

    def do_mysql_backup(self, outfile):
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

        cmd = 'mysqldump %s > %s' % (' '.join(args), outfile)
        exit_status = os.system(cmd)
        if exit_status != 0:
                raise Exception("Dump command (%s) failed with %s."%(cmd,exit_status))

    def do_postgresql_backup(self, outfile):
        args = []
        if self.user:
            args += ["--username=%s" % self.user]
        if self.passwd:
            args += ["--password"]
        if self.host:
            args += ["--host=%s" % self.host]
        if self.port:
            args += ["--port=%s" % self.port]
        if self.db:
            args += [self.db]
	p = Popen("pg_dump %s > %s" %( ' '.join(args), outfile ), shell=True,
		stdin=PIPE, stdout=PIPE, close_fds=True)
        if self.passwd:
            p.stdin.write('%s\n' % self.passwd)
        print p.stdout.read()

    def do_compress_backup(self, outfile):
	cmd = 'bzip2 -9 %s'%( outfile )
	exit_status = os.system(cmd)
        #This assumes you run unix (you do run unix, don't you?)
        if exit_status != 0:
                raise Exception("Encrypt command (%s) failed with %s."%(cmd,exit_status))
	
    def do_encrypt_backup(self, outfile):
        args = ["--encrypt", "--batch", "--yes",
                "--homedir", "%s/gnupg"%(self.var_path),
                "--output", "%s.gpg"%(outfile)
                ]
        if len(self.encrypt_to) == 0:
            raise Exception("DB_BACKUP_ENCRYPT_TO empty (see settings.py)")
	for r in self.encrypt_to:
	    args += ["--recipient", r]
	args += [ outfile ]
        cmd = 'gpg %s'%(' '.join(args))
        exit_status = os.system(cmd)
        os.unlink(outfile)
        #This assumes you run unix (you do run unix, don't you?)
        if exit_status != 0:
                raise Exception("Encrypt command (%s) failed with %s."%(cmd,exit_status))
        

