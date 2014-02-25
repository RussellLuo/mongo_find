#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient

db = MongoClient().generic


def init():
    datas = [
        {
            'user': {
                'name': 'russell',
                'passwd': '123456'
            },
            'site': {
                'domain': 'www.me.com',
                'name': 'my_site',
                'industry': 'web',
                'pv': 1500
            }
        },
        {
            'user': {
                'name': 'tracey',
                'passwd': '123456'
            },
            'site': {
                'domain': 'www.you.com',
                'name': 'your_site',
                'industry': 'software',
                'pv': 1000
            }
        }
    ]

    for data in datas:
        save(data)


def save(data):
    user = data['user']
    site = data['site']

    _id = db.user.update({'name': user['name']}, {'$set': user}, upsert=True).get('upserted')
    if _id:
        site.update(user_id=_id)
        db.site.insert(site)


if __name__ == '__main__':
    init()
