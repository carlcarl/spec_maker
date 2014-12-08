from spec_maker.settings.staging import *

# There should be only minor differences from staging

DATABASES['default']['NAME'] = 'spec_maker_production'
DATABASES['default']['USER'] = 'spec_maker_production'

EMAIL_SUBJECT_PREFIX = '[Spec_Maker Prod] '

# Uncomment if using celery worker configuration
# BROKER_URL = 'amqp://spec_maker_production:%(BROKER_PASSWORD)s@%(BROKER_HOST)s/spec_maker_production' % os.environ