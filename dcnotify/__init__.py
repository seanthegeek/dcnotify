#-*- coding: utf-8 -*-
'''
The D*C Notifications application module
'''
# pylint false positives
# pylint: disable=E0611
# pylint: disable=F0401

from logging import ERROR
from logging.handlers import SMTPHandler

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.babel import Babel
from flask_mail import Mail

__author__ = "Sean Whalen"
__copyright__ = "Copyright (C) 2012 %s" % __author__
__license__ = "MIT"
__version__ = "0.3.2"

# Ignore flask case
# pylint: disable=C0103

app = Flask(__name__)
app.config.from_pyfile("config.py")

if not app.debug:
    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['DEFAULT_MAIL_SENDER'],
                               [app.config['ADMIN_MAIL']],
                               'D*C Notifications Failed',
                               credentials=(app.config['MAIL_USERNAME'],
                               app.config['MAIL_PASSWORD']),
                               secure=())
    mail_handler.setLevel(ERROR)
    app.logger.addHandler(mail_handler)

db = SQLAlchemy(app)
babel = Babel(app)
mail = Mail(app)


import dcnotify.views
