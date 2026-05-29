from .base import *

DEBUG = True
ALLOWED_HOSTS = []

STATICFILES_DIRS = [BASE_DIR / '_common' / 'static']

MIDDLEWARE = [
	'_conf.middleware.RequestTimingMiddleware',
	*MIDDLEWARE,
]

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'edonius.perf': {
			'handlers': ['console'],
			'level': 'INFO',
			'propagate': False,
		},
	},
}
