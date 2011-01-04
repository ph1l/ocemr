#!/bin/sh
#

WEB_ROOT=${1}
DJANGO_ROOT=${2}

if [ -z "${DJANGO_ROOT}" ]; then 
        echo "./install_static.sh <WEB_ROOT> <DJANGO_ROOT>"
        exit
fi

rm -vrf ${WEB_ROOT}/media/admin
rm -vrf ${WEB_ROOT}/css
rm -vrf ${WEB_ROOT}/js

cp -av ${DJANGO_ROOT}/contrib/admin/media ${WEB_ROOT}/media/admin
cp -av static_media/css ${WEB_ROOT}/css
cp -av static_media/js ${WEB_ROOT}/js


