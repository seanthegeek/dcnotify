#-*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, TextAreaField, RecaptchaField, \
Required, Email, Length
from flask.ext.wtf.html5 import EmailField

# pylint: disable=W0232
# pylint: disable=R0903

class SubscriptionForm(Form):
    """Subscription form"""
    email = EmailField(label="Email address",
                       validators=[Length(min=6, max=120), Email()])


class ContactForm(Form):
    """Contact form"""
    name = TextField(label="Name", validators=[Length(max=35), Required()])
    email = EmailField(label="Email address",
                       validators=[Length(min=6, max=120), Email()])
    message = TextAreaField(label="Message",
                            validators=[Length(max=1000), Required()])
    recaptcha = RecaptchaField(label="reCAPTCHA")
