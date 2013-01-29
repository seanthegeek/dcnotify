#-*- coding: utf-8 -*-

from os import path, remove
from time import time
from datetime import datetime, timedelta

from pretty import date
from twitter import Twitter, OAuth

from dcnotify import app, db, mail, __version__
import dcnotify.models as models
from dcnotify.scraper import get_guests

module_directory = path.dirname(__file__)

def send_mail(messages):
    """Sends the list of email messages"""
    with mail.connect() as conn:
        for message in messages:
            # Remove excess whitespace from subject
            message.subject = " ".join(message.subject.split())
            # Add subject prefix
            message.subject = "%s %s" % (app.config['MAIL_PREFIX'],
            message.subject)

            conn.send(message)


def email_admin(subject, message):
    """Sends an email message to the site administrator"""
    send_mail([Message(recipients=[app.config['ADMIN_MAIL']],
                       subject=subject,
                       html=message)])


def email_subscribers(subject, body):
    """Sends an email to all active subscibers"""
    subscribers = models.Subscriber.get_all()
    messages = []
    for subscriber in subscribers:
        unsub_url = url = url_for('unsubscribe', email=subscriber.email,
                          uuid=subscriber.uuid, _external=True)
        html = render_template('emails/mailer.html',
                                subscriber=subscriber,
                                message=body,
                                unsub_url=unsub_url)
        message = Message(recipients=[subscriber.email],
                                     subject=subject,
                                     html=html)
        messages.append(message)

    send_mail(messages)


def post_tweet(status):
    """Sends a tweet"""
    twit = Twitter(auth=OAuth(app.config['TWITTER_OAUTH_TOKEN'],
                              app.config['TWITTER_OAUTH_SECRET'],
                              app.config['TWITTER_CONSUMER_KEY'],
                              app.config['TWITTER_CONSUMER_SECRET']))

    twit.statuses.update(status=status)


def set_notice(notice=None):
    """Sets a site-wide notice"""
    full_path_to_file = path.join(module_directory, "notice.txt")
    if notice is None:
        if path.exists(full_path_to_file):
            remove(full_path_to_file)
    else:
        notice_file = open(full_path_to_file, "w")
        notice_file.writelines(notice)
        notice_file.close()


def get_notice():
    """Gets the site-wide notice"""
    full_path_to_file = path.join(module_directory, "notice.txt")
    if path.exists(full_path_to_file):
        notice_file = open(full_path_to_file, "r")
        notice = notice_file.read()
        notice_file.close()
        return notice
    else:
        return None


def get_status():
    """Returns a dictionary containing site status information"""
    notice = get_notice()
    guests = models.Guest.count()
    subscribers = models.Subscriber.count()
    full_path_to_file = path.join(module_directory, "updated.txt")
    updated_file = open(full_path_to_file, "r")
    timestamp = datetime.fromtimestamp(float(updated_file.readline()))
    updated_file.close()
    updated = date(timestamp)

    return dict(notice=notice,
                version=__version__,
                updated=updated,
                guests=guests,
                subscribers=subscribers)

def _purge_subscribers():
    """Purges inactive subscribers from the database"""
    subscribers = models.Subscriber.get_all(active=False)
    for subscriber in subscribers:
        expires = subscriber.timestamp + timedelta(hours=24)
        if datetime.utcnow() > expires:
            subscriber.remove()


def _update_guests():
    """Processes the D*C guest list"""
    year = str(app.config['DC_YEAR'])
    existing_count = 0
    print("Getting guest list...")
    guests = get_guests()
    new_guests = []

    print("Updating guests...")
    for guest in guests:
        record = models.Guest.get(guest['id'])
        if record is None:
            new_guests.append(guest)
            guest = models.Guest(guest['id'], guest['name'], guest['description'])
            db.session.add(guest)
        else:
            existing_count += 1
            record.name = guest['name']
            record.url = guest['url']
            record.description = guest['description']

        db.session.commit()

    full_path_to_file = path.join(module_directory, "updated.txt")
    updated_file = open(full_path_to_file, "w")
    updated_file.write(unicode(time()))
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
