from ... import interfaces


_SENTINEL = object()


class SettingsBase(interfaces.ISettings):
    def __getitem__(self, path):
        result = self.get(path, _SENTINEL)
        if result is _SENTINEL:
            raise KeyError('Could not find path (%s) in config' % path)
        return result
