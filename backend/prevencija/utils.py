def get_or_none(klass, *args, **kwargs):
    try:
        return klass.get(*args, **kwargs)
    except klass.model.DoesNotExist:
        return None


