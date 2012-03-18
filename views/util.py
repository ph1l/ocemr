
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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest

from django.db.models import get_model
from django.views.decorators.cache import cache_page
from django.template import RequestContext

def close_window(request):
	return render_to_response('close_window.html', {})

def blank(request):
	return render_to_response('blank.html', {})

@login_required
def index(request):
	"""
	Main Landing Page
		-Redirect to patient Queue
	"""
	return HttpResponseRedirect('/patient_queue/')

@login_required
def user_prefs(request):
	"""
	"""
	return render_to_response(
		'user_prefs.html', locals(),
		context_instance=RequestContext(request))

@login_required
def get_backup(request):
	"""
	"""
	import os, time
	from django.http import HttpResponse
	from django.core.servers.basehttp import FileWrapper
	from django.core.management import call_command, CommandError
	from ocemr.settings import VAR_PATH, DB_BACKUP_ENCRYPT
	backup_dir = '%s/backups'%(VAR_PATH)
	if not os.path.exists(backup_dir):
		os.makedirs(backup_dir)
	outfile = os.path.join(backup_dir, 'backup_%s.sql' % time.strftime('%y%m%d-%H%M%S'))
	try:
		call_command('backupdb', outfile)
	except CommandError:
		return render_to_response('popup_lines.html', {'lines': CommandError, 'link_text': """<a href="#" onclick="window.print();return false;">Print</a>"""})
	if DB_BACKUP_ENCRYPT:
		outfile += ".gpg"
	wrapper = FileWrapper(file(outfile))
	response = HttpResponse(wrapper, content_type='text/plain')
	response['Content-Length'] = os.path.getsize(outfile)
	response['Content-Disposition'] = 'attachment; filename=%s'%(os.path.basename(outfile))
	return response

def autocomplete_name(request, inapp, inmodel):
	"""
	"""
	def iter_results(results):
		if results:
			for r in results:
				yield '%s|%s\n' % (r.name, r.id)
	
	if not request.GET.get('q'):
		return HttpResponse(mimetype='text/plain')
	
	q = request.GET.get('q')
	limit = request.GET.get('limit', 15)
	try:
		limit = int(limit)
	except ValueError:
		return HttpResponseBadRequest() 
	Foo = get_model( inapp, inmodel )
	foos = Foo.objects.filter(name__istartswith=q,active=True)[:limit]
	return HttpResponse(iter_results(foos), mimetype='text/plain')

autocomplete_name = cache_page(autocomplete_name, 60 * 60)

def autosearch_title(request, inapp, inmodel):
	"""
	"""
	def iter_results(results):
		if results:
			for r in results:
				yield '%s|%s\n' % (r.title, r.id)
	
	if not request.GET.get('q'):
		return HttpResponse(mimetype='text/plain')
	
	q = request.GET.get('q')
	limit = request.GET.get('limit', 15)
	try:
		limit = int(limit)
	except ValueError:
		return HttpResponseBadRequest() 
	Foo = get_model( inapp, inmodel )
	foos = Foo.objects.filter(title__icontains=q,active=True) #[:limit]
	return HttpResponse(iter_results(foos), mimetype='text/plain')

autosearch_title = cache_page(autosearch_title, 60 * 60)

