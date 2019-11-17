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

from django import forms
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from simplejson import JSONEncoder

class JQueryAutoComplete(forms.TextInput):
	class Media:
		js = (
			'/media/ocemr/js/jquery-1.4.2.js',
			'/media/ocemr/js/jquery.autocomplete.js',
		)
		css = {
			'all': ('/media/ocemr/css/jquery.autocomplete.css',),
		}
	def __init__(self, source, options={}, attrs={}):
		"""source can be a list containing the autocomplete values or a
		string containing the url used for the XHR request.

		For available options see the autocomplete sample page::
		http://jquery.bassistance.de/autocomplete/"""

		self.options = { 'minChars': '2', 'max': '64' }
		self.attrs = {'autocomplete': 'off'}
		self.source = source
		if len(options) > 0:
			self.options = JSONEncoder().encode(options)

		self.attrs.update(attrs)
	
	def render_js(self, field_id):
		if isinstance(self.source, list):
			source = JSONEncoder().encode(self.source)
		elif isinstance(self.source, str):
			source = "'%s'" % escape(self.source)
		else:
			raise ValueError('source type is not valid')
		
		options = ''
		if self.options:
			options += ',%s' % self.options

		return u'$(\'#%s\').autocomplete(%s%s);' % (field_id, source, options)

	def render(self, name, value=None, attrs=None):
		attrs = dict(attrs)
		attrs.update(name=name)
		if value:
			attrs.update(value=escape(smart_unicode(value)))

		if not self.attrs.has_key('id'):
			attrs.update(id='id_%s'%name)

		final_attrs = self.build_attrs(self.attrs, attrs)
		
		return u'''<input type="text" %(attrs)s/>
		<script type="text/javascript"><!--//
		%(js)s//--></script>
		''' % {
			'attrs' : flatatt(final_attrs),
			'js' : self.render_js(final_attrs['id']),
		}

class JQueryAutoContains(forms.TextInput):
	class Media:
		js = (
			'/media/ocemr/js/jquery-1.4.2.js',
			'/media/ocemr/js/jquery.autocomplete.js',
		)
		css = {
			'all': ('/media/ocemr/css/jquery.autocomplete.css',),
		}
	def __init__(self, source, options={}, attrs={}):
		"""source can be a list containing the autocomplete values or a
		string containing the url used for the XHR request.

		For available options see the autocomplete sample page::
		http://jquery.bassistance.de/autocomplete/"""

		self.options = {'matchContains': 'true', 'minChars': '2', 'max': '64'}
		self.attrs = {'autocomplete': 'off'}
		self.source = source
		if len(options) > 0:
			self.options = JSONEncoder().encode(options)

		self.attrs.update(attrs)
	
	def render_js(self, field_id):
		if isinstance(self.source, list):
			source = JSONEncoder().encode(self.source)
		elif isinstance(self.source, str):
			source = "'%s'" % escape(self.source)
		else:
			raise ValueError('source type is not valid')
		
		options = ''
		if self.options:
			options += ',%s' % self.options

		return u'$(\'#%s\').autocomplete(%s%s);' % (field_id, source, options)

	def render(self, name, value=None, attrs=None):
		attrs = dict(attrs)
		attrs.update(name=name)
		if value:
			attrs.update(value=escape(smart_unicode(value)))

		if not self.attrs.has_key('id'):
			attrs.update(id='id_%s'%name)

		final_attrs = self.build_attrs(self.attrs,attrs)
		
		return u'''<input type="text" %(attrs)s/>
		<script type="text/javascript"><!--//
		%(js)s//--></script>
		''' % {
			'attrs' : flatatt(final_attrs),
			'js' : self.render_js(final_attrs['id']),
		}

class CalendarWidget(forms.TextInput):
	"""
	var cal = new CalendarPopup('mydiv');
	cal.showNavigationDropdowns();
	cal.select(inputObject, anchorname, dateFormat);
	"""
	class Media:
		js = (
			'/media/ocemr/js/CalendarPopup.js',
			'/media/ocemr/js/AnchorPosition.js',
			'/media/ocemr/js/date.js',
			'/media/ocemr/js/PopupWindow.js',
		)
	def render(self, name, value, attrs=None):
		from django.utils import formats
		output = []
		output.append(
			"""<SCRIPT LANGUAGE="JavaScript" ID="jscal_%(NAME)s">
				var cal_%(NAME)s = new CalendarPopup();
				cal_%(NAME)s.showYearNavigation();
				cal_%(NAME)s.showYearNavigationInput();
			</SCRIPT>""" %{
				'NAME': name,
			})
		output.append(super(CalendarWidget, self).render(name, value, attrs))
		date_format = formats.get_format('DATE_INPUT_FORMATS')[0]
		js_date_format = date_format.replace('%d','dd').replace('%m','MM').replace('%Y','yyyy').replace('%y','yy')
		output.append(
			"""<a href="#"
				onClick='cal_%(NAME)s.select(document.forms[0].id_%(NAME)s,"%(NAME)s","%(DATE_FORMAT)s"); return false;'
			 name="%(NAME)s" id="%(NAME)s">Show Calendar</a>
			""" % \
				{
					'NAME': name,
					'DATE_FORMAT': js_date_format,
				})

		return mark_safe(u''.join(output))
