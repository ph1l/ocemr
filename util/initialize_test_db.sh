#!/bin/bash
#
VAR=~/var
APP_DIR=.
APP=$APP_DIR/ocemr
UTIL=./util

export PYTHONPATH=$APP_DIR

mkdir -p ${VAR}/{db,backups,gnupg}
chmod 700 ${VAR}/gnupg

#if [ ! -e ${VAR}/gnupg/secring.gpg ]; then
#	cat contrib/gpg_server_key.options  | gpg --home ${VAR}/gnupg --gen-key --batch
#fi

if [ -e ${VAR}/db/ocemr.db ]; then
	echo SQLite database present, aborting initialization...
	exit 10
fi


python ${APP}/../manage.py migrate

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

echo "all done initializing in ${VAR}/db/ocemr.db"
