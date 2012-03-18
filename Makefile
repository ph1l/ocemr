include makefile.defines

SITE_FILES=admin.py forms.py __init__.py manage.py models.py urls.py widgets.py
SITE_DIRS=formats formats/en formats/en_GB templates templatetags views \
	management management/commands

all: $(SITE_FILES)

install:
	install -d $(DESTDIR)$(SITE)
	install -d $(DESTDIR)$(CONF)
	install -m 644 $(SITE_FILES) $(DESTDIR)$(SITE)
	./util/make_version.sh > version.py
	install -m 644 version.py $(DESTDIR)$(SITE)
	for subdir in $(SITE_DIRS); do \
		install -d $(DESTDIR)$(SITE)/$$subdir; \
		install -m 644 `find $$subdir -mindepth 1 -maxdepth 1 -type f` $(DESTDIR)$(SITE)/$$subdir ; \
	done
	make -C util install
	install -T -o root -g www-data -m 640 settings.py.DIST $(DESTDIR)$(CONF)/settings.py
	install -m 644 apache2.conf $(DESTDIR)$(CONF)
	make -C static_media install
	make -C contrib install

pkg:
	dpkg-buildpackage -rfakeroot -us -uc
pkgtest:
	lintian ../ocemr_*_all.deb
pkgclean:
	fakeroot ./debian/rules clean
