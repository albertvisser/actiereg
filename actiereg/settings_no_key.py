"""Django settings for actiereg project.
"""
import pathlib

HERE = pathlib.Path(__file__).parent.resolve()


# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

DEBUG = True

ALLOWED_HOSTS = ['.lemoncurry.nl']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'actiereg._basic',
    'actiereg.probreg_pc',
    'actiereg.jvsdoe',
    'actiereg.leesJCL',
    'actiereg.actiereg_web',
    'actiereg.DocTool',
    'actiereg.afrift',
    'actiereg.htmledit',
    'actiereg.tcmdrkeys',
    'actiereg.versies',
    'actiereg.xmledit',
    'actiereg.apropos',
    'actiereg.DocTree',
    'actiereg.Todo',
    'django.contrib.admindocs',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # nieuw in 1.6
    'django.middleware.security.SecurityMiddleware',           # nieuw in 1.8
)

ROOT_URLCONF = 'actiereg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(HERE / 'templates'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            ## 'loaders': [
            ## #     'django.template.loaders.eggs.Loader',
            ##     'django.template.loaders.filesystem.Loader',
            ##     'django.template.loaders.app_directories.Loader',
            ## ],
        },
    },
]

WSGI_APPLICATION = 'actiereg.wsgi.application'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',     # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': str(HERE / 'actiereg.db'),       # Or path to database file if using sqlite3.
        'USER': '',             # Not used with sqlite3.
        'PASSWORD': '',         # Not used with sqlite3.
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SITES = {
    "doctool": "http://myprojects.lemoncurry.nl",
    "probreg": "http://actiereg.lemoncurry.nl"}

CSRF_COOKIE_DOMAIN = '.lemoncurry.nl'
