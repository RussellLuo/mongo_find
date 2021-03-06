# -*- coding: utf-8 -*-

from django.shortcuts import render

from utils.generic import mongo_find
from utils.convertor import to_dict
from .models import db


params = {
    'collection': db.site,
    'foreign_keys': {
        'user_id': {
            'collection': db.user,
            'match_key': '_id',
            'return_fields': [
                # 在查询后返回的文档中
                # 将集合user中的字段name合并到集合site中
                # 并将其重命名为user_name
                ('name', 'user_name'),
            ]
        }
    },
    'basic_args': {
        'spec': {
            #'name': 'my_site',
        },
        'sort': [
            #('pv', 1),
        ]
    },
    'fields_map': {
        'spec': [
            # 集合site中的字段name
            # --> (str匹配)
            # 查询数据中的字段site_name
            ('name', 'str', 'site_name'),
            # 集合site中的外键user_id的关联集合(user)中的字段name
            # --> (str匹配)
            # 查询数据中的字段user_name
            (('user_id', 'name'), 'str', 'user_name'),
        ],
        'sort': [
            # 集合site中的字段pv
            # --> (映射)
            # 查询数据中的字段pv
            ('pv', 'pv'),
        ]
    },
    'docs_per_page': 2
}


def show_sites(request, template):
    """ 显示网站列表
    """
    data = to_dict(request.GET)
    result = mongo_find(data, **params)
    return render(request, template, result)
