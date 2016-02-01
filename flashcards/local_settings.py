# No trailing slash! Used to send links to validate and sign in with
WEBSITE_BASE_URI = 'http://woordenwords.nl'

DEBUG = True
VERSION = '0.3'

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'kevindunn'
EMAIL_HOST_PASSWORD = 'DrAD4dra'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'Woorden-Words Website <noreply@example.com>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
SEND_BROKEN_LINK_EMAILS = True

ADMINS = (('Kevin Dunn', 'kgdunn@gmail.com'), )
MANAGERS = ADMINS

LOG_FILENAME = '/Users/kevindunn/Personal/Myself/Learn-Dutch/flashcards/logfile.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILENAME,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'formatter': 'verbose',
        }
    },
    'formatters': {
        'verbose': {
            #'format': "%(levelname)s :: %(pathname)s:%(lineno)s :: %(asctime)s :: %(message)s",
            'format': ('%(asctime)s::%(levelname)s::%(filename)s::%(lineno)d::[%(funcName)s(...)] :: %(message)s')
            },
        'simple': {
            'format': '%(levelname)s %(message)s'
            },
        },
    'loggers': {
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'rsm.views': {
            'handlers': ['file', ],
            'level': 'DEBUG',
        }
    },
}

# Where should JQuery be served from?
JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js'
JQUERYUI_URL = 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js'
JQUERYUI_CSS = 'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css'

# If you use Piwik, Google Analytics, etc: add the code snippet here that
# will be placed as the last entry in the closing </head> tag.
ANALYTICS_SNIPPET = ''


