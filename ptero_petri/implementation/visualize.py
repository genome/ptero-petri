import argparse
import simplejson
import sys


class DotVisualizer(object):
    def __init__(self, net_data):
        self.net_data = net_data

    def dot(self):
        return self._join_lines(
            self._graph_header,
            self._get_place_lines(),
            self._format_entry_points(),
            self._get_transition_lines(),
            self._get_arc_lines(),
            self._graph_footer,
        )

    @property
    def _graph_header(self):
        return ['digraph "petri-net" {']

    @property
    def _graph_footer(self):
        return ['}']

    def _join_lines(self, *args):
        lines = []
        for group in args:
            lines.extend(group)
            lines.append('')
        return '\n'.join(lines)

    def _get_place_lines(self):
        result = ['{', 'node [shape=oval]']
        result.extend(self._get_places())
        result.append('}')

        return result

    def _get_places(self):
        result = set()
        for transition_dict in self.net_data.get('transitions', []):
            for name in ['inputs', 'outputs']:
                result.update(set(transition_dict.get(name, [])))
        return [_quote(p) for p in result]

    def _format_entry_points(self):
        result = ['{', 'rank=source']
        result.extend([_quote(ep)
            for ep in self.net_data.get('entry_places', [])])
        result.append('}')
        return result

    def _get_transition_lines(self):
        result = [
            '{',
            'node [%s]' % ' '.join([
                'label=""',
                'shape=rectangle',
                'style=filled',
                'height=0.1',
            ]),
        ]
        result.extend(self._get_transitions())
        result.append('}')
        return result

    def _get_transitions(self):
        return [self._get_transition_line(i, t)
                for i, t in enumerate(self.net_data.get('transitions', []))]

    def _get_transition_line(self, i, t):
        return '%s [color=%s]' % (
                self._transition_name(i), self._get_transition_color(t))

    _ACTION_COLOR_MAP = {
        'convert-to-parent-color': 'green',
        'create-color-group': 'red',
        'join': 'red',
        'notify': 'blue',
        'split': 'red',
    }
    def _get_transition_color(self, t):
        return self._ACTION_COLOR_MAP.get(
                t.get('action', {}).get('type'), 'black')


    def _get_arc_lines(self):
        arcs = []
        for i, transition_dict in enumerate(
                self.net_data.get('transitions', [])):
            arcs.extend(self._arcs_for_transition(i, transition_dict))
        return arcs

    def _arcs_for_transition(self, index, transition_dict):
        t_name = self._transition_name(index)

        arcs = []
        for i in transition_dict.get('inputs', []):
            arcs.append(self._format_arc(i, t_name))

        for o in transition_dict.get('outputs', []):
            arcs.append(self._format_arc(t_name, o))

        return arcs

    def _transition_name(self, index):
        return 't_%d' % index

    def _format_arc(self, f, t):
        return '%s -> %s' % (_quote(f), _quote(t))

def _quote(str):
    return '"%s"' % str

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', '-i', help='Input (default=STDIN)')
    parser.add_argument('--output', '-o', help='Output (default=STDOUT)')

    return parser.parse_args()


def main():
    args = parse_args()

    with _open_file(args.input, sys.stdin, 'r') as infile:
        net_data = simplejson.load(infile)

    v = DotVisualizer(net_data)
    dot_output = v.dot()

    with _open_file(args.output, sys.stdout, 'w') as outfile:
        outfile.write(dot_output)


def _open_file(name, default, *args):
    if name is not None:
        return open(name, *args)
    else:
        return default


if __name__ == '__main__':
    main()
