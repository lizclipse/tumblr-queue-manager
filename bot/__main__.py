#!/usr/bin/env python
import json
from dotenv import dotenv_values
from pytumblr2 import TumblrRestClient

config = dotenv_values()
client = TumblrRestClient(
    consumer_key=config['CONSUMER_KEY'],
    consumer_secret=config['CONSUMER_SECRET'],
    oauth_token=config['TOKEN'],
    oauth_secret=config['TOKEN_SECRET']
)

blog = config['BLOG']
queue_tag = config['QUEUE_TAG']


class PageIter:
    def __init__(self, page):
        self.page = page
        self.posts = []
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.posts) == 0:
            self.posts = self.page(self.offset)
            self.offset = self.offset + len(self.posts)

        try:
            return self.posts.pop(0)
        except IndexError:
            raise StopIteration


fields = [
    'content',
    'layout',
    'state',
    'publish_on',
    'date',
    # 'tags', # manual
    'source_url',
    'send_to_twitter',
    'is_private',
    'slug',
    'interactability_reblog',
    'parent_tumblelog_uuid',
    'parent_post_id',
    'reblog_key',
    'hide_trail',
    'exclude_trail_items',
]

edited = 0
for post in PageIter(lambda offset: client.queue(blog, offset=offset)['posts']):
    if post['queued_state'] != 'queued':
        continue

    tags: list = post['tags']
    if queue_tag in tags:
        continue

    content: dict = client.get_single_post(blog, post['id'])

    update = {}
    for field in fields:
        if field in content:
            update[field] = content[field]

    tags.append(queue_tag)
    update['tags'] = tags

    client.edit_post(blog, content['id'], **update)
    edited += 1

print("edited {} posts".format(edited))
