include ../makefile.defines

SOURCE_TEMPLATES=engeye
all:
	-echo nothing to do
install:
	install -m 755 -d $(DESTDIR)$(SHARE)/contrib
	install -m 644 gpg_server_key.options $(DESTDIR)$(SHARE)/contrib
	for t in $(SOURCE_TEMPLATES); do \
		install -m 755 -d $(DESTDIR)$(SHARE)/contrib/source_data/$$t;\
		install -m 644 source_data/$$t/*.csv $(DESTDIR)$(SHARE)/contrib/source_data/$$t;\
	done
	install -m 755 -d $(DESTDIR)$(SHARE)/contrib/schema_updates
	install -m 644 schema_updates/* $(DESTDIR)$(SHARE)/contrib/schema_updates
