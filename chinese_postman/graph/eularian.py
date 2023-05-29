import copy
import itertools
import random

from chinese_postman.graph import dijkstra
from chinese_postman.graph.utils import all_unique
from chinese_postman.graph.graph_constants import FLEURY_WALK_TRIES


def fleury_walk(graph, start=None):
    visited = set()
    node = start if start else random.choice(graph.node_keys)

    route = [node]
    while len(visited) < len(graph):
        reduced_graph = copy.deepcopy(graph)
        reduced_graph.remove_edges(visited)
        options = reduced_graph.edge_options(node)
        bridges = [key for key in options.keys() if reduced_graph.is_bridge(key)]
        non_bridges = [key for key in options.keys() if key not in bridges]
        if non_bridges:
            chosen_path = random.choice(non_bridges)
        elif bridges:
            chosen_path = random.choice(bridges)
        else:
            break
        next_node = reduced_graph.edges[chosen_path].end(node)
        visited.add(chosen_path)
        route.append(next_node)
        node = next_node

    return route


def eularian_path(graph, start=None):
    for _ in range(FLEURY_WALK_TRIES):
        route = fleury_walk(graph, start)
        if len(route) == len(graph) + 1:
            return route
    return []


def find_dead_ends(graph):
    single_nodes = [key for key, order in graph.node_orders.items() if order == 1]
    return set([edge for key in single_nodes for edge in graph.edges.values()
                if key in (edge.head, edge.tail)])


def build_node_pairs(graph):
    odd_nodes = graph.odd_nodes
    return [item for item in itertools.combinations(odd_nodes, 2)]


def build_path_sets(node_pairs, set_size):
    return (item for item in itertools.combinations(node_pairs, set_size)
            if all_unique(sum(item, ())))


def unique_pairs(items):
    for item in items[1:]:
        pair = items[0], item
        leftovers = [left_item for left_item in items if left_item not in pair]
        if leftovers:
            for tail in unique_pairs(leftovers):
                yield [pair] + tail
        else:
            yield [pair]


def find_node_pair_solutions(node_pairs, graph):
    node_pair_solutions = {}
    for node_pair in node_pairs:
        if node_pair not in node_pair_solutions:
            cost, path = dijkstra.find_cost(node_pair, graph)
            node_pair_solutions[node_pair] = (cost, path)
            node_pair_solutions[node_pair[::-1]] = (cost, path[::-1])
    return node_pair_solutions


def build_min_set(node_solutions):
    odd_nodes = set([key for pair in node_solutions.keys() for key in pair])
    sorted_solutions = sorted(node_solutions.items(), key=lambda item: item[1][0])
    path_set = []
    for node_pair, solution in sorted_solutions:
        if not all(node in odd_nodes for node in node_pair):
            continue
        path_set.append((node_pair, solution))
        for node in node_pair:
            odd_nodes.remove(node)
        if not odd_nodes:
            break
    return path_set


def find_minimum_path_set(pair_sets, pair_solutions):
    cheapest_set = None
    min_cost = float('inf')
    min_route = []
    for pair_set in pair_sets:
        set_cost = sum(pair_solutions[pair][0] for pair in pair_set)
        if set_cost < min_cost:
            cheapest_set = pair_set
            min_cost = set_cost
            min_route = [pair_solutions[pair][1] for pair in pair_set]

    return cheapest_set, min_route


def add_new_edges(graph, min_route):
    new_graph = copy.deepcopy(graph)
    for node in min_route:
        for i in range(len(node) - 1):
            start, end = node[i], node[i + 1]
            cost = graph.edge_cost(start, end)
            new_graph.add_edge(start, end, cost, False)
    return new_graph


def make_eularian(graph):
    dead_ends = [edge.contents for edge in find_dead_ends(graph)]
    graph.add_edges(dead_ends)
    node_pairs = list(build_node_pairs(graph))
    pair_solutions = find_node_pair_solutions(node_pairs, graph)
    pair_sets = (x for x in unique_pairs(graph.odd_nodes))
    cheapest_set, min_route = find_minimum_path_set(pair_sets, pair_solutions)
    return add_new_edges(graph, min_route)
