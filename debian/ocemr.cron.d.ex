#
# Regular cron jobs for the ocemr package
#
0 4	* * *	root	[ -x /usr/bin/ocemr_maintenance ] && /usr/bin/ocemr_maintenance
