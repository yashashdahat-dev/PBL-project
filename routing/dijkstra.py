import heapq
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import IntentVector

class ShortestPathRouter:
    """
    Centralized Shortest Path (Dijkstra) baseline.
    Has perfect global knowledge of topology and link latencies.
    """
    def __init__(self, topology: ConstellationTopology):
        self.topology = topology
        
    def route_packet(self, source_id: str, dest_id: str, intent: IntentVector, max_hops: int = 15):
        # Run Dijkstra
        distances = {node: float('inf') for node in self.topology.nodes}
        previous = {node: None for node in self.topology.nodes}
        distances[source_id] = 0
        pq = [(0, source_id)]
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node == dest_id:
                break
                
            if current_dist > distances[current_node]:
                continue
                
            node = self.topology.nodes[current_node]
            for nbr_id, link in node.isl_interfaces.items():
                if link.state == ISLState.FAILED:
                    continue
                    
                # Use dynamic latency as weight
                weight = link.dynamic_latency
                distance = current_dist + weight
                
                if distance < distances[nbr_id]:
                    distances[nbr_id] = distance
                    previous[nbr_id] = current_node
                    heapq.heappush(pq, (distance, nbr_id))
                    
        # Reconstruct path
        path = []
        curr = dest_id
        while curr is not None:
            path.insert(0, curr)
            if curr == source_id:
                break
            curr = previous[curr]
            
        if not path or path[0] != source_id:
            return [], False
            
        return path, True
