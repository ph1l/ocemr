from django.db.models.signals import post_syncdb
import ocemr.models


def post_syncdb_auto_upgrade(sender, **kwargs):
	"""
	# Your specific logic here
	"""
	import os, re
	from ocemr.models import DBVersion
	from ocemr.settings import DATABASE_ENGINE, CONTRIB_PATH, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT


	DEBUG=False

	if DATABASE_ENGINE not in ('mysql', 'sqlite3'):
		print "Skipping post_syncdb_auto_upgrade because %s is an unsupported DATABASE_ENGINE."%(DATABASE_ENGINE)
		return

	versions = DBVersion.objects.all().order_by("-addedDateTime")
	if len(versions) == 0:
		latest_version = DBVersion.objects.create(major=0,minor=5)
		latest_version.save()
	else:
		latest_version=versions[0]

	re_match_filename=re.compile("^(\d+)-(\d+)-%s.sql$"%(DATABASE_ENGINE))
	for fname in sorted(os.listdir("%s/schema_updates"%CONTRIB_PATH)):
		if DEBUG: print "checking %s"%(fname)
		m = re_match_filename.match(fname)
		if m:
			f_major=int(m.group(1))
			f_minor=int(m.group(2))
			if DEBUG: print "found %s: major=%d, minor=%d"%(fname,f_major,f_minor)
			if f_major > latest_version.major or ( f_major == latest_version.major and f_minor > latest_version.minor ):
				print "applying %s..."%(fname)
				cmd="cat %s/schema_updates/%s | "%(CONTRIB_PATH,fname)
				if DATABASE_ENGINE=='mysql':
					cmd += "mysql --force "
					if DATABASE_USER:
						cmd += "--user=%s " % DATABASE_USER
					if DATABASE_PASSWORD:
						cmd += "--password=%s " % DATABASE_PASSWORD
					if DATABASE_HOST:
						cmd += "--host=%s " % DATABASE_HOST
					if DATABASE_PORT:
						cmd += "--port=%s " % DATABASE_PORT
					cmd += DATABASE_NAME
				elif DATABASE_ENGINE=='sqlite3':
					cmd += "sqlite3 %s"%(DATABASE_NAME)
				else:
					raise Exception("WTF")
				exit_status = os.system(cmd)
				dbv = DBVersion.objects.create(major=f_major,minor=f_minor)
				dbv.save()
				if exit_status != 0:
					raise Exception("Command (%s) failed with %s."%(cmd,exit_status))
	return

post_syncdb.connect(post_syncdb_auto_upgrade, sender=ocemr.models)
