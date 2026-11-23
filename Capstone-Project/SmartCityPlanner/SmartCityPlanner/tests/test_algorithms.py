from algorithms.graph import dijkstra, kruskal, edmonds_karp

def test_dijkstra():
    g={"a":[("b",2),("c",7)],"b":[("a",2),("c",3)],"c":[("a",7),("b",3)]}
    assert dijkstra(g,"a","c")["distance"] == 5

def test_kruskal():
    edges,cost=kruskal(["a","b","c"],[("a","b",1),("b","c",2),("a","c",8)])
    assert cost==3 and len(edges)==2

def test_flow():
    f,_=edmonds_karp({"s":{"a":3,"b":2},"a":{"t":2},"b":{"t":3},"t":{}},"s","t")
    assert f==4
