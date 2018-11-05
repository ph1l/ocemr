#!/bin/bash -e
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
MYSQL_DATA=/var/lib/mysql
APP_DIR=/usr/share/ocemr/apps
APP=$APP_DIR/ocemr
UTIL=/usr/share/ocemr/util

export PYTHONPATH=$APP_DIR

MYSQL_ADMIN_USER=root
MYSQL_USER=ocemr
MYSQL_HOST=localhost
MYSQL_DBNAME=ocemr

if ! cat /etc/ocemr/settings.py  | grep -v ^# | grep ENGINE | grep mysql >/dev/null; then
	echo "set \"DATABASE_ENGINE\" in /etc/ocemr/settings.py to \"mysql\""
	exit 1
fi
	
if [ -e ${MYSQL_DATA}/${MYSQL_DBNAME} ]; then
	echo "MySQL database present (${MYSQL_DATA}/${MYSQN_DBNAME}), aborting initialization..."
	exit 1
fi
if [ -z "${PASSWD}" ]; then
	echo
	echo -n please enter mysql password for ${MYSQL_USER}@${MYSQL_HOST}:\
	read -s PASSWD
	echo
	echo
	echo -n again:\
	read -s PASSWD2
	echo

	if [ ${PASSWD} != ${PASSWD2} ]; then
		echo Error: Passwords didn\'t match.
		exit 1
	fi
fi

echo
echo please enter mysql credentials for ${MYSQL_ADMIN_USER}:
echo 'CREATE DATABASE IF NOT EXISTS '${MYSQL_DBNAME} \
	| mysql -u${MYSQL_ADMIN_USER} -p${MYSQL_ADMIN_PASSWD}

echo
echo please enter mysql credentials for ${MYSQL_ADMIN_USER}:
echo 'GRANT ALL ON ocemr.* TO '${MYSQL_USER}'@'${MYSQL_HOST}' IDENTIFIED BY "'${PASSWD}'";' \
	| mysql -u${MYSQL_ADMIN_USER} -p${MYSQL_ADMIN_PASSWD}

python ${APP}/manage.py migrate

#----------

python ${UTIL}/import_symptom_csv.py
python ${UTIL}/import_vital_csv.py
python ${UTIL}/import_examnotes_csv.py
python ${UTIL}/import_labs_csv.py
python ${UTIL}/import_dx_csv.py
python ${UTIL}/import_rx_csv.py

#----------
#
# python ./util/import_test_patients_csv.py
#

echo "all done initializing in MySQL"
