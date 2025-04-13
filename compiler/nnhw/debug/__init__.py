def log(*args, **kwargs):
    """Logging function that can be used for debugging."""
    value_only = kwargs.pop('value_only', False)
    if value_only:
        print(*args, **kwargs)
    else:
        print(f"[DEBUG]", *args, **kwargs) 