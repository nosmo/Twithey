#!/usr/bin/env python

import os
import sys

import BeautifulSoup
import twithey

DEFAULT_OUTPUT_ENCODING = "utf-8"

username = ""
password = ""

class TimeLine:

    tweets = []

    def insertTweet(self, tweet):
        self.tweets.append(tweet)

    def __str__(self, encoding=DEFAULT_OUTPUT_ENCODING):
        s = ""
        for i in self.tweets:
            s += str(i) + "\n\n"
        return s

class User:

    userid=0
    name=""
    screen_name=""
    location=""
    description=""
    url=""

    def __init__(self, userid, aname, screen_name, location="", description="", url=""):
        self.userid = userid
        self.name = aname
        self.screen_name = screen_name
        self.location = location
        self.description = description
        self.url = url
    
class Tweet:

    user = None
    date = ""
    tweetid = 0
    message = ""

    def __init__(self, user, date, tweetid, message):
        self.user = user
        self.date = date
        self.tweetid = tweetid
        self.message = message


    def __str__(self, encoding=DEFAULT_OUTPUT_ENCODING):
        """Make the Tweets actually look like hey messages.

        I know it's stupid, you don't have to tell me
        """

        global username
        
        header = """Message from %s at %s
%s sez:
Tweet! %s

""" % (self.user.screen_name, self.date,
                        self.user.name, username)

        footer = "\n\nEOF"

        termwidth = 80
        leftpadding = 8
        messagepoint = 0
        messagestr = " "*leftpadding
        bits = self.message.split()
        lines = []

        for i in bits:
            messagepoint += len(i)
            if messagepoint > 80:
                lines.append(messagestr)
                messagestr = " "*leftpadding + i + " "
                messagepoint = len(i)
            else:
                messagestr += i + " "
        lines.append(messagestr)

        return header + "\n".join(lines) + footer

def parseTimeline():

    timeline = TimeLine()

    f = open(os.path.expanduser("~") + "/.twithey/timeline.xml", "r")
    data = f.read()
    soup = BeautifulSoup.BeautifulStoneSoup(data)
    statuses = soup.findAll("status")
    for i in statuses:
        date = i.created_at.string
        msgid = i.id.string
        message = i.text.string

        user = i.find("user")
        
        thisuser = parseUser(user, i.user.find("name").string)
        thistweet = Tweet(thisuser, date, msgid, message)

        timeline.insertTweet(thistweet)

    print timeline

def parseUser(userdata, name):
    
    u = User(userdata.id.string,
             name,
             userdata.screen_name.string,
             userdata.location.string,
             userdata.description.string,
             userdata.url.string)

    return u

def main():

    global username
    global password

    (username, password, proto) = twithey.readConfig()

    if not username or not password:
        sys.stderr.write("Fill in the username and password variables you silly nonny\n")
        sys.exit(1)

    twithey.getTimeline(proto)
    parseTimeline()


if __name__ == "__main__":
    main()
