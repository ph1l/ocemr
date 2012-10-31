
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
def change_password(request):
	"""
	"""
	from ocemr.forms import ChangePasswordForm
	if request.method == 'POST':
		form = ChangePasswordForm(request.user, request.POST)
		if form.is_valid():
			request.user.set_password(form.cleaned_data['newPassword'])
			request.user.save()
			return HttpResponseRedirect('/close_window/')
	else:
		form = ChangePasswordForm(request.user)
	return render_to_response('popup_form.html', {
		'title': 'Change Password',
		'form_action': '/user_prefs/change_password/',
		'form': form,
	},context_instance=RequestContext(request))

@login_required
def get_backup(request):
	"""
	"""
	if not request.user.is_staff:
		return HttpResponse( "Permission Denied." )

	import os, time
	from django.http import HttpResponse
	from django.core.servers.basehttp import FileWrapper
	from django.core.management import call_command, CommandError
	from ocemr.settings import VAR_PATH, DB_BACKUP_ENCRYPT, DATABASES

	DATABASE_ENGINE=DATABASES['default']['ENGINE'].split(".")[-1]

	backup_dir = '%s/backups'%(VAR_PATH)
	if not os.path.exists(backup_dir):
		os.makedirs(backup_dir)
	outfile = os.path.join(backup_dir, 'backup_%s.%s' % (time.strftime('%y%m%d-%H%M%S'),DATABASE_ENGINE))
	try:
		call_command('backupdb', outfile)
	except CommandError:
		return render_to_response('popup_lines.html', {'lines': CommandError, 'link_text': """<a href="#" onclick="window.print();return false;">Print</a>"""})
	if DB_BACKUP_ENCRYPT:
		outfile += ".gpg"
	else:
		outfile += ".bz2"
	wrapper = FileWrapper(file(outfile))
	response = HttpResponse(wrapper, content_type='text/plain')
	response['Content-Length'] = os.path.getsize(outfile)
	response['Content-Disposition'] = 'attachment; filename=%s'%(os.path.basename(outfile))
	return response

@login_required
def restore_backup(request):
	"""
	allow admin user to upload a restore file and have the system use it.
	"""

	if not request.user.is_staff:
		return HttpResponse( "Permission Denied." )

	from ocemr.forms import UploadBackupForm
	from django.core.management import call_command, CommandError

	if request.method == 'POST':
		form = UploadBackupForm(request.POST, request.FILES)
		if form.is_valid():
			f = request.FILES['file']
			try:
				with open('/tmp/%s'%(f), 'wb+') as destination:
					for chunk in f.chunks():
						destination.write(chunk)
				call_command('restoredb', "/tmp/%s"%(f))
					
			except Exception, err:
				return render_to_response('popup_lines.html', {'lines': "ERROR: %s"%err})
			return HttpResponseRedirect('/close_window/')
	else:
		form = UploadBackupForm()

	return render_to_response( 'popup_form.html',
			{
			'title': 'Restore from a backup',
			'form_action': '/restore_backup/',
			'form': form
			},
		context_instance=RequestContext(request) )


@login_required
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

@login_required
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

def village_merge_wizard(request):
	"""
	"""
	if not request.user.is_staff:
		return HttpResponse( "Permission Denied." )

	from ocemr.models import Village, Patient
	from ocemr.forms import MergeVillageForm

	valid_form=False

	if request.method == 'POST': # If the form has been submitted...
		form = MergeVillageForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			villageIncorrect = form.cleaned_data['villageIncorrect']
			villageCorrect = form.cleaned_data['villageCorrect']
			valid_form=True
	else:
		form = MergeVillageForm() # An unbound form
	if not valid_form:
		return render_to_response('popup_form.html', {
			'title': 'Merge Patient Records',
			'form_action': '/village_merge_wizard/',
			'form': form,
		},context_instance=RequestContext(request))
	out_txt="Merge %s: %s\n  into %s: %s\n\n"%(villageIncorrect.id, villageIncorrect, villageCorrect.id, villageCorrect)

	patients=	Patient.objects.filter(village=villageIncorrect)

	for o in patients: out_txt += "  -> Patient: %s\n"%(o)

	out_txt += "\n\nThere is NO UNDO function to reverse this change.\n"
	out_txt += "Please be sure this is what you want before continuing...\n"
	out_link = "<A HREF=/village_merge_wizard/%d/%d/>Do the merge!</A> or "%(villageCorrect.id,villageIncorrect.id)
	return render_to_response('popup_info.html', {
		'title': 'Schedule Patient Visit',
		'info': out_txt,
		'link_text': out_link,
		})

@login_required
def village_merge_wizard_go(request,villageId,villageIncorrectId):
	"""
	"""
	if not request.user.is_staff:
		return HttpResponse( "Permission Denied." )

	from ocemr.models import Village, Patient

	village = Village.objects.get(pk=int(villageId))
	villageIncorrect = Village.objects.get(pk=int(villageIncorrectId))

	patients = Patient.objects.filter(village=villageIncorrect)

	for o in patients:
		o.village=village
		o.save()
	villageIncorrect.delete()
	return HttpResponseRedirect('/close_window/')
