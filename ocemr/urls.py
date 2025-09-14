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
#       Copyright 2011-8 Philip Freeman <elektron@halo.nu>
##########################################################################

from django.conf.urls import include, url
from django.conf.urls.static import static

from . import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.auth import views as auth_views

import settings

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='login.html')),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(template_name='logout.html')),
    url(r'^user_prefs/$', views.util.user_prefs),
    url(r'^$', views.util.index),
    url(r'^user_prefs/change_password/$', views.util.change_password),
    url(r'^get_backup/$', views.util.get_backup),
    url(r'^restore_backup/$', views.util.restore_backup),
    url(r'^village_merge_wizard/$', views.util.village_merge_wizard),
    url(r'^village_merge_wizard/(?P<villageId>[0-9]+)/(?P<villageIncorrectId>[0-9]+)/$', views.util.village_merge_wizard_go),
    url(r'^autospel_name/(?P<inapp>.+)/(?P<inmodel>.+)/$', views.util.autospel_name),
    url(r'^autocomplete_name/(?P<inapp>.+)/(?P<inmodel>.+)/$', views.util.autocomplete_name),
    url(r'^autosearch_title/(?P<inapp>.+)/(?P<inmodel>.+)/$', views.util.autosearch_title),
    url(r'^blank/$',views.util.blank),
    url(r'^close_window/$',views.util.close_window),

    url(r'^patient_queue/$', views.patient.patient_queue),
    url(r'^patient_queue/(?P<dayoffset>[-0-9]+)/$', views.patient.patient_queue),
    url(r'^select_date_for_patient_queue/$', views.patient.select_date_for_patient_queue),
    url(r'^patient/(?P<id>\d+)/$', views.patient.patient),
    url(r'^patient/edit/age/(?P<id>\d+)/$', views.patient.patient_edit_age),
    url(r'^patient/edit/village/(?P<id>\d+)/$', views.patient.patient_edit_village),
    url(r'^patient/edit/name/(?P<id>\d+)/$', views.patient.patient_edit_name),
    url(r'^patient/edit/note/(?P<id>\d+)/$', views.patient.patient_edit_note),
    url(r'^patient/edit/gender/(?P<id>\d+)/$', views.patient.patient_edit_gender),
    url(r'^patient/edit/phone/(?P<id>\d+)/$', views.patient.patient_edit_phone),
    url(r'^patient/edit/email/(?P<id>\d+)/$', views.patient.patient_edit_email),
    url(r'^patient/edit/alt_contact_name/(?P<id>\d+)/$', views.patient.patient_edit_alt_contact_name),
    url(r'^patient/edit/alt_contact_phone/(?P<id>\d+)/$', views.patient.patient_edit_alt_contact_phone),
    url(r'^patient/search/$', views.patient.patient_search),
    url(r'^patient/new/$', views.patient.patient_new),
    url(r'^patient/schedule_new_visit/(?P<id>\d+)/$', views.patient.schedule_new_visit),
    url(r'^patient/schedule_walkin_visit/(?P<id>\d+)/$', views.patient.schedule_walkin_visit),
    url(r'^patient/delete_visit/(?P<id>\d+)/$', views.patient.delete_visit),
    url(r'^patient/edit_visit/(?P<id>\d+)/$', views.patient.edit_visit),
    url(r'^patient/edit_visit_reason/(?P<id>\d+)/$', views.patient.edit_visit_reason),
    url(r'^patient/edit_visit_seen/(?P<id>\d+)/$', views.patient.edit_visit_seen),
    url(r'^patient/merge/(?P<id>\d+)/$', views.patient.patient_merge),
    url(r'^patient/merge/(?P<id>\d+)/(?P<dupid>\d+)/$', views.patient.patient_do_merge),

    url(r'^visit/(?P<id>\d+)/$', views.visit.visit),
    url(r'^visit/(?P<id>\d+)/edit_type/$', views.visit.visit_edit_type),
    url(r'^visit/(?P<id>\d+)/set_type/(?P<new_type>\w+)/$', views.visit.visit_set_type),
    url(r'^visit/(?P<id>\d+)/seen/$', views.visit.visit_seen),
    url(r'^visit/(?P<id>\d+)/unseen/$', views.visit.visit_unseen),
    url(r'^visit/(?P<id>\d+)/claim/$', views.visit.visit_claim),
    url(r'^visit/(?P<id>\d+)/unclaim/$', views.visit.visit_unclaim),
    url(r'^visit/(?P<id>\d+)/finish/$', views.visit.visit_finish),
    url(r'^visit/(?P<id>\d+)/unfinish/$', views.visit.visit_unfinish),
    url(r'^visit/(?P<id>\d+)/allergy/new/$', views.visit.visit_allergy_new),
    url(r'^visit/(?P<id>\d+)/allergy/delete/(?P<oid>\d+)/$', views.visit.visit_allergy_delete),
    url(r'^visit/(?P<id>\d+)/past/$', views.visit.visit_past),
    url(r'^visit/(?P<id>\d+)/subj/$', views.visit.visit_subj),
    url(r'^visit/(?P<id>\d+)/subj/new/(?P<symptomtypeid>\d+)/$', views.visit.visit_subj_new),
    url(r'^visit/(?P<id>\d+)/subj/edit/(?P<visitsymptomid>\d+)/$', views.visit.visit_subj_edit),
    url(r'^visit/(?P<id>\d+)/subj/delete/(?P<visitsymptomid>\d+)/$', views.visit.visit_subj_delete),
    url(r'^visit/(?P<id>\d+)/obje/$', views.visit.visit_obje),
    url(r'^visit/(?P<id>\d+)/obje/vitals/new/$', views.visit.visit_obje_vitals_new),
    #url(r'^visit/(?P<id>\d+)/obje/vital/new/(?P<vitaltypeid>\d+)/$', views.visit.visit_obje_vital_new),
    url(r'^visit/(?P<id>\d+)/obje/vital/delete/(?P<oid>\d+)/$', views.visit.visit_obje_vital_delete),
    url(r'^visit/(?P<id>\d+)/obje/examNote/new/(?P<examnotetypeid>\d+)/$', views.visit.visit_obje_examNote_new),
    url(r'^visit/(?P<id>\d+)/obje/examNote/edit/(?P<examnoteid>\d+)/$', views.visit.visit_obje_examNote_edit),
    #url(r'^visit/(?P<id>\d+)/obje/examNote/delete/(?P<examnoteid>\d+)/$', views.visit.visit_obje_examNote_delete),
    url(r'^visit/(?P<id>\d+)/labs/$', views.visit.visit_labs),
    url(r'^visit/(?P<id>\d+)/labs/new/(?P<labtypeid>\d+)/$', views.visit.visit_labs_new),
    url(r'^visit/(?P<id>\d+)/plan/$', views.visit.visit_plan),
    url(r'^visit/(?P<id>\d+)/plan/diag/new/$', views.visit.visit_plan_diag_new),
    url(r'^visit/(?P<id>\d+)/plan/diag/new/(?P<dtid>\d+)/$', views.visit.visit_plan_diag_new_bytype),
    url(r'^visit/(?P<id>\d+)/meds/$', views.visit.visit_meds),
    url(r'^visit/(?P<id>\d+)/meds/new/(?P<did>\d+)/$', views.visit.visit_meds_new),
    url(r'^visit/(?P<id>\d+)/refe/$', views.visit.visit_refe),
    url(r'^visit/(?P<id>\d+)/refe/new/$', views.visit.visit_refe_new),
    url(r'^visit/(?P<id>\d+)/refe/edit/(?P<refid>\d+)/$', views.visit.visit_refe_edit),
    url(r'^visit/(?P<id>\d+)/note/$', views.visit.visit_note),
    url(r'^visit/(?P<id>\d+)/collect/$', views.visit.visit_collect),
    url(r'^visit/(?P<id>\d+)/bill_amount/$', views.visit.visit_bill_amount),
    url(r'^visit/(?P<id>\d+)/cost_estimate_detail/$', views.visit.visit_cost_estimate_detail),
    url(r'^visit/(?P<id>\d+)/resolve/$', views.visit.visit_resolve),
    url(r'^visit/(?P<id>\d+)/unresolve/$', views.visit.visit_unresolve),
    url(r'^visit/(?P<id>\d+)/record/(?P<type>\w+)/$', views.visit.visit_record),

    url(r'^visit/(?P<id>\d+)/preg/$', views.pregnancy.pregnancy),
    url(r'^visit/(?P<id>\d+)/preg/new/$', views.pregnancy.pregnancy_new),
    url(r'^visit/(?P<id>\d+)/preg/edit/(?P<pregid>\d+)/$', views.pregnancy.pregnancy_edit),

    url(r'^lab_queue/$', views.lab.lab_queue),
    url(r'^lab/(?P<id>\d+)/start/$', views.lab.lab_start),
    url(r'^lab/(?P<id>\d+)/cancel/$', views.lab.lab_cancel),
    url(r'^lab/(?P<id>\d+)/fail/$', views.lab.lab_fail),
    url(r'^lab/(?P<id>\d+)/complete/$', views.lab.lab_complete),
    url(r'^lab/(?P<id>\d+)/reorder/$', views.lab.lab_reorder),
    url(r'^lab/(?P<id>\d+)/notate/$', views.lab.lab_notate),

    url(r'^diag/(?P<id>\d+)/stat_change/(?P<newstat>\w+)/$', views.diag.diag_stat_change),
    url(r'^diag/(?P<id>\d+)/edit/notes/$', views.diag.diag_edit_notes),
    url(r'^diag/(?P<id>\d+)/history/$', views.diag.diag_history),
    url(r'^diag/patienttypehistory/(?P<pid>\d+)/(?P<dtid>\d+)/$', views.diag.diag_patienttypehistory),
    url(r'^diag/(?P<id>\d+)/delete/$', views.diag.diag_delete),

    url(r'^med_queue/$', views.med.med_queue),
    url(r'^meds/(?P<vid>\d+)/$', views.med.meds_view),
    url(r'^med/(?P<id>\d+)/dispense/$', views.med.med_dispense),
    url(r'^med/(?P<id>\d+)/undo_dispense/$', views.med.med_undo_dispense),
    url(r'^med/(?P<id>\d+)/substitute/$', views.med.med_substitute),
    url(r'^med/(?P<id>\d+)/cancel/$', views.med.med_cancel),
    url(r'^med/(?P<id>\d+)/undo_cancel/$', views.med.med_undo_cancel),
    url(r'^med/(?P<id>\d+)/notate/$', views.med.med_notate),
    url(r'^med/(?P<id>\d+)/edit/$', views.med.med_edit),

    url(r'^reports/$', views.reports.index),
    url(r'^reports/legacy/patient/daily/$', views.reports.legacy_patient_daily),
    url(r'^reports/diagnosis_patient/$', views.reports.diagnosis_patient),
    url(r'^reports/diagnosis/tally/$', views.reports.diagnosis_tally),
    url(r'^reports/clinician/tally/$', views.reports.clinician_tally),
    url(r'^reports/lab/tally/$', views.reports.lab_tally),
    url(r'^reports/med/tally/$', views.reports.med_tally),
    url(r'^reports/village/tally/$', views.reports.village_tally),
    url(r'^reports/cashflow/$', views.reports.cashflow),
    url(r'^reports/accounts_outstanding/$', views.reports.accounts_outstanding),
    url(r'^reports/hmis105/$', views.reports.hmis105),
    url(r'^reports/med_pricelist/$', views.reports.med_pricelist),

    url(r'^graphs/test_matplotlib/$', views.graphs.test_matplotlib),
    url(r'^graphs/vitals/(?P<id>\d+)/bp.png$', views.graphs.vitals_bp),
    url(r'^graphs/vitals/(?P<id>\d+)/temp.png$', views.graphs.vitals_temp),
    url(r'^graphs/vitals/(?P<id>\d+)/hrrr.png$', views.graphs.vitals_hrrr),
    url(r'^graphs/vitals/(?P<id>\d+)/hw.png$', views.graphs.vitals_height_weight),
    url(r'^graphs/vitals/(?P<id>\d+)/spo2o2.png$', views.graphs.vitals_spo2_o2),
    url(r'^graphs/vitals/(?P<id>\d+)/$', views.graphs.vitals_graphs_index),
]
