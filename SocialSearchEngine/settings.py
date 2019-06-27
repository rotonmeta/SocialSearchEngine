import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ys#(4)#yj=^lk0ai8(jr@+_#a(xr%eabn&+9y#t@=_8w40m5nz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']  #modificare quando debug = false

#CSRF_COOKIE_SECURE = True
#SESSION_COOKIE_SECURE = True
#X_FRAME_OPTIONS = 'DENY'
#SECURE_CONTENT_TYPE_NOSNIFF = True
#SECURE_BROWSER_XSS_FILTER = True

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
os.environ['HTTPS'] = "on"
os.environ['wsgi.url_scheme'] = 'https'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# Application definition

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'social_core.backends.facebook.FacebookOAuth2',
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'app',
    'Score_evaluator',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',

]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'SocialSearchEngine.urls'


WSGI_APPLICATION = 'SocialSearchEngine.wsgi.application'

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
            'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
        }
    }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'ebdb',
#         'USER':'roton',
#         'PASSWORD': '18shtator',
#         'HOST': 'aa1njbwlpsbdg7p.cqnyuin38az6.us-west-2.rds.amazonaws.com',
#         'PORT': '3306',
#         'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
#     }
# }


SOCIALACCOUNT_PROVIDERS = \
    {'facebook':
         {'METHOD': 'js_sdk',
          'SCOPE': ['email',
                    'public_profile',
                    'user_likes',
                    'user_posts',
                    'user_friends'],
          #'AUTH_PARAMS': {'auth_type': 'reauthenticate'}, #added by rm
          'FIELDS': [
              'id',
              'email',
              'name',
              'first_name',
              'last_name',
              'verified',
              'locale',
              'timezone',
              'link',
              'updated_time'],
          'EXCHANGE_TOKEN': True,
          'ACCOUNT_SESSION_REMEMBER': None,
          'LOCALE_FUNC': lambda request: 'en_US',
          'VERIFIED_EMAIL': False,
          'VERSION': 'v3.3',
          }
     }

ACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_REDIRECT_URL = ('/')

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

#LOGIN_REDIRECT_URL = 'http://localhost:8000/'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Pacific'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = 'static'




