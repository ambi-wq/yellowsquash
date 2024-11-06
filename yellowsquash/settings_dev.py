DATABASES = {
    # 'default': {
    #       'ENGINE': 'django.db.backends.postgresql',
    #      'NAME': 'yellowsquash',
    #     'USER': 'ysdbadmin',
    #     'PASSWORD': 'ysdev@2022',
    #     'HOST': 'localhost',
    #     'PORT': 5432
    # }

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yellowsquash',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': 5432
    }
}

# 'NAME': 'yellowsquash2',
# 'USER': 'postgres',
# 'PASSWORD': 'securedaccess',
# 'HOST': '94.130.34.104',
# 'PORT': 5482

DEBUG = True
CORS_ORIGIN_ALLOW_ALL=True

# mail config
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = '587'
# EMAIL_HOST_USER = 'prayas@opskube.com'
# EMAIL_HOST_PASSWORD = 'prayas9968'
# EMAIL_USE_TLS = True

# new gmail config
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@prolifiquetech.in'
EMAIL_HOST_PASSWORD = 'gramngbrxyfmtvjp'
EMAIL_USE_TLS = True


# aws config
AWS_ACCESS_KEY_ID = 'AKIAYNS5HOJOYJVEC666'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'yellowsquash-stage'
AWS_S3_CUSTOM_DOMAIN = 'https://yellowsquash-stage.s3.ap-south-1.amazonaws.com/'
AWS_S3_OBJECT_PARAMETERS = {}


# mobile otp config
API_KEY_2FACTOR = '4658f2bc-f395-11ea-9fa5-0200cd936042'

# email otp config
API_KEY_SENDINBLUE = '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'