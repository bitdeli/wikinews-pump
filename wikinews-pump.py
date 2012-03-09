import feedparser
import traceback
import json
import time
import os

from urllib import urlopen
from BeautifulSoup import BeautifulSoup

MINUTE = 60

BITDELI_URL = "https://in.bitdeli.com/events/i-04baaf737e91e4-799c3b50"
BITDELI_AUTH = os.environ['BITDELI_AUTH']
RSS_URL = 'http://en.wikinews.org/w/index.php?title=Special:NewsFeed&feed=atom&categories=Published&notcategories=No%20publish%7CArchived%7CAutoArchived%7Cdisputed&namespace=0&count=30&hourcount=124&ordermethod=categoryadd&stablepages=only'

def read_tstamp():
    try:
        return open('last-update').read()
    except:
        return ''

def write_tstamp(tstamp):
    f = open('last-update', 'w')
    f.write(tstamp)
    f.close()

def extract(root, filter):
    hits = root.find(True, filter)
    if hits:
        hits.extract()

def text_content(doc):
    extract(doc, {'class': 'published'})
    extract(doc, {'class': 'Z3988'})
    extract(doc, {'id': 'social_bookmarks'})
    extract(doc, {'id': 'commentrequest'})
    txt = ' '.join(' '.join(p.findAll(text=True)) for p in doc.findAll('p'))
    return txt.replace('  ', ' ').replace(' . ', '. ').replace(' , ', ', ').strip()

def process_article(entry):
    return {'updated': entry.updated,
            'title': entry.title,
            'link': entry.link,
            'summary': text_content(BeautifulSoup(entry.summary))}

def send_to_bitdeli(article):
    event = json.dumps({'auth': BITDELI_AUTH, 'object': article})
    print urlopen(BITDELI_URL, event).read()

def process_feed(latest):
    new_latest = latest
    for entry in feedparser.parse(RSS_URL).entries:
        if entry.updated > latest:
            try:
                article = process_article(entry)
                print 'sending', entry.updated, entry.title
                send_to_bitdeli(article)
                new_latest = max(new_latest, entry.updated)
            except:
                traceback.print_exc()
    return new_latest

def pump(latest):
    while True:
        try:
            latest = process_feed(latest)
            write_tstamp(latest)
        except:
            traceback.print_exc()
        time.sleep(5 * MINUTE)

if __name__ == '__main__':
    pump(read_tstamp())
