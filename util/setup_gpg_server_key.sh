#!/bin/sh
#

if [ ! -e /var/lib/ocemr/gnupg/secring.gpg ]; then
	echo "========= setup_gpg_server_key.sh: `date`" >> /var/log/ocemr/update.log
	echo "gnupg --gen-key --batch" >> /var/log/ocemr/update.log
	cat /usr/share/ocemr/contrib/gpg_server_key.options \
		| gpg --home /var/lib/ocemr/gnupg --gen-key --batch \
		2>&1 | tee -a /var/log/ocemr/update.log
	chown -R www-data:www-data /var/lib/ocemr/gnupg
fi

