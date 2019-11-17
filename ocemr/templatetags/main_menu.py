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

from django import template
register = template.Library()


class MenuItemNode(template.Node):
    def __init__(self, url, description, current_path_info):
        self.url = url
	self.description = description
	self.current_path_info = template.Variable(current_path_info)

    def render(self, context):
	try:
		actual_path_info = self.current_path_info.resolve(context)
		if self.url == actual_path_info:
			return "<!-- %s %s %s -->%s"%(self.url,self.description,actual_path_info,self.description)
		else:
			return "<!-- %s %s %s --><A HREF=%s>%s</A>"%(self.url,self.description,actual_path_info,self.url,self.description)
	except template.VariableDoesNotExist:
		return ''

@register.tag(name="menu_item")
def do_menu_item(parser, token):
	try:
		tag_name, url, description, current_path_info = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
	if not (description[0] == description[-1] and description[0] in ('"', "'")):
		raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
	return MenuItemNode(url, description[1:-1], current_path_info)


