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

user_home = path.expanduser("~")
activate = path.join(user_home, 'virtualenvs/dcnotify/bin/activate_this.py')
if path.exists(activate):
    execfile(activate, dict(__file__=activate))

import logging
from logging.handlers import SMTPHandler
from datetime import datetime, timedelta
from time import time
from json import loads

from flask.ext.script import Manager
from flask_mail import Message
from flask import render_template

from dcnotify import app, db, Guest, Subscriber, get_status,\
post_tweet, send_mail, set_notice, email_subscribers, __version__
from scraper import get_guests


__author__ = "Sean Whalen"
__copyright__ = "Copyright (C) 2012 %s" % __author__
__license__ = "MIT"

if not app.debug:
    mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                               app.config['DEFAULT_MAIL_SENDER'],
                               [app.config['ADMIN_MAIL']],
                               'D*C Notifications Command Failed',
                               credentials=(app.config['MAIL_USERNAME'],
                               app.config['MAIL_PASSWORD']),
                               secure=())
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

manager = Manager(app)

module_directory = path.dirname(__file__)


def _purge_subscribers():
    """Purges inactive subscribers from the database"""
    subscribers = Subscriber.query.filter_by(active=False).all()
    for subscriber in subscribers:
        expires = subscriber.timestamp + timedelta(hours=24)
        if datetime.utcnow() > expires:
            db.session.delete(subscriber)

    db.session.commit()


def _update_guests():
    """Processes the D*C guest list"""
    year = str(app.config['DC_YEAR'])
    existing_count = 0
    print("Getting guest list...")
    guests = get_guests()
    new_guests = []

    print("Updating guests...")
    for guest in guests:
        record = Guest.query.filter_by(id=guest['id']).first()
        if record is None:
            new_guests.append(guest)
            guest = Guest(guest['id'], guest['url'], guest['name'], guest['description'])
            db.session.add(guest)
        else:
            existing_count += 1
            record.name = guest['name']
            record.url = guest['url']
            record.description = guest['description']

        db.session.commit()

    full_path_to_file = path.join(module_directory, "updated.txt")
    updated_file = open(full_path_to_file, "w")
    updated_file.write(str(time()))
    updated_file.close()

    if existing_count > 0:
        print("Updated %d existing guest(s)...") % existing_count

    new_count = len(new_guests)
    total_count = existing_count + new_count

    if new_count > 0:
        print("Found %d new guest(s)!") % new_count

        print("Sending Twitter update(s)...")
        for guest in new_guests:
            message = "%s is a guest at #DragonCon %s! %s" % (guest['name'],
                                                              year,
                                                               guest['url'])
            tweet(message, silent=True)

        print("Building email message...")
        message = render_template('emails/guest.html', guests=new_guests)

        if new_count > 1:
            subject = "New guests added!"
        else:
            subject = "New guest added!"

        print("Sending emails...")
        email_subscribers(subject, message)

        full_path_to_file = path.join(module_directory, "custom.txt")
        if path.exists(full_path_to_file):
            updated_file = open(full_path_to_file, "r")
            print("Checking custom checks...")
            custom_file = open(full_path_to_file, "r")
            checks = loads(custom_file.read())
            for check in checks:
                for guest in new_guests:
                    if guest['name'] == check['name']:
                        print("Found %s! sending email(s)...") % check['name']
                        messages = []
                        for recipient in check['recipients']:
                            message = Message(recipients=[recipient],
                            subject=check['subject'], body=check['message'])
                            messages.append(message)
                        send_mail(messages)
                        break

            custom_file.close()

    else:
        print("No new guests found...")

    print("Done. Total guests: %d.") % (total_count)


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
def notice(message=None):
    """Sets or remove a site-wide notice."""
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
