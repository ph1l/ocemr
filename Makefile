include makefile.defines

SITE_FILES=ocemr/admin.py ocemr/forms.py ocemr/__init__.py ocemr/models.py ocemr/urls.py ocemr/widgets.py ocemr/wsgi.py manage.py
SITE_DIRS=formats formats/en formats/en_GB templates templatetags views \
	management management/commands migrations

all: $(SITE_FILES)

install:
	install -d $(DESTDIR)$(SITE)
	install -d $(DESTDIR)$(CONF)
	install -d $(DESTDIR)$(CONF)/apache2/conf
	install -d $(DESTDIR)$(CONF)/apache2/sites
	install -m 644 $(SITE_FILES) $(DESTDIR)$(SITE)
	# Don't build the version in build, use the one checked in
	#./util/make_version.sh > version.py
	install -m 644 ocemr/version.py $(DESTDIR)$(SITE)
	for subdir in $(SITE_DIRS); do \
		install -d $(DESTDIR)$(SITE)/$$subdir; \
		install -m 644 `find ocemr/$$subdir -mindepth 1 -maxdepth 1 -type f` $(DESTDIR)$(SITE)/$$subdir ; \
	done
	make -C util install
	install -T -o root -g www-data -m 640 package_configs/settings.py $(DESTDIR)$(CONF)/settings.py
	install -m 644 package_configs/conf/ocemr.conf $(DESTDIR)$(CONF)/apache2/conf
	install -m 644 package_configs/sites/ocemr.conf $(DESTDIR)$(CONF)/apache2/sites
	install -T -m 640 package_configs/util_conf.py $(DESTDIR)$(CONF)/util_conf.py
	make -C ocemr/static install
	make -C contrib install
	install -o root -g root -m 755 ocemr-manage $(DESTDIR)/usr/sbin

/var/lib/machines/ocemr-server:
	debootstrap --include=systemd buster /var/lib/machines/ocemr-server

container-build: /var/lib/machines/ocemr-server
	systemd-nspawn -U -D /var/lib/machines/ocemr-server --machine ocemr-server --bind $$PWD/:/build /build/contrib/nspawn/build

container-clean:
	rm -rf /var/lib/machines/ocemr-server

pkg:
	dpkg-buildpackage -rfakeroot -us -uc
pkgtest:
	lintian ../ocemr_*_all.deb
pkgclean:
	fakeroot ./debian/rules clean
