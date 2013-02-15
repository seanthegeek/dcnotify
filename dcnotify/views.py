#-*- coding: utf-8 -*-
"""
View functions
"""

# pylint false positives
# pylint: disable=E1101
# pylint: disable=E0602
# pylint: disable=C0103
# pylint: disable=E0012

from flask import render_template, url_for, flash, abort
from flask_mail import Message

from dcnotify import app, db
import dcnotify.models as models
import dcnotify.forms as forms
import dcnotify.controllers as controllers


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the %s field - %s" % (
                getattr(form, field).label.text, error), 'error')


@app.context_processor
def inject_status():
    """Injects status info into templates"""
    return controllers.get_status()


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


@app.route("/", methods=("GET", "POST"))
def index():
    """Index view"""
    form = forms.SubscriptionForm()
    desc = """Provides notifications when new Dragon*Con guests are announced.
Not affiliated with or endorsed by Dragon*Con or DCI, Inc."""
    if form.validate_on_submit():
        send_message = False
        email = form.email.data
        subscriber = models.Subscriber.get(email)
        if subscriber:
            if subscriber.active is False:
                send_message = True
                flash("Another activation message has been sent.", "success")
            else:
                flash("Your subscription is already active.")
        else:
            subscriber = models.Subscriber(form.email.data)
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
            controllers.send_mail([Message(recipients=[subscriber.email],
                                   subject="Subscription activation",
                                   html=html)])
    else:
        flash_errors(form)
    return render_template("index.html",
                           form=form, description=desc)


@app.route("/about/")
def about():
    """About view"""
    return render_template("about.html")


@app.route("/contact/", methods=("GET", "POST"))
def contact():
    """Contact view"""
    form = forms.ContactForm()
    if form.validate_on_submit():
        sender = (form.name.data, form.email.data)
        subject = "Message from %s" % form.name.data
        message = form.message.data
        body = render_template('emails/contact.html', sender=sender,
                               message=message)
        controllers.email_admin(subject, body)
        flash("Your message has been sent.", "success")
    else:
        flash_errors(form)

    return render_template("contact.html",
                           form=form)


@app.route("/activate/<email>/<uuid>/")
def activate_subscription(email, uuid):
    """Activates a subscription"""
    subscriber = models.Subscriber.get(email)
    if subscriber:
        if uuid == subscriber.uuid:
            if not subscriber.active:
                subscriber.activate()
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
    subscriber = models.Subscriber.get(email)
    if subscriber:
        if uuid == subscriber.uuid:
            subscriber.remove()
            flash("Your subscription has been removed.", "success")
            return index()
        else:
            abort(404)
    else:
        abort(404)
