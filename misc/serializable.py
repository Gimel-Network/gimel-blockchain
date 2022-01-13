class Serializable:

    @classmethod
    def _from_serializer(cls, raw):
        raise NotImplementedError()

    def _to_serializer(self):
        raise NotImplementedError()

    @classmethod
    def loads(cls, raw, serializer, **kwargs):
        return cls._from_serializer(serializer.loads(raw, **kwargs))

    def dumps(self, serializer, **kwargs):
        return serializer.dumps(self._to_serializer(), **kwargs)
