"""Project configuration file"""

# ignore wildcard import
# pylint: disable=W0614
# pylint: disable=W0401
# Package namespace false-positive
# pylint: disable=W0403

from dcnotify.secrets import *

DEBUG = False

DC_YEAR = 2014

BABEL_DEFAULT_LOCALE = 'en_US'
BABEL_DEFAULT_TIMEZONE = 'UTC'

if DEBUG is False:
    SERVER_NAME = "dcnotify.net"

SQLALCHEMY_DATABASE_URI = "sqlite:///dcnotify.db"
DEFAULT_MAIL_SENDER = "noreply@dcnotify.net"
MAIL_PREFIX = "[D*C Notifications]"
