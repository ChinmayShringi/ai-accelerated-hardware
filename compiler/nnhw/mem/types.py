from typing import Any, Union, List, Tuple

class GetType:
    def __init__(self, type_str: str = 'default'):
        self.type_str = type_str

    def __call__(self, value: Any) -> Any:
        if self.type_str == 'default':
            return value
        elif self.type_str == 'list':
            return list(value) if isinstance(value, (list, tuple)) else [value]
        elif self.type_str == 'tuple':
            return tuple(value) if isinstance(value, (list, tuple)) else (value,)
        elif self.type_str == 'int':
            return int(value)
        elif self.type_str == 'float':
            return float(value)
        elif self.type_str == 'str':
            return str(value)
        return value 