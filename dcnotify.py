'''
The D*C Notifications application module
'''
# SQLAlchemy false positives
# pylint: disable=E1101
# pylint: disable=W0611
# pylint: disable=E0611
# pylint: disable=F0401


from logging import ERROR
from logging.handlers import SMTPHandler
from uuid import uuid4
from os import path, remove
from datetime import datetime

from flask import Flask, render_template, flash, abort, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from pretty import date
from flaskext.babel import Babel
from flask_mail import Mail, Message
from twitter import Twitter, OAuth
from flask.ext.wtf import Form, TextField, TextAreaField, RecaptchaField, \
Required, Email, Length
from flask.ext.wtf.html5 import EmailField


__author__ = "Sean Whalen"
__copyright__ = "Copyright (C) 2012 %s" % __author__
__license__ = "MIT"
__version__ = "0.2.0"

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


module_directory = path.dirname(__file__)


class Guest(db.Model):
    """The subscriber model"""
    # Ignore a lack of public methods
    # pylint: disable=R0903
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(512))

    def __init__(self, id_, url, name, description):
        self.id = id_
        self.url = url
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Guest %r>' % self.name


class Subscriber(db.Model):
    """The subscriber model"""
    # Ignore a lack of public methods
    # pylint: disable=R0903
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    uuid = db.Column(db.String(37))
    timestamp = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

    def __init__(self, email, active=False):
        self.email = email
        self.uuid = str(uuid4())
        self.timestamp = datetime.utcnow()
        self.active = active

    def __repr__(self):
        return '<Subscriber %r>' % self.email


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
    subscribers = Subscriber.query.filter_by(active=True).all()
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
    guests = Guest.query.count()
    subscribers = Subscriber.query.filter_by(active=True).count()
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


@app.context_processor
def inject_status():
    """Injects status info into templates"""
    return get_status()


@app.errorhandler(500)
def server_error(e):
    """Handles server errors"""
    # Ignore unused arguments
    # pylint: disable=W0613
    return render_template("errors/500.html")


@app.errorhandler(404)
def not_found_error(e):
    """HTTP 404 view"""
    # Ignore unused arguments
    # pylint: disable=W0613
    return render_template("errors/404.html"), 404


class SubscriptionForm(Form):
    """Subscription form"""
    # pylint: disable=W0232
    # pylint: disable=R0903
    email = EmailField(label="Email address",
                       validators=[Length(min=6, max=120), Email()])


class ContactForm(Form):
    """Contact form"""
    # pylint: disable=W0232
    # pylint: disable=R0903
    name = TextField(label="Name", validators=[Length(max=35), Required()])
    email = EmailField(label="Email address",
                       validators=[Length(min=6, max=120), Email()])
    message = TextAreaField(label="Message",
                            validators=[Length(max=1000), Required()])
    recaptcha = RecaptchaField(label="reCAPTCHA")


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error), 'error')


@app.route("/", methods=("GET", "POST"))
def index():
    """Index view"""
    form = SubscriptionForm()
    desc = """Provides notifications when new Dragon*Con guests are announced.
Not affiliated with or endorsed by Dragon*Con or DCI, Inc."""
    if form.validate_on_submit():
        send_message = False
        subscriber = Subscriber.query.filter_by(email=form.email.data).first()
        if subscriber:
            if  subscriber.active is False:
                send_message = True
                flash("Another activation message has been sent.", "success")
            else:
                flash("Your subscription is already active.")
        else:
            subscriber = Subscriber(form.email.data)
            db.session.add(subscriber)
            db.session.commit()
            send_message = True
            flash("Please check your email for an activation message.",
                  "success")
        if send_message:
            url = url_for('activate_subscription', email=subscriber.email,
                          uuid=subscriber.uuid, _external=True)
            html = render_template("emails/activate.html",
                                      url=url)
            send_mail([Message(recipients=[subscriber.email],
            subject="Subscription activation",
            html=html)])
    else:
            flash_errors(form)
    return render_template("index.html",
                           form=form, description=desc)


@app.route("/about/")
def about():
    """About view"""
    return render_template("about.html", status=get_status())


@app.route("/contact/", methods=("GET", "POST"))
def contact():
    """Contact view"""
    form = ContactForm()
    if form.validate_on_submit():
        sender = (form.name.data, form.email.data)
        subject = "Message from %s" % form.name.data
        message = form.message.data
        body = render_template('emails/contact.html', sender=sender,
                               message=message)
        email_admin(subject, body)
        flash("Your message has been sent.", "success")
    else:
        flash_errors(form)

    return render_template("contact.html",
                           form=form)


@app.route("/activate/<email>/<uuid>/")
def activate_subscription(email, uuid):
    """Activates a subscription"""
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        if uuid == subscriber.uuid:
            if not subscriber.active:
                subscriber.active = True
                db.session.commit()
                flash("Your subscription has been activated.", "success")
            else:
                flash("Your subscription is already active.")
        else:
            abort(404)

        return index()
    else:
        abort(404)


@app.route("/unsubscribe/<email>/<uuid>/")
def unsubscribe(email, uuid):
    """Removes a subscription"""
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        if uuid == subscriber.uuid:
            db.session.delete(subscriber)
            db.session.commit()
            flash("Your subscription has been removed.", "success")
            return index()
        else:
            abort(404)
    else:
        abort(404)


@app.route('/error/')
def error():
    """Exception test"""
    raise ValueError("Test")

if __name__ == "__main__":
    app.run()
