#!/bin/sh
#

RSYNC_OPTS="-aL --delete-after --verbose --progress"

WEB_ROOT=${1}
#/usr/share/pyshared/django
DJANGO_ROOT=${2}

if [ -z "${DJANGO_ROOT}" ]; then 
        echo "./install_static.sh <WEB_ROOT> <DJANGO_ROOT>"
        exit
fi

#rm -vrf ${WEB_ROOT}/media/admin
#rm -vrf ${WEB_ROOT}/media/ocemr

rsync ${RSYNC_OPTS} ${DJANGO_ROOT}/contrib/admin/media/ ${WEB_ROOT}/media/admin
rsync ${RSYNC_OPTS} static_media/ ${WEB_ROOT}/media/ocemr
