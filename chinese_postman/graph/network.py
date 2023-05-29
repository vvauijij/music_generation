import copy


class Graph(object):
    def __init__(self, data=None):
        self.edges = {}
        if data:
            self.add_edges(data)

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(*edge)

    def add_edge(self, *args):
        self.edges[len(self.edges)] = Edge(*args)

    def remove_edges(self, edges):
        for edge in edges:
            if isinstance(edge, int):
                self.remove_edge(edge)
            else:
                self.remove_edge(*edge.contents)

    def remove_edge(self, *args):
        if len(args) == 1 and isinstance(args[0], int):
            del self.edges[args[0]]
        else:
            match = self.find_edge(*args)
            del self.edges[list(match.keys())[0]]

    @property
    def nodes(self):
        return set([node for edge in self.edges.values() for node in (edge.head, edge.tail)])

    @property
    def node_keys(self):
        return sorted(self.nodes)

    @property
    def node_orders(self):
        return {key: len(self.edge_options(key)) for key in self.nodes}

    @property
    def odd_nodes(self):
        return [key for key in self.nodes if self.node_orders[key] % 2]

    def node_options(self, node):
        options = []
        for edge in self.edges.values():
            if edge.head == node:
                options.append(edge.tail)
            elif edge.tail == node:
                options.append(edge.head)
        return sorted(options)

    @property
    def is_eularian(self):
        return len(self.odd_nodes) == 0

    @property
    def is_semi_eularian(self):
        return len(self.odd_nodes) == 2

    @property
    def all_edges(self):
        return list(self.edges.values())

    def find_edges(self, head, tail, cost=None, directed=None):
        results = {}
        for key, edge in self.edges.items():
            if not cost and not directed:
                if (head, tail) == (edge.head, edge.tail) or \
                   (tail, head) == (edge.head, edge.tail):
                    results[key] = edge
            elif not directed:
                if (head, tail, cost) == edge or \
                   (tail, head, cost) == edge:
                    results[key] = edge
            else:
                if directed and (head, tail, cost, directed) == edge:
                    results[key] = edge
                elif (tail, head, cost, directed) == edge:
                    results[key] = edge
        return results

    def find_edge(self, head, tail, cost=None, directed=None):
        matches = self.find_edges(head, tail, cost, directed)
        return dict((matches.popitem(),))

    def edge_options(self, node):
        return {key: v for key, v in self.edges.items() if node in (v.head, v.tail)}

    def edge_cost(self, *args):
        weight = min([edge.weight for edge in self.find_edges(*args).values() if edge.weight])
        return weight

    @property
    def total_cost(self):
        return sum(edge.weight for edge in self.edges.values() if edge.weight)

    def is_bridge(self, key):
        graph = copy.deepcopy(self)
        start = graph.edges[key].tail
        graph.remove_edge(key)
        stack = []
        visited = set()
        while True:
            if start not in stack:
                stack.append(start)
            visited.add(start)
            nodes = [v for v in graph.node_options(start) if v not in visited]
            if nodes:
                start = nodes[0]
            else:
                try:
                    stack.pop()
                    start = stack[-1]
                except IndexError:
                    break

        if len(visited) == len(self.nodes):
            return False
        else:
            return True

    def __len__(self):
        return len(self.edges)


class Edge(object):
    def __init__(self, head=None, tail=None, weight=0, directed=False):
        self.head = head
        self.tail = tail
        self.weight = weight
        self.directed = directed

    def __eq__(self, other):
        if len(other) == 3:
            other = other + (False,)
        return (self.head, self.tail, self.weight, self.directed) == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.contents)

    def __len__(self):
        return len([item for item in (self.head, self.tail, self.weight, self.directed) if item is not None])

    def end(self, node):
        if node == self.head:
            return self.tail
        else:
            return self.head

    @property
    def contents(self):
        return (self.head, self.tail, self.weight, self.directed)
