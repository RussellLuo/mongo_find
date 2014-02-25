# -*- coding: utf-8 -*-


def mongo_find(data,
               collection, foreign_keys={},
               basic_args={}, fields_map={},
               spec_funcs=(), sort_funcs=(),
               docs_per_page=10):
    """ MongoDB通用查询接口(支持筛选, 排序, 分页)

    参数:
        data           查询数据
        collection     数据库集合名
        foreign_keys   `collection`中的外键
                       (collection: 关联集合, match_key: 匹配建, return_fields: 返回字段)
        basic_args     基本的条件参数
                       (spec: 筛选, sort: 排序)
        fields_map     从`collection`到`data`的字段映射表
                       (spec: 筛选, sort: 排序)
        spec_funcs     自定义的筛选函数列表
                       (每一个函数返回一种筛选条件)
        sort_funcs     自定义的排序函数列表
                       (每一个函数返回一种排序条件)
        docs_per_page  每页显示的文档数

    返回:
        documents      结果文档
        page           分页数据
                       (docs_amount: 文档总数, docs_per_page: 每页文档数, cur_page: 当前分页号)

    示例:
        see app `sites`
    """
    spec_basic_args = basic_args.get('spec', {})
    sort_basic_args = basic_args.get('sort', [])
    spec_fields_map = fields_map.get('spec', [])
    sort_fields_map = fields_map.get('sort', [])

    spec_condition = get_spec_condition(data, foreign_keys, spec_basic_args, spec_fields_map, spec_funcs)
    sort_condition = get_sort_condition(data, sort_basic_args, sort_fields_map, sort_funcs)
    cur_page = get_cur_page(data)

    find_condition = get_find_condition(spec_condition, sort_condition, cur_page, docs_per_page)
    documents = collection.find(**find_condition)

    documents_count = documents.count()
    documents = list(documents)

    merge_foreign_fields(documents, foreign_keys)

    return {
        'documents': documents,
        'page': {
            'docs_amount': documents_count,
            'docs_per_page': docs_per_page,
            'cur_page': cur_page
        }
    }


def get_spec_condition(data, foreign_keys, spec_basic_args, spec_fields_map, spec_funcs):
    """ 获取筛选条件
    """
    condition = spec_basic_args

    for field, match_type, data_field in spec_fields_map:
        value = data.get(data_field)
        if value is not None:
            if isinstance(field, basestring): # 普通字段
                normal = get_normal_spec_condition(field, value, match_type)
                condition.update(normal)
            elif isinstance(field, (tuple, list)) and len(field) == 2: # 外键字段
                foreign = get_foreign_spec_condition(foreign_keys, field, value, match_type)
                condition.update(foreign)

    for func in spec_funcs:
        condition.update(func(data, foreign_keys))

    return condition


def get_sort_condition(data, sort_basic_args, sort_fields_map, sort_funcs):
    """ 获取排序条件
    """
    condition = sort_basic_args

    for field, data_field in sort_fields_map:
        direction = data.get(data_field)
        if direction in ('1', '-1'):
            condition.append((field, int(direction)))

    # sort_funcs中的排序条件具有高优先级
    for func in reversed(sort_funcs):
        pair = func(data)
        if pair:
            condition.insert(0, pair)

    return condition


def get_cur_page(data):
    """ 获取当前分页数
    """
    try:
        page = int(data.get('page'))
    except Exception:
        page = 1

    return page if page > 0 else 1


def get_find_condition(spec_condition, sort_condition, cur_page, docs_per_page):
    """ 获取查询条件
    """
    condition = {
        'spec': spec_condition,
        'sort': sort_condition
    }

    if docs_per_page: # 需要分页
        condition.update({
            'skip': (cur_page-1) * docs_per_page,
            'limit': docs_per_page
        })

    return condition


def merge_foreign_fields(documents, foreign_keys):
    """ 合并关联集合中的字段
    """
    for document in documents:
        for key, value in foreign_keys.items():
            collection = value['collection']
            match_key = value['match_key']

            foreign_documents = collection.find({match_key: document[key]})

            if foreign_documents.count() == 0:
                raise Exception('`%s` (%s) does not match any document in collection '
                                '`%s`' % (match_key, document[key], collection.name))

            if foreign_documents.count() > 1:
                raise Exception('`%s` (%s) matches more than one document in collection '
                                '`%s`' % (match_key, document[key], collection.name))

            for field, alias in value['return_fields']:
                if alias in document:
                    raise Exception('alias "%s" in `foreign_keys->%s->return_fields` '
                                    'already exists' % (alias, key))
                document[alias] = foreign_documents[0][field]


def get_normal_spec_condition(field, value, match_type):
    """ 获取普通字段的筛选条件
    """
    import methods

    return getattr(methods, 'match_'+match_type)(field, value)


def get_foreign_spec_condition(foreign_keys, field, value, match_type):
    """ 获取外键字段的筛选条件
    """
    the_key, the_field = field
    foreign_data = foreign_keys[the_key]

    collection = foreign_data['collection']
    match_key = foreign_data['match_key']

    condition = get_normal_spec_condition(the_field, value, match_type)
    the_values = [document[match_key] for document in collection.find(condition)]

    # 目前只支持对外键做范围筛选（即$in查询）
    return {the_key: {'$in': the_values}} if the_values else {}
