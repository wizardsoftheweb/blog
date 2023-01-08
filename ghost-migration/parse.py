#!/usr/bin/env python

import json
import jinja2

with open('scratch.json', 'r') as file:
    data = json.load(file)

posts = dict()
for post_object in data['db'][0]['data']['posts']:
    post = dict()
    post['title'] = post_object['title']
    post['slug'] = post_object['slug']
    post['published'] = post_object['published_at']
    post['image'] = str(post_object.get(
        'feature_image', '')).replace('/content', '')
    post['tags'] = list()
    post['meta_description'] = ''
    mobiledoc = json.loads(post_object['mobiledoc'])
    post['markdown'] = mobiledoc['cards'][0][1]['markdown']
    posts[post_object['id']] = post

tags = dict()
for tag_object in data['db'][0]['data']['tags']:
    tags[tag_object['id']] = tag_object['name']

posts_tags = dict()
for post_tag in data['db'][0]['data']['posts_tags']:
    post_id = post_tag['post_id']
    tag_id = post_tag['tag_id']
    if post_id in posts_tags:
        posts_tags[post_id][post_tag['sort_order']] = tags[tag_id]
    else:
        posts_tags[post_id] = dict()
        posts_tags[post_id][post_tag['sort_order']] = tags[tag_id]

for post_id in posts_tags:
    sorted(posts_tags[post_id].items())
    posts[post_id]['tags'] = list(posts_tags[post_id].values())

for post_meta in data['db'][0]['data']['posts_meta']:
    post_id = post_meta['post_id']
    posts[post_id]['meta_description'] = post_meta['meta_description']

templateLoader = jinja2.FileSystemLoader(searchpath='.')
templateEnv = jinja2.Environment(loader=templateLoader)

TEMPLATE_FILE = './post.jinja'
template = templateEnv.get_template(TEMPLATE_FILE)

for post_id in posts:
    post = posts[post_id]
    outputText = template.render(post)
    with open('./parsed/' + post['slug'] + '.md', 'w') as file:
        file.write(outputText)
