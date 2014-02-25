# -*- coding: utf-8 -*-


def to_dict(get):
    """ 将request.GET中的查询数据转换为字典

    字典结构:
        key    字段名
        value  字段值(有多个值时，为列表)
    """
    from django.http import QueryDict
    assert isinstance(get, QueryDict)

    return {
        key: value if len(value) > 1 else value[0]
        for key, value in get.lists()
    }
