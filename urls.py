########################################################################## #
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

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings

urlpatterns = patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
    #Development
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
	{'document_root': settings.APP_PATH+'/static_media/css'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
	{'document_root': settings.APP_PATH+'/static_media/js'}),
)
urlpatterns += patterns('ocemr.views.util',

    (r'^$', 'index'),
    (r'^autocomplete_name/(?P<inapp>.+)/(?P<inmodel>.+)/$', 'autocomplete_name'),
    (r'^autosearch_title/(?P<inapp>.+)/(?P<inmodel>.+)/$', 'autosearch_title'),
    (r'^blank/$','blank'),
    (r'^close_window/$','close_window'),
)
urlpatterns += patterns('ocemr.views.patient',
    (r'^patient_queue/$', 'patient_queue'),
    (r'^patient_queue/(?P<dayoffset>[-0-9]+)/$', 'patient_queue'),
    (r'^patient/(?P<id>\d+)/$', 'patient'),
    (r'^patient/edit/age/(?P<id>\d+)/$', 'patient_edit_age'),
    (r'^patient/edit/village/(?P<id>\d+)/$', 'patient_edit_village'),
    (r'^patient/edit/name/(?P<id>\d+)/$', 'patient_edit_name'),
    (r'^patient/edit/note/(?P<id>\d+)/$', 'patient_edit_note'),
    (r'^patient/search/$', 'patient_search'),
    (r'^patient/new/$', 'patient_new'),
    (r'^patient/schedule_new_visit/(?P<id>\d+)/$', 'schedule_new_visit'),
    (r'^patient/schedule_walkin_visit/(?P<id>\d+)/$', 'schedule_walkin_visit'),
    (r'^patient/delete_visit/(?P<id>\d+)/$', 'delete_visit'),
    (r'^patient/edit_visit/(?P<id>\d+)/$', 'edit_visit'),
    (r'^patient/edit_visit_reason/(?P<id>\d+)/$', 'edit_visit_reason'),
    (r'^patient/edit_visit_seen/(?P<id>\d+)/$', 'edit_visit_seen'),
    (r'^patient/merge/(?P<id>\d+)/$', 'patient_merge'),
    (r'^patient/merge/(?P<id>\d+)/(?P<dupid>\d+)/$', 'patient_do_merge'),
)
urlpatterns += patterns('ocemr.views.visit',
    (r'^visit/(?P<id>\d+)/$', 'visit'),
    (r'^visit/(?P<id>\d+)/seen/$', 'visit_seen'),
    (r'^visit/(?P<id>\d+)/unseen/$', 'visit_unseen'),
    (r'^visit/(?P<id>\d+)/claim/$', 'visit_claim'),
    (r'^visit/(?P<id>\d+)/unclaim/$', 'visit_unclaim'),
    (r'^visit/(?P<id>\d+)/finish/$', 'visit_finish'),
    (r'^visit/(?P<id>\d+)/unfinish/$', 'visit_unfinish'),
    (r'^visit/(?P<id>\d+)/allergy/new/$', 'visit_allergy_new'),
    (r'^visit/(?P<id>\d+)/allergy/delete/(?P<oid>\d+)/$', 'visit_allergy_delete'),
    (r'^visit/(?P<id>\d+)/past/$', 'visit_past'),
    (r'^visit/(?P<id>\d+)/subj/$', 'visit_subj'),
    (r'^visit/(?P<id>\d+)/subj/new/(?P<symptomtypeid>\d+)/$', 'visit_subj_new'),
    (r'^visit/(?P<id>\d+)/subj/edit/(?P<visitsymptomid>\d+)/$', 'visit_subj_edit'),
    (r'^visit/(?P<id>\d+)/subj/delete/(?P<visitsymptomid>\d+)/$', 'visit_subj_delete'),
    (r'^visit/(?P<id>\d+)/obje/$', 'visit_obje'),
    (r'^visit/(?P<id>\d+)/obje/vital/new/(?P<vitaltypeid>\d+)/$', 'visit_obje_vital_new'),
    (r'^visit/(?P<id>\d+)/obje/vital/delete/(?P<oid>\d+)/$', 'visit_obje_vital_delete'),
    (r'^visit/(?P<id>\d+)/obje/examNote/new/(?P<examnotetypeid>\d+)/$', 'visit_obje_examNote_new'),
    (r'^visit/(?P<id>\d+)/obje/examNote/edit/(?P<examnoteid>\d+)/$', 'visit_obje_examNote_edit'),
    #(r'^visit/(?P<id>\d+)/obje/examNote/delete/(?P<examnoteid>\d+)/$', 'visit_obje_examNote_delete'),
    (r'^visit/(?P<id>\d+)/labs/$', 'visit_labs'),
    (r'^visit/(?P<id>\d+)/labs/new/(?P<labtypeid>\d+)/$', 'visit_labs_new'),
    (r'^visit/(?P<id>\d+)/plan/$', 'visit_plan'),
    (r'^visit/(?P<id>\d+)/plan/diag/new/$', 'visit_plan_diag_new'),
    (r'^visit/(?P<id>\d+)/plan/diag/new/(?P<dtid>\d+)/$', 'visit_plan_diag_new_bytype'),
    (r'^visit/(?P<id>\d+)/meds/$', 'visit_meds'),
    (r'^visit/(?P<id>\d+)/meds/new/(?P<did>\d+)/$', 'visit_meds_new'),
    (r'^visit/(?P<id>\d+)/refe/$', 'visit_refe'),
    (r'^visit/(?P<id>\d+)/refe/new/$', 'visit_refe_new'),
    (r'^visit/(?P<id>\d+)/refe/edit/(?P<refid>\d+)/$', 'visit_refe_edit'),
    (r'^visit/(?P<id>\d+)/immu/$', 'visit_immu'),
    (r'^visit/(?P<id>\d+)/immu/new/$', 'visit_immu_new'),
    (r'^visit/(?P<id>\d+)/note/$', 'visit_note'),
    (r'^visit/(?P<id>\d+)/collect/$', 'visit_collect'),
    (r'^visit/(?P<id>\d+)/bill_amount/$', 'visit_bill_amount'),
    (r'^visit/(?P<id>\d+)/resolve/$', 'visit_resolve'),
    (r'^visit/(?P<id>\d+)/unresolve/$', 'visit_unresolve'),
    (r'^visit/(?P<id>\d+)/record/(?P<type>\w+)/$', 'visit_record'),
)
urlpatterns += patterns('ocemr.views.lab',
    (r'^lab_queue/$', 'lab_queue'),
    (r'^lab/(?P<id>\d+)/start/$', 'lab_start'),
    (r'^lab/(?P<id>\d+)/cancel/$', 'lab_cancel'),
    (r'^lab/(?P<id>\d+)/fail/$', 'lab_fail'),
    (r'^lab/(?P<id>\d+)/complete/$', 'lab_complete'),
    (r'^lab/(?P<id>\d+)/reorder/$', 'lab_reorder'),
    (r'^lab/(?P<id>\d+)/notate/$', 'lab_notate'),
)
urlpatterns += patterns('ocemr.views.diag',
    (r'^diag/(?P<id>\d+)/stat_change/(?P<newstat>\w+)/$', 'diag_stat_change'),
    (r'^diag/(?P<id>\d+)/edit/notes/$', 'diag_edit_notes'),
    (r'^diag/(?P<id>\d+)/history/$', 'diag_history'),
    (r'^diag/patienttypehistory/(?P<pid>\d+)/(?P<dtid>\d+)/$', 'diag_patienttypehistory'),
    (r'^diag/(?P<id>\d+)/delete/$', 'diag_delete'),
)
urlpatterns += patterns('ocemr.views.med',
    (r'^med_queue/$', 'med_queue'),
    (r'^meds/(?P<vid>\d+)/$', 'meds_view'),
    (r'^med/(?P<id>\d+)/dispense/$', 'med_dispense'),
    (r'^med/(?P<id>\d+)/undo_dispense/$', 'med_undo_dispense'),
    (r'^med/(?P<id>\d+)/substitute/$', 'med_substitute'),
    (r'^med/(?P<id>\d+)/cancel/$', 'med_cancel'),
    (r'^med/(?P<id>\d+)/undo_cancel/$', 'med_undo_cancel'),
    (r'^med/(?P<id>\d+)/notate/$', 'med_notate'),
    (r'^med/(?P<id>\d+)/edit/$', 'med_edit'),
)
urlpatterns += patterns('ocemr.views.reports',
    (r'^reports/$', 'index'),
    (r'^reports/legacy/patient/daily/$', 'legacy_patient_daily'),
    (r'^reports/diagnosis/tally/$', 'diagnosis_tally'),
    (r'^reports/clinician/daily/$', 'clinician_daily'),
    (r'^reports/cashflow/$', 'cashflow'),
    (r'^reports/accounts_outstanding/$', 'accounts_outstanding'),
)
