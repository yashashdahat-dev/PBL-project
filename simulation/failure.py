import random
from typing import Optional
from network.topology import ConstellationTopology
from network.isl_state import ISLState

class FailureModel:
    def __init__(self, topology: ConstellationTopology):
        self.topology = topology
        
    def inject_random_failure(self, failure_probability: float = 0.05) -> Optional[tuple]:
        """Randomly selects an active link and sets it to FAILED (bidirectional)."""
        if random.random() > failure_probability:
            return None
            
        active_links = []
        for node_id, node in self.topology.nodes.items():
            for nbr_id, link in node.isl_interfaces.items():
                # Avoid duplicates by enforcing node_a < node_b
                if link.state == ISLState.ACTIVE and node_id < nbr_id:
                    active_links.append((node_id, nbr_id))
                    
        if not active_links:
            return None
            
        node_a, node_b = random.choice(active_links)
        
        # Inject bidirectional failure
        self.topology.nodes[node_a].update_link_state(node_b, ISLState.FAILED)
        self.topology.nodes[node_b].update_link_state(node_a, ISLState.FAILED)
        
        return (node_a, node_b)
        
    def recover_all_failures(self):
        """Recovers all failed links back to ACTIVE."""
        for node_id, node in self.topology.nodes.items():
            for nbr_id, link in node.isl_interfaces.items():
                if link.state == ISLState.FAILED:
                    node.update_link_state(nbr_id, ISLState.ACTIVE)
