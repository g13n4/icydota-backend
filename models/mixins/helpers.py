def inherit_annotations(klass: object):
    for subklass in klass.__bases__:
        try:
            subklass.__mixin__
        except AttributeError:
            continue

        klass.__annotations__.update(subklass.__annotations__)
    return klass
