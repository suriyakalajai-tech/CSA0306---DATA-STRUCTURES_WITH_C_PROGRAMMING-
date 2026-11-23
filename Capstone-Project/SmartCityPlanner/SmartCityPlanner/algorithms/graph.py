import heapq
from collections import deque, defaultdict

def dijkstra(graph, source, target):
    dist = {n: float("inf") for n in graph}
    prev = {}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]: continue
        if u == target: break
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v], prev[v] = nd, u
                heapq.heappush(heap, (nd, v))
    if dist.get(target, float("inf")) == float("inf"): return None
    path, cur = [], target
    while cur != source:
        path.append(cur); cur = prev[cur]
    return {"distance": dist[target], "path": [source] + path[::-1]}

def alternative_path(graph, source, target):
    first = dijkstra(graph, source, target)
    if not first: return None
    # Yen-style single deviation: remove each edge of the best path and find best remaining route.
    candidates = []
    for a, b in zip(first["path"], first["path"][1:]):
        g = {u: list(edges) for u, edges in graph.items()}
        g[a] = [(v,w) for v,w in g[a] if v != b]
        g[b] = [(v,w) for v,w in g[b] if v != a]
        result = dijkstra(g, source, target)
        if result: candidates.append(result)
    return min(candidates, key=lambda x:x["distance"]) if candidates else None

def kruskal(nodes, edges):
    parent = {n:n for n in nodes}
    rank = {n:0 for n in nodes}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    result, cost = [], 0
    for u,v,w in sorted(edges, key=lambda e:e[2]):
        ru,rv=find(u),find(v)
        if ru != rv:
            if rank[ru] < rank[rv]: ru,rv=rv,ru
            parent[rv]=ru
            if rank[ru]==rank[rv]: rank[ru]+=1
            result.append((u,v,w)); cost += w
    return result, cost

def components(graph):
    seen, groups = set(), []
    for n in graph:
        if n in seen: continue
        q=[n]; seen.add(n); group=[]
        while q:
            u=q.pop(); group.append(u)
            for v,_ in graph[u]:
                if v not in seen: seen.add(v); q.append(v)
        groups.append(group)
    return groups

def edmonds_karp(capacity, source, sink):
    residual = {u:dict(vs) for u,vs in capacity.items()}
    for u,vs in list(residual.items()):
        for v in vs: residual.setdefault(v, {}).setdefault(u, 0)
    flow=0
    while True:
        parent={source:None}; q=deque([source])
        while q and sink not in parent:
            u=q.popleft()
            for v,c in residual.get(u,{}).items():
                if c>0 and v not in parent: parent[v]=u; q.append(v)
        if sink not in parent: break
        bottleneck=float("inf"); v=sink
        while parent[v] is not None:
            u=parent[v]; bottleneck=min(bottleneck,residual[u][v]); v=u
        v=sink
        while parent[v] is not None:
            u=parent[v]; residual[u][v]-=bottleneck
            residual[v][u]=residual[v].get(u,0)+bottleneck; v=u
        flow += bottleneck
    return flow, residual
