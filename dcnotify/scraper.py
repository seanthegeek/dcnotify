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
__version__ = "1.3.0"

BASE_URL = "http://dragoncon.org"


def _get_soup(path):
    """Gets soup from the given path, respecting robots.txt"""

    full_path = BASE_URL + path

    # Set a user-agent
    user_agent = 'dcnotify/%s' % __version__
    http_headers = {'User-Agent': '%s' % user_agent}

    # Honor robots.txt
    robots = RobotFileParser()
    robots.set_url("%s/robots.txt" % BASE_URL)
    robots.read()
    if not robots.can_fetch(user_agent, full_path):
        raise ValueError("Path disallowed by robots.txt")

    # Make a make a request, raising any HTTP errors that might occur
    request = get(full_path, headers=http_headers)
    request.raise_for_status()

    return bs(request.text)


def get_guests():
    """ Returns a list of dictionaries containing guest data"""

    # The path to the guest list
    guest_path = "/?q=guests"
    
    # A CSS-style selector for guest listings
    guest_selector = "div.member-prof-pros p"

    # Get the page content
    soup = _get_soup(guest_path)

    # Remove all script and style elements
    for elem in soup.findAll(['script', 'style']):
        elem.extract()

    # Find all the guest listings
    raw_guests = soup.select(guest_selector)

    guests = []

    # Parse the guest listings
    for guest in raw_guests:
        if len(guest.text) > 0:
    	    name = unicode(guest.a.get_text())
            url = "%s/%s" % (BASE_URL, guest.a['href'])
            id_ = int(match(r".*/(\d*)", url).group(1)) # Use existing PK
            guest.a.extract() # Remove the name, leaving only the description
            description = guest.get_text().strip().lstrip(u"\xbb ") # Remove extra chars
            new_guest = dict(id=id_, name=name, url=url, description=description)
            guests.append(new_guest)

    return guests
