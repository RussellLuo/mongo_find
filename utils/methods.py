# -*- coding: utf-8 -*-


def match_num(field, value):
    """ 用于匹配数字的查询条件
    """
    if isinstance(value, list):
        return {field: {'$in': value}}
    else:
        return {field: value}


def match_str(field, value):
    """ 用于匹配字符串的查询条件
    """
    if isinstance(value, list):
        return {field: {'$in': value}}
    else:
        return {field: value}
