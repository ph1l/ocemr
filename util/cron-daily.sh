#!/bin/sh
#
#


set -e

#

cd /usr/share/ocemr/apps/ocemr
sudo -u www-data python ./manage.py backupdb

#cd /usr/share/ocemr/util
#sudo -u www-data python ./
