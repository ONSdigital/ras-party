import functools


def filter_dict(d, cb):
    """
    Filter a dictionary based on passed function.

    :param d: The dictionary to be filtered
    :param cb: A function which is called back for each k, v pair of the dictionary. Should return Truthy or Falsey
    :return: The filtered dictionary (new instance)
    """

    return {k: v for k, v in d.items() if cb(k, v)}


filter_falsey_values = functools.partial(filter_dict, cb=lambda _, v: v)


def model_to_dict(model, exclude=None):
    """
    Extract a SQLAlchemy model instance to a dictionary
    :param model: the model to be extracted
    :param exclude: Any keys to be excluded
    :return: New dictionary consisting of property-values
    """
    exclude = exclude or []
    exclude.append('_sa_instance_state')
    return {k: v for k, v in model.__dict__.items() if k not in exclude}


def partition_dict(d, in_left):

    left = {}
    right = {}

    for k, v in d.items():
        if k in in_left:
            left[k] = v
        else:
            right[k] = v

    return left, right


def flatten_keys(d, prefix=None):

    prefix = prefix or ''
    result = []

    for k, v in d.items():
        result.append('.'.join([prefix, k] if prefix else [k]))
        if isinstance(v, dict):
            result.extend(flatten_keys(v, prefix='.'.join([prefix, k] if prefix else [k])))

    return result


def build_url(template, config, *args):
    url = template.format(config['scheme'], config['host'], config['port'], *args)
    return url


def obfuscate_email(email):
    """Takes an email address and returns an obfuscated version of it.
    For example: test@example.com would turn into t**t@e*********m
    """
    m = email.split('@')
    prefix = f'{m[0][0]}{"*"*(len(m[0])-2)}{m[0][-1]}'
    domain = f'{m[1][0]}{"*"*(len(m[1])-2)}{m[1][-1]}'
    return f'{prefix}@{domain}'
