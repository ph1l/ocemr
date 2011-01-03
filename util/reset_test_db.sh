#!/bin/sh
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
#       Copyright 2011 Philip Freeman <philip.freeman@gmail.com>
##########################################################################
echo
echo This will DESTROY and re-create the Databse. Type 'YES' to continue...
echo

read FOO

if [ "${FOO}" != "YES" ]; then
	echo Canceled
	exit
fi



if [ -d /var/lib/mysql/ocemr ]; then
	/etc/init.d/apache2 stop
	echo Resetting MySQL
	echo "drop database ocemr ; create database ocemr;" | mysql -p
elif [ -e /tmp/ocemr.db ]; then
	echo Resetting SQLite3
	rm -v /tmp/ocemr.db
fi


python manage.py syncdb

#----------

python ./util/import_symptom_csv.py
python ./util/import_vital_csv.py
python ./util/import_examnotes_csv.py
python ./util/import_labs_csv.py
python ./util/import_dx_csv.py
python ./util/import_rx_csv.py

#----------
#
# python ./util/import_test_patients_csv.py
#

if [ -d /var/lib/mysql/ocemr ]; then
	/etc/init.d/apache2 start
fi
