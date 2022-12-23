#!/usr/bin/env python3
#
# Simple Python bot to retrieve a RSS feed 
# and toot items
#
# Copyright (c) B Tasker, 2022
#
# Released under BSD 3 Clause
# See https://www.bentasker.co.uk/pages/licenses/bsd-3-clause.html
#
import feedparser
import hashlib
import os
import yaml
import requests
import time

def build_toot(entry):
    ''' Take the entry dict and build a toot
    '''
    # Initialise
    skip_tags = SKIP_TAGS + ["blog", "documentation", CW_TAG]
    toot_str = ''

    if "blog" in entry['tags']:
        toot_str += "New #Blog: "
    elif "documentation" in entry['tags']:
        toot_str += "New #Documentation: "

    toot_str += f"{entry['title']}\n"

    if entry['author']:
        toot_str += f"Author: {entry['author']}\n"

    toot_str += f"\n\n{entry['link']}\n\n"

    # Tags to hashtags
    if len(entry['tags']) > 0:
        for tag in entry['tags']:
            if tag in skip_tags:
                # Skip the tag
                continue
            toot_str += f'#{tag.replace(" ", "")} '

    return toot_str


def send_toot(en):
    ''' Turn the dict into toot text

    and send the toot
    '''
    toot_txt = build_toot(en)

    headers = {
        "Authorization" : f"Bearer {MASTODON_TOKEN}"
        }

    data = {
        'status': toot_txt,
        'visibility': MASTODON_VISIBILITY
        }

    if en['cw']:
        data['spoiler_text'] = en['title']

    if DRY_RUN == "Y":
        print("------")
        print(data['status'])
        print(data)
        print("------")
        return True

    try:
        resp = SESSION.post(
            f"{MASTODON_URL.strip('/')}/api/v1/statuses",
            data=data,
            headers=headers
        )

        if resp.status_code == 200:
            return True
        else:
            print(f"Failed to post {en['link']}")
            print(resp.status_code)
            return False
    except:
        print(f"Urg, exception {en['link']}")
        return False


def process_feed(feed):
    ''' Process the RSS feed and generate a toot for any entry we haven't yet seen
    '''
    if os.path.exists(feed['hash_file']):
        hashtracker = open(feed['hash_file'],'r+')
        storedhash = hashtracker.read()
    else:
        hashtracker = open(feed['hash_file'],'w')
        storedhash = ''

    # This will be overridden as we iterate through
    firsthash = False

    # Load the feed
    d = feedparser.parse(feed['uri'])

    # Iterate over entries
    for entry in d.entries:

        # compare a checksum of the URL to the stored one
        # this is used to prevent us re-sending old items
        linkhash = hashlib.sha256(entry.link.encode('utf-8')).hexdigest()

        if storedhash == linkhash:
            print("Reached last seen entry")
            break

        en = {}
        en['title'] = entry.title
        en['link'] = entry.link
        en['author'] = False       
        en['tags'] = feed['tags'] if 'tags' in feed else []

        if hasattr(entry, "tags"):
            # Iterate over tags and add them
            [en['tags'].append(x['term']) for x in entry.tags]

        en['cw'] = (CW_TAG in en['tags'] or feed['sensitive'])

        if INCLUDE_AUTHOR == "True" and hasattr(entry, "author"):
            en['author'] = entry.author

        # Keep a record of the hash for the first item in the feed
        if not firsthash:
            firsthash = linkhash

        # Send the toot
        if send_toot(en):
            # If that worked, write hash to disk to prevent re-sending
            hashtracker.seek(0)
            hashtracker.truncate()
            hashtracker.write(firsthash)

        time.sleep(1)
    hashtracker.close()

with open('/app/feeds.yaml', 'r') as fh:
    FEEDS = yaml.safe_load(fh)

HASH_DIR = os.getenv('HASH_DIR', '/hashdir')
INCLUDE_AUTHOR = os.getenv('INCLUDE_AUTHOR', "True")

# Posts with this tag will toot with a content warning
CW_TAG = os.getenv('CW_TAG', "content-warning")

MASTODON_URL = os.getenv('MASTODON_URL', "https://mastodon.social")
MASTODON_TOKEN = os.getenv('MASTODON_TOKEN', "")
MASTODON_VISIBILITY = os.getenv('MASTODON_VISIBILITY', 'public')
DRY_RUN = os.getenv('DRY_RUN', "N").upper()
SKIP_TAGS = os.getenv('SKIP_TAGS', "").lower().split(',')

# We want to be able to use keep-alive if we're posting multiple things
SESSION = requests.session()

for feed in FEEDS:
    feed_hash = hashlib.sha256(feed['uri'].encode('utf-8')).hexdigest()
    feed['hash_file'] = os.path.join(HASH_DIR, feed_hash)
    process_feed(feed)
