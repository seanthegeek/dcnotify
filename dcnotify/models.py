#-*- coding: utf-8 -*-
'''
Object models
'''
# SQLAlchemy false positives
# pylint: disable=E1101
# pylint: disable=W0611
# pylint: disable=E0611
# pylint: disable=F0401

from datetime import datetime
from uuid import uuid4

from dcnotify import db


class Guest(db.Model):
    """The subscriber model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(512))

    def __init__(self, id_, name, description):
        self.id = id_
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Guest %r>' % self.name

    @staticmethod
    def count():
        """Returns the guest count"""
        return Subscriber.query.count()
    
    @staticmethod
    def get(id_):
        """Returns a single guest"""
        return Guest.query.filter_by(id=id_).first()

    @staticmethod
    def get_all():
        """Returns all guests"""
        return Guest.query.all()

    def remove(self):
        """Removes the guest from the database"""
        db.session.delete(self)
        db.session.commit()


class Subscriber(db.Model):
    """The subscriber model"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    uuid = db.Column(db.String(37))
    timestamp = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

    def __init__(self, email, active=False):
        self.email = email.lower()
        self.uuid = str(uuid4())
        self.timestamp = datetime.utcnow()
        self.active = active

    def __repr__(self):
        return '<Subscriber %r>' % self.email

    @staticmethod
    def count(active=True):
        """Returns the subscriber count"""
        return Subscriber.query.filter_by(active=active).count()

    @staticmethod
    def get(email):
        """Returns a single subscriber"""
        return Subscriber.query.filter_by(email=email).first()

    @staticmethod
    def get_all(active=True):
        """Returns all subscribers"""
        return Subscriber.query.filter_by(active=active).all()

    def remove(self):
        """Removes the subscriber from the database"""
        db.session.delete(self)
        db.session.commit()

    def activate(self):
       """Activates the subscriber"""
       self.active = True
       db.commit()
