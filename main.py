from SampleSpace import SampleSpace
from Graph import MeanderGraph

space = SampleSpace(n=4)
print(f"Total Meanders: {len(space)}")

meander_graph = MeanderGraph(space)
print(f"Graph Nodes: {meander_graph.graph.number_of_nodes()}")
print(f"Graph Edges: {meander_graph.graph.number_of_edges()}")

meander_graph._highlight_worst_edge()
print(f"Worst Case Value: {meander_graph.worst_case_value}")

meander_graph.draw(highlight_worst=True)



