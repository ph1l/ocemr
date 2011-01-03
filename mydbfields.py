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

from django import forms
from django.forms.fields import DEFAULT_DATE_INPUT_FORMATS
from django.db import models


class EuDateField(models.DateField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': EuDateFormField})
        return super(EuDateField, self).formfield(**kwargs)

class EuDateFormField(forms.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'input_formats': ("%d.%m.%Y","%d-%m-%Y","%d/%m/%Y")+DEFAULT_DATE_INPUT_FORMATS})
        super(EuDateFormField, self).__init__(*args, **kwargs)
