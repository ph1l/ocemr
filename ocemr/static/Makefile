include ../../makefile.defines
all:
	-echo nothing to do
install:
	for subdir in css js img; do \
		install -m 755 -d $(DESTDIR)$(WWW)/media/ocemr/$$subdir; \
		install -m 644 ./$$subdir/* $(DESTDIR)$(WWW)/media/ocemr/$$subdir; \
	done
	
