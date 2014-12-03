from ptero_petri.implementation.petri.future import FutureAction
from ptero_petri.implementation.translator import Translator
from unittest import TestCase, main


class TestTranslator(TestCase):

    def test_null_net(self):
        net_data = {}
        translator = Translator(net_data)
        future_net = translator.future_net
        self.assertEqual(0, len(future_net.places))
        self.assertEqual(0, len(future_net.subnets))
        self.assertEqual(0, len(future_net.transitions))

    def test_null_transition(self):
        net_data = {
            'entry_places': set(),
            'transitions': [{}]
        }
        translator = Translator(net_data)
        future_net = translator.future_net
        self.assertEqual(0, len(future_net.places))
        self.assertEqual(0, len(future_net.subnets))
        self.assertEqual(1, len(future_net.transitions))
        t = future_net.transitions.pop()
        self.assertIsNone(t.action)

    def test_simple_transition(self):
        net_data = {
            'entry_places': {'start'},
            'transitions': [{
                'inputs': ['start'],
                'outputs': ['stop'],
            }]
        }
        translator = Translator(net_data)
        future_net = translator.future_net
        self.assertEqual(2, len(future_net.places))
        self.assertEqual(0, len(future_net.subnets))
        self.assertEqual(1, len(future_net.transitions))
        t = future_net.transitions.pop()
        self.assertIsNone(t.action)
        self.assertEqual('start', get_unique_arc_in(t).name)
        self.assertEqual('stop', get_unique_arc_out(t).name)
        self.assertTrue(get_unique_arc_in(t).has_lookup)
        self.assertFalse(get_unique_arc_out(t).has_lookup)

    def test_transition_action(self):
        test_url = 'foobar'
        net_data = {
            'entry_places': set(),
            'transitions': [{
                'action': {
                    'type': 'notify',
                    'url': test_url,
                },
            }]
        }
        translator = Translator(net_data)
        future_net = translator.future_net
        self.assertEqual(0, len(future_net.places))
        self.assertEqual(0, len(future_net.subnets))
        self.assertEqual(1, len(future_net.transitions))

        t = future_net.transitions.pop()
        self.assertIsInstance(t.action, FutureAction)
        self.assertEqual(test_url, t.action.args['url'])


def get_unique_arc_out(source):
    return list(source.arcs_out)[0]


def get_unique_arc_in(source):
    return list(source.arcs_in)[0]


if __name__ == "__main__":
    main()
