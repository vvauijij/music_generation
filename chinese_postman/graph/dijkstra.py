def summarize_path(end, previous_nodes):
    route = []
    prev = end
    while prev:
        route.insert(0, prev)
        prev = previous_nodes[prev]
    return route


def find_cost(path, graph):
    start, end = path

    all_nodes = graph.node_keys
    unvisited = set(all_nodes)
    total_cost = graph.total_cost
    node_costs = {node: total_cost for node in all_nodes}
    node_costs[start] = 0

    previous_nodes = {node: None for node in all_nodes}

    node = start
    while unvisited:
        for option in graph.edge_options(node).values():
            next_node = option.end(node)
            if next_node not in unvisited:
                continue
            if node_costs[next_node] > node_costs[node] + option.weight:
                node_costs[next_node] = node_costs[node] + option.weight
                previous_nodes[next_node] = node
        unvisited.remove(node)
        options = {key: v for key, v in node_costs.items() if key in unvisited}
        try:
            node = min(options, key=options.get)
        except ValueError:
            break
        if node == end:
            break

    cost = node_costs[end]
    shortest_path = summarize_path(end, previous_nodes)

    return cost, shortest_path
