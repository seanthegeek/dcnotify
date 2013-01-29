'''
This in an example of the secrets.py contains the secret app settings.
secrets.py is imported by config.py and is listed in .gitignore for security.
'''
# Flask secret for sessions
SECRET_KEY = ""

# Admin email address
ADMIN_MAIL = ""

# Twitter API credentials
TWITTER_OAUTH_TOKEN = ""
TWITTER_OAUTH_SECRET = ""
TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""

# Recaptcha settings
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""
RECAPTCHA_OPTIONS = {'theme': 'white'}

# SMTP settings
MAIL_SERVER = ""
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USERNAME = ADMIN_MAIL
MAIL_PASSWORD = ""
