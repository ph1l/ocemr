#!/bin/bash
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

b=`git branch | grep ^\* | cut -b3-`
t=`git tag -l | tail -1`

if [ "${b}" != "master" ]; then
    OCEMR_VERSION="${b}-`date +%Y%m%d%H%M`"
else
    OCEMR_VERSION="${t}"
fi

./util/make_version.sh > version.py

git archive master --prefix=ocemr-${OCEMR_VERSION}/ | bzip2 > ../ocemr-${OCEMR_VERSION}.tar.bz2

