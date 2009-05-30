#!/usr/bin/env python

import base64
import ConfigParser
import os
import sys
import urllib
import urllib2

username = ""
password = ""
proto = ""

"""Twithey poster/getter.

 These functions are used to post information to and get information
 from Twitter. They're short and equal parts bitter and sweet.

  getPage: Request a page using the user's details.
  getTimeline(): Get the user's timeline
  Post(): Post a public status message
  directMessage(): Direct message a user
"""

__author__ = "nosmo@netsoc.tcd.ie"

def readConfig(path=os.path.expanduser("~") + "/.twithey/twitheyrc"):
    """Reads configuration information from the twitheyrc file.

     path: an optional string pointing to the config file a user wishes to use
    """

    global username
    global password
    global proto

    config = ConfigParser.ConfigParser()
    config.read(path)

    if not (config.has_option("account", "user") and config.has_option("account", "pass")):
        sys.stderr.write("Config file has no username or password!")
        sys.exit(4)

    if config.get("connection", "https") == "yes":
        proto = "https"
    else:
        proto = "http"

    username = config.get("account", "user")
    password = config.get("account", "pass")

    return (username, password, proto)


def getPage(url, data=None):
    """Encode the user's login details and request a page.

     url: a string containing the URL to be fetched
     data: optional urlencode'd data dictionary
    """
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    if data:
        data = data + "&" + urllib.urlencode({"source": "twithey"})
    # This breaks the timeline - I have no idea why but it isn't of much use
    #else:
    #    data =  urllib.urlencode({"source": "twithey"})
    req = urllib2.Request(url, data)
    req.add_header("Authorization", "Basic %s" % base64string)
    try:
        results = urllib2.build_opener().open(req).read()
    except IOError, e:
        print e.headers
        sys.stderr.write("Uh oh, something screwed up when getting page!\n")
        sys.exit(3)

    return results

def getTimeline(proto=None):
    """Get the user's timeline."""
    
    theurl = '%s://twitter.com/statuses/friends_timeline.xml' % proto
    results = getPage(theurl)
    timeline = open(os.path.expanduser("~") + "/.twithey/timeline.xml", "w")
    timeline.write(results)
    timeline.close()

def chkLength(message):
    length = 0
    for i in message:
        if i == "<" or i == ">":
            length += 4
        else:
            length += 1
    if length > 140:
        return False
    return True

def Post():
    """Make a public status update."""
    
    print "[ recipients : <Twitter> ]"

    postdata = raw_input()

    if not chkLength(postdata):
        sys.stderr.write("Post too long!")
        sys.exit(2)
    
    data = urllib.urlencode({'status' : postdata})
    theurl = '%s://twitter.com/statuses/update.xml' % proto
    if getPage(theurl, data):
        print "[ tweet--okay. ]"
    else:
        print "Something went wrong along the way :("

def directMessage(user):
    """Direct message a user.

     user: a username
    """
    
    print "[ recipients : %s ]" % user
    postdata = raw_input()

    if not chkLength(postdata):
        sys.stderr.write("Post too long!")
        sys.exit(2)

    data = urllib.urlencode({'user' : user, 'text' : postdata})
    
    theurl = '%s://twitter.com/direct_messages/new.xml' % proto
    if getPage(theurl, data):
        print "[ tweet %s--okay. ]" % user
    else:
        print "Something went wrong along the way :("

if __name__ == "__main__":
    """Yes, I know this is very basic."""

    readConfig()

    if not username or not password:
        sys.stderr.write("Fill in the username and password variables you silly nonny\n")
        sys.exit(1)
        
    if len(sys.argv) > 1:
        directMessage(sys.argv[1])
    else: 
        Post()
