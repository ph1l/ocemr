#
# OCEMR - settings.py
#
#     This is the main django settings file and must be valid python.
#

# DATABASES
DATABASES = {}

# mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ocemr',
        'USER': 'ocemr',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}

# sqlite3
# Remove / comment out to use mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/var/lib/ocemr/db/ocemr.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# DB_BACKUP_*
#
# To Encrypt Backups, you need to:
#
#  1). Generate a server key:
#
#      $ sudo /usr/share/ocemr/util/setup_gpg_server_key.sh
#
#  2). Set DB_BACKUP_ENCRYPT to "True".
#
#  TODO: document adding a personal key to the server keyring.

DB_BACKUP_ENCRYPT = False
DB_BACKUP_ENCRYPT_TO = ["ocemr@localhost"]

#
# DEBUG -
#    Set DEBUG = True in development
#

DEBUG = False

# ADMINS-
#     Set name and email addresses of administrators. Site error reports
#    get emailed here.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# SERVER_EMAIL -
#      Address from which the server sends email.
SERVER_EMAIL = 'ocemr@example.com'

# *_PATH -
#       Location the software is installed.
#
APP_PATH = "/usr/share/ocemr/apps/ocemr"
CONTRIB_PATH = "/usr/share/ocemr/contrib"
UTIL_PATH = "/usr/share/ocemr/util"
VAR_PATH = "/var/lib/ocemr"

#
# OCEMR PRINTER SETTINGS
#
# PRINTER_NAME -
#       Local CUPS printer name for printing records
#
# PAPER_SIZE -
#       Paper Size. 'letter' or 'A4'
#

PRINTER_NAME = "Some_CUPS_Printer"
PAPER_SIZE = "Letter"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Make this unique, and don't share it with anybody.
#
#  python -c 'import random; print "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])'
#
SECRET_KEY = '5!&)hu8!_=l-*y2gwm9z9z&qro+m7%wswqpzk1)hlt_nxi)k_x'

##############################################################################
#
# Settings beyond this point should, in most cases, be left untouched.
#
##############################################################################

# Session Security
#
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
USE_L10N = True
# LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
STATIC_URL = '/media/ocemr/'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
ROOT_URLCONF = 'ocemr.urls'
FORMAT_MODULE_PATH = 'ocemr.formats'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'ocemr',
)

ALLOWED_HOSTS = ('*')

import version
OCEMR_VERSION = version.OCEMR_VERSION
