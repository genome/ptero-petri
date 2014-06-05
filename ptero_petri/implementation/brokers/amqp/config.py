from collections import namedtuple


EXCHANGE_NAME = 'ptero'
DEAD_EXCHANGE_NAME = 'ptero_dead'
ALT_EXCHANGE_NAME = 'ptero_alt'


BINDINGS = {
    'petri_create_token': 'petri.place.create_token',
    'petri_notify_place': 'petri.place.notify',
    'petri_notify_transition': 'petri.transition.notify',
}


ExchangeConfiguration = namedtuple('ExchangeConfiguration', [
    'name',
    'arguments',
])


QueueConfiguration = namedtuple('QueueConfiguration', [
    'queue_name',
    'arguments',
])


BindingConfiguration = namedtuple('BindingConfiguration', [
    'queue',
    'exchange',
    'topic',
])


def get_exchange_configurations():
    return [
        ExchangeConfiguration(name=ALT_EXCHANGE_NAME, arguments={}),
        ExchangeConfiguration(name=EXCHANGE_NAME,
            arguments={'alternate-exchange': ALT_EXCHANGE_NAME}),
        ExchangeConfiguration(name=DEAD_EXCHANGE_NAME,
            arguments={'alternate-exchange': ALT_EXCHANGE_NAME}),
    ]


def get_queue_configurations():
    results = []

    for queue_name in BINDINGS.iterkeys():
        results.append(QueueConfiguration(queue_name=queue_name,
                arguments={'x-dead-letter-exchange': DEAD_EXCHANGE_NAME}))
        results.append(QueueConfiguration(queue_name=_dead_name(queue_name),
                arguments={}))

    results.append(QueueConfiguration(queue_name='missing_routing_key',
        arguments={}))

    return results



def get_binding_configurations():
    results = []

    for queue, topic in BINDINGS.iteritems():
        results.append(BindingConfiguration(
            queue=queue,
            exchange=EXCHANGE_NAME,
            topic=topic,
        ))
        results.append(BindingConfiguration(
            queue=_dead_name(queue),
            exchange=DEAD_EXCHANGE_NAME,
            topic=topic,
        ))

    results.append(BindingConfiguration(
        queue='missing_routing_key',
        exchange=ALT_EXCHANGE_NAME,
        topic='#',
    ))

    return results


def _dead_name(queue_name):
    return 'dead_' + queue_name
