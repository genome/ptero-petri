from ... import interfaces
import injector


class InjectedSettings(injector.Module):
    def __init__(self, settings):
        self.settings = settings
        injector.Module.__init__(self)

    @injector.singleton
    @injector.provides(interfaces.ISettings)
    def provide_settings(self):
        return self.settings
