import injector
from .broker import BrokerConfiguration
from .redis_conf import RedisConfiguration
from .service_locator import ServiceLocatorConfiguration


INJECTOR = injector.Injector()


def initialize_injector():
    injector_modules = [
            BrokerConfiguration,
            RedisConfiguration,
            ServiceLocatorConfiguration,
    ]

    add_modules(INJECTOR, *injector_modules)

    return INJECTOR

def add_modules(inj, *modules):
    for module in modules:
        if isinstance(module, type):
            module = module()

        module(inj.binder)

def reset_injector():
    global INJECTOR
    INJECTOR = injector.Injector()
