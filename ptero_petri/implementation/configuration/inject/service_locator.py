from ... import interfaces
from ...service_locator import ServiceLocator
import injector


class ServiceLocatorConfiguration(injector.Module):
    def configure(self, binder):
        binder.bind(interfaces.IServiceLocator, ServiceLocator)
