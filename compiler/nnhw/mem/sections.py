class MetaSection(type):
    def __call__(self, *args, **kwds):
        obj = super().__call__(*args, **kwds)
        obj.structure_change()
        return obj

class SectionNone:
    pass

class Section:
    def __init__(self, name, size=0, stride=0):
        self.name = name
        self.size = size
        self.stride = stride

    def __str__(self):
        return f"{self.name}(size={self.size}, stride={self.stride})"

    def __repr__(self):
        return str(self)

class Sections:
    def __init__(self, *args, **kwargs):
        self.sections = {}
        for arg in args:
            if isinstance(arg, tuple):
                name, size, stride = arg
                self.sections[name] = Section(name, size, stride)
            elif isinstance(arg, str):
                self.sections[arg] = Section(arg)

    def __getitem__(self, key):
        return self.sections[key]

    def __setitem__(self, key, value):
        if isinstance(value, Section):
            self.sections[key] = value
        elif isinstance(value, dict):
            self.sections[key] = Section(key, **value)

    def __str__(self):
        return str(self.sections)

    def __repr__(self):
        return str(self) 