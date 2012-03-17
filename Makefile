include makefile.defines


SITE_FILES=admin.py forms.py __init__.py manage.py models.py settings.py \
	urls.py widgets.py
SITE_DIRS=formats formats/en formats/en_GB templates templatetags views

all: $(SITE_FILES)

install:
	install -d $(DESTDIR)$(SITE)
	install -m 644 $(SITE_FILES) $(DESTDIR)$(SITE)
	for subdir in $(SITE_DIRS); do \
		install -d $(DESTDIR)$(SITE)/$$subdir; \
		install -m 644 `find $$subdir -mindepth 1 -maxdepth 1 -type f` $(DESTDIR)$(SITE)/$$subdir ; \
	done
	make -C static_media install
settings.py:
	cp -a settings.py.DIST settings.py
