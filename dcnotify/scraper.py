#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
Provides information by screen-scraping the D*C website
'''
# member function false-positive
# pylint: disable=E1103
# Package namespace false-positive
# pylint: disable=W0403


from re import match
from robotparser import RobotFileParser

from requests import get
from bs4 import BeautifulSoup as bs


__author__ = "Sean Whalen"
__copyright__ = "Copyright (C) 2012 %s" % __author__
__license__ = "MIT"
__version__ = "1.2.0"

BASE_URL = "http://dragoncon.org"


def _get_soup(path):
    """Gets soup from the given path, respecting robots.txt"""
    user_agent = 'dcnotify/%s' % __version__
    http_headers = {'User-Agent': '%s' % user_agent}
    full_path = BASE_URL + path

    robots = RobotFileParser()
    robots.set_url("%s/robots.txt" % BASE_URL)
    robots.read()

    if not robots.can_fetch(user_agent, full_path):
        raise ValueError("Path disallowed by robots.txt")

    request = get(full_path, headers=http_headers)
    request.raise_for_status()

    return bs(request.text)


def get_guests():
    """ Returns a list of dictionaries containing guest data"""
    # regex false-positive
    # pylint: disable=W1401

    guest_path = "/?q=guests"
    guest_selector = "div.member-prof-pros p"

    soup = _get_soup(guest_path)

    for elem in soup.findAll(['script', 'style']):
        elem.extract()

    raw_guests = soup.select(guest_selector)

    guests = []

    for guest in raw_guests:
        name = unicode(guest.a.get_text())
        url = "%s/%s" % (BASE_URL, guest.a['href'])
        id_ = int(match(".*/(\d*)", url).group(1))
        guest.a.extract()
        description = guest.get_text().strip().lstrip(u"\xbb ")
        new_guest = dict(id=id_, name=name, url=url, description=description)

        guests.append(new_guest)

    return guests
