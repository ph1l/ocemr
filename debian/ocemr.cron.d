#
# Regular cron jobs for the ocemr package
#
0 4	* * *	root	[ -x /usr/share/ocemr/util/cron-daily.sh ] && /usr/share/ocemr/util/cron-daily.sh
