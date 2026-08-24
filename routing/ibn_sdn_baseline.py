import heapq
from typing import Tuple, List
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import IntentVector

class IBNSDNRouter:
    """
    Intent-Based Networking (IBN) via Software-Defined Networking Baseline.
    
    Represents centralized intent orchestration. 
    - The SDN controller extracts intents and maps them to fixed QoS routing policies.
    - Uses centralized shortest-path (Dijkstra) with weighted metrics based on intent.
    - Lacks decentralized swarm adaptability and proactive reorganization.
    """
    def __init__(self, topology: ConstellationTopology):
        self.topology = topology
        
    def _calculate_link_weight(self, source: str, target: str, intent: IntentVector) -> float:
        """
        Centralized controller calculates static link weights based on intent policy.
        """
        link = self.topology.nodes[source].isl_interfaces[target]
        
        # Policy: If latency is critical, weight heavily on latency
        if intent.w_latency > 0.5:
            return link.dynamic_latency
            
        # Policy: If throughput is critical, use available bandwidth as inverse weight
        if intent.w_throughput > 0.5:
            if link.available_bandwidth <= 0:
                return float('inf')
            return 1000.0 / link.available_bandwidth
            
        # Default policy: balanced
        return link.dynamic_latency * 0.5 + (1000.0 / max(1.0, link.available_bandwidth)) * 0.5

    def route_packet(self, source_id: str, dest_id: str, intent: IntentVector, max_hops: int = 15) -> Tuple[List[str], bool]:
        """
        Centralized SDN routing. Controller pushes paths based on global topology state.
        Vulnerable to sudden failures since it lacks rapid local adaptation.
        """
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
                weight = self._calculate_link_weight(current_node, nbr_id, intent)
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
