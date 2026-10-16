"""Physical copper geometry shared by the independent PCB audits."""
from collections import defaultdict
from shapely.affinity import rotate
from shapely.geometry import Point, LineString, Polygon, box
from shapely.strtree import STRtree

LAYERS = ['top', 'inner1', 'inner2', 'bottom']


def pad_shape(e):
    if e.get('shape') == 'polygon':
        return Polygon([(p['x'], p['y']) for p in e['points']]).buffer(0)
    x, y = e['x'], e['y']
    w = e.get('width', e.get('outer_diameter', e.get('radius', 0) * 2))
    h = e.get('height', w)
    if e.get('shape') == 'circle':
        result = Point(x, y).buffer(w / 2, quad_segs=32)
    elif e.get('shape') in ['pill', 'rotated_pill']:
        dx, dy = ((w - h) / 2, 0) if w >= h else (0, (h - w) / 2)
        result = LineString([(x-dx, y-dy), (x+dx, y+dy)]).buffer(min(w, h) / 2, quad_segs=32)
    else:
        result = box(x-w/2, y-h/2, x+w/2, y+h/2)
    return rotate(result, e.get('ccw_rotation', 0), origin=(x, y))


class Copper:
    def __init__(self, records):
        self.records = records
        self.source = {e['source_port_id']: e for e in records if e['type'] == 'source_port'}
        self.ports = {e['pcb_port_id']: e for e in records if e['type'] == 'pcb_port'}
        self.names = {e['source_component_id']: e['name'] for e in records if e['type'] == 'source_component'}
        self.nets = {e['subcircuit_connectivity_map_key']: e['name'] for e in records if e['type'] == 'source_net'}

    def key(self, record):
        if record['type'] == 'pcb_smtpad':
            return self.source[self.ports[record['pcb_port_id']]['source_port_id']].get('subcircuit_connectivity_map_key')
        return record.get('subcircuit_connectivity_map_key')

    def elements(self):
        result = []
        for e in self.records:
            typ = e['type']
            key = self.key(e) if typ in ['pcb_smtpad', 'pcb_trace', 'pcb_via', 'pcb_copper_pour'] else None
            if typ == 'pcb_smtpad':
                result.append((e, key, {e['layer']: pad_shape(e)}))
            elif typ == 'pcb_via':
                ring = Point(e['x'], e['y']).buffer(e['outer_diameter']/2, quad_segs=32).difference(
                    Point(e['x'], e['y']).buffer(e['hole_diameter']/2, quad_segs=32))
                result.append((e, key, {layer: ring for layer in e['layers']}))
            elif typ == 'pcb_trace':
                for a, b in zip(e['route'], e['route'][1:]):
                    if a['route_type'] == b['route_type'] == 'wire' and a['layer'] == b['layer']:
                        if abs(a['width'] - b['width']) > 1e-8:
                            raise ValueError('Variable-width segment needs explicit CAM treatment: ' + e['pcb_trace_id'])
                        shape = LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(a['width']/2, quad_segs=32)
                        result.append(({**e, 'route': [a, b]}, key, {a['layer']: shape}))
            elif typ == 'pcb_copper_pour':
                brep = e['brep_shape']
                points = lambda r: [(p['x'], p['y']) for p in r['vertices']]
                shape = Polygon(points(brep['outer_ring']), [points(r) for r in brep.get('inner_rings', [])])
                result.append((e, key, {e['layer']: shape}))
        return result

    def groups(self, net):
        elements = [e for e in self.elements() if e[1] == net]
        parent = list(range(len(elements)))

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for layer in LAYERS:
            shapes, owners = [], []
            for i, (_, _, geometry) in enumerate(elements):
                if layer in geometry:
                    shapes.append(geometry[layer]); owners.append(i)
            tree = STRtree(shapes)
            for i, shape in enumerate(shapes):
                for other in tree.query(shape, predicate='intersects'):
                    a, b = root(owners[i]), root(owners[other])
                    if a != b:
                        parent[b] = a
        return elements, [root(i) for i in range(len(elements))]

    def connectivity(self):
        errors = []
        for key, name in self.nets.items():
            elements, roots = self.groups(key)
            islands = defaultdict(set)
            for (record, _, _), group in zip(elements, roots):
                if record['type'] == 'pcb_smtpad':
                    port = self.source[self.ports[record['pcb_port_id']]['source_port_id']]
                    islands[group].add(f"{self.names[port['source_component_id']]}.{port['pin_number']}")
            if len(islands) > 1:
                errors.append({'net': name, 'islands': [sorted(v) for v in islands.values()]})
        return errors
