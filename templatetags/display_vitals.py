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

from django import template
register = template.Library()


class DisplayVitalNode(template.Node):
    def __init__(self, data_in, type):
        self.data_in = template.Variable(data_in)
	self.type = template.Variable(type)

    def render(self, context):
	try:
		actual_data = float(self.data_in.resolve(context))
		type = self.type.resolve(context)
		if type == "Temp":
			return "%.2fc (%.1ff)"%(actual_data, round( ((actual_data*9/5)+32), 2) )
		elif type == "Weight":
			return "%.2fkg (%.1flb)"%(actual_data, round( actual_data*2.205,2))
		elif type == "Height":
			return "%.1fcm (%.2fin)"%(actual_data, round( actual_data/2.54,2))
		else:
			return "%.2f"%(actual_data)
	except template.VariableDoesNotExist:
		return ''


@register.tag(name="display_vital")
def do_display_vital(parser, token):
	try:
		tag_name, data, type = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
	return DisplayVitalNode(data, type)


