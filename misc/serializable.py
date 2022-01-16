class Serializable:

    @classmethod
    def from_serializer(cls, raw):
        raise NotImplementedError()

    def to_serializer(self):
        raise NotImplementedError()

    @classmethod
    def loads(cls, raw, serializer, **kwargs):
        return cls.from_serializer(serializer.loads(raw, **kwargs))

    def dumps(self, serializer, **kwargs):
        return serializer.dumps(self.to_serializer(), **kwargs)
