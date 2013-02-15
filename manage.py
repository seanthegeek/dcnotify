#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Provides commands for managing D*C Notifications
'''
# Ignore flask case
# pylint: disable=C0103

# Resolution false positives
# pylint: disable=F0401
# pylint: disable=E0611
# pylint: disable=W0611
# pylint: disable=W0403
# pylint: disable=E1101

from os import path
from time import time
from datetime import datetime, timedelta
from json import loads

from flask.ext.script import Manager
from flask_mail import Message
from flask import render_template

from dcnotify import app, db, __version__
from dcnotify.controllers import get_status, _purge_subscribers, \
    _update_guests, post_tweet, send_mail, set_notice, email_subscribers


__author__ = "Sean Whalen"
__copyright__ = "Copyright (C) 2012 %s" % __author__
__license__ = "MIT"


manager = Manager(app)


@manager.command
def init():
    """Creates the database."""
    print("Creating database...")
    db.create_all()


@manager.command
def update():
    """Triggers database maintiance."""
    print("Updating database...")
    _update_guests()
    _purge_subscribers()


@manager.command
def notice(message=None, email=False, tweet=False):
    """Sets or remove a site-wide notice."""
    if email:
        print("Sending mail...")
        email_subscribers("Status update", message)

    if tweet:
        post_tweet(message)

    set_notice(message)


@manager.command
def status():
    """Displays various site status information."""
    data = get_status()

    for key in data:
        print (key + '\t' + str(data[key]))


@manager.command
def tweet(message, silent=False):
    """Sends a update to Twitter."""
    post_tweet(message)

    if silent is not True:
        print("Update posted.")


if __name__ == "__main__":
    manager.run()
