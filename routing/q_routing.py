from typing import List, Tuple
from intent.mission_intent import IntentVector
from network.topology import ConstellationTopology
from routing.intent_router import IntentRouter
from learning.q_learning import QLearningEngine

class QRoutingManager:
    def __init__(self, topology: ConstellationTopology, router: IntentRouter, ql_engine: QLearningEngine, epsilon: float = 0.2, epsilon_decay: float = 0.995):
        self.topology = topology
        self.router = router
        self.ql_engine = ql_engine
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

    def route_packet(self, source_id: str, dest_id: str, intent: IntentVector, max_hops: int = 15) -> Tuple[List[str], bool]:
        """
        Simulates decentralized routing of a packet from source to destination.
        Each satellite independently chooses the next hop and updates its local Q-table.
        """
        current_node_id = source_id
        path = [current_node_id]
        visited = [current_node_id] # Track visited in packet header
        step = 0
        
        while current_node_id != dest_id and step < max_hops:
            step += 1
            node = self.topology.nodes[current_node_id]
            
            # Cognitive Pipeline
            node.perceive_environment()
            node.update_cognitive_state()
            
            # Agent independently selects next hop
            next_hop = node.decide_next_hop(intent.name, dest_id, self.epsilon, visited)
            
            if not next_hop:
                break # Dead end
                
            # Forward action
            metrics = node.forward_packet(next_hop)
            link_cost = self.router.calculate_cost(metrics, intent)
            
            # Learning
            next_node = self.topology.nodes[next_hop]
            min_next_q = 0.0 if next_hop == dest_id else next_node.get_min_q_value(intent.name, dest_id)
            node.learn_from_action(intent.name, dest_id, next_hop, link_cost, min_next_q, self.ql_engine)
            
            # Move packet to next hop
            current_node_id = next_hop
            path.append(current_node_id)
            visited.append(current_node_id)
            
        success = (current_node_id == dest_id)
        return path, success

    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay
