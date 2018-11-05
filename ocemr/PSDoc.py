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

class PSDoc():
	"""
	psdoc = PSDoc(margins=.75,debug=True)
	psdoc.text("Title", font_size=36)
	for i in range(10):
		psdoc.text("1234567890"*6, indent=float(i)/4.0)
		psdoc.text("abcdefghij"*6, indent=float(i)/4.0)
	psdoc.text(u"doesn\u2019t sleep well due to pain ", indent=float(i)/4.0)
	print psdoc.complete()
	#########################################

	teletypefont
	7.2: 65 characters wide at 12 pts.
	6: 78, 10
	
	ptsize / (5/3) = width
	"""

	def __init__(self, font_size=12, margins=None, debug=False):
		"""
		font_size - sets the default pt size for text
		margins - sets all 4 margins
		debug - set to true to draw an box on the margins
		"""
		#
		dpi=72
		font_name='teletypefont'

		self.width_ratio = float(5.0/3.0)

		import PSDraw
		import StringIO

		self.ps_out = StringIO.StringIO()
		self.dpi = float(dpi)
		self.font_name = font_name
		self.font_size = float(font_size)
		self.debug = debug
		self.line_spacing = float(2)
		if margins == None:
			self.margin_top = 1.0
			self.margin_left = 1.0
			self.margin_right = 1.0
			self.margin_bottom = 1.0
		else:
			self.margin_top = margins
			self.margin_left = margins
			self.margin_right =  margins
			self.margin_bottom = margins

		self.page_height = 11.0
		self.page_width = 8.5

		#self.tot_w = int(self.dpi * 8.5)
		#self.tot_h = int(self.dpi * 11)
		self.cur_h = -1

		self.ps = PSDraw.PSDraw(self.ps_out)
		self.ps.begin_document()
		self.ps.setfont(self.font_name, self.font_size)
		if self.debug:
			#Left 
			self.ps.line(
				(self.dpi*self.margin_left,
				 self.dpi*self.margin_bottom),
				(self.dpi*self.margin_left,
				 self.dpi*(self.page_height-self.margin_top))
				)
			#Top
			self.ps.line(
				(self.dpi*self.margin_left,
				 self.dpi*(self.page_height-self.margin_top)),
				(self.dpi*(self.page_width-self.margin_right),
				 self.dpi*(self.page_height-self.margin_top))
				)
			#Right
			self.ps.line(
				(self.dpi*(self.page_width-self.margin_right),
				 self.dpi*(self.page_height-self.margin_top)),
				(self.dpi*(self.page_width-self.margin_right),
				 self.dpi*self.margin_bottom),
				)
			#Bottom
			self.ps.line(
				(self.dpi*(self.page_width-self.margin_right),
				 self.dpi*self.margin_bottom),
				(self.dpi*self.margin_left,
				 self.dpi*self.margin_bottom)
				)

	def text(self, text, font_size=None, indent=0):
		"""
		text - the stuff to print... duh
		font_size - override the object default
		indent - in inches
		"""

		if font_size == None:
			font_size = self.font_size
		font_size = float(font_size)
		self.ps.setfont(self.font_name, font_size)
		indent = float(indent)
		if self.cur_h == -1:
			self.cur_h = int(self.dpi * (self.page_height-self.margin_top)) - (font_size)

		wrapped = 0.0

		
		while text != "":
			cur_h = self.cur_h
			max_chars = int(
				( self.dpi*(self.page_width-(self.margin_left+self.margin_right+indent)))
				/
				( float(font_size) / self.width_ratio )
				)
			line = text[0:max_chars]
			
			self.ps.text( (int(self.dpi*(self.margin_left+indent+wrapped)),self.cur_h), line.encode("utf-8"))
			text = text[max_chars:]
			self.cur_h = cur_h - ( font_size + self.line_spacing )
			wrapped = 0.5
		
	def complete(self):
		"""
		call this when you're done and it returns the postscript
		for your doc.
		"""
		self.ps.end_document()
		return self.ps_out.getvalue()

