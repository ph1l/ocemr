include ../makefile.defines

UTILS=dump_anon_data.py setup_gpg_server_key.sh \
	import_dx_csv.py import_examnotes_csv.py import_labs_csv.py \
	import_rx_csv.py import_symptom_csv.py import_test_patients_csv.py \
	import_vital_csv.py import_vacs_csv.py \
	most_visits.py update_visit.py update_vitals.py \
	initialize_sqlite_db.sh initialize_mysql_db.sh cron-daily.sh

all:
	-echo nothing to do
install:
	install -m 755 -d $(DESTDIR)$(SHARE)/util
	install -m 755 $(UTILS) $(DESTDIR)$(SHARE)/util
