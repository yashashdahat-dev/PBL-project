import random
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import IntentVector
from learning.q_learning import QLearningEngine

class BasicQRoutingManager:
    """
    Standard Q-Routing baseline.
    - No intents (all traffic uses the same Q table)
    - No cognitive memory (no `visited` checking, prone to loops)
    - Cost is strictly based on link latency
    """
    def __init__(self, topology: ConstellationTopology, ql_engine: QLearningEngine, epsilon: float = 0.1, epsilon_decay: float = 0.995):
        self.topology = topology
        self.ql_engine = ql_engine
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        
        # Initialize basic Q-table for all nodes: Q[dest][neighbor]
        self.q_table = {node_id: {} for node_id in self.topology.nodes}
        for node_id, node in self.topology.nodes.items():
            for dest_id in self.topology.nodes:
                self.q_table[node_id][dest_id] = {nbr: 0.0 for nbr in node.isl_interfaces}
                
    def decay_epsilon(self):
        self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)
        
    def route_packet(self, source_id: str, dest_id: str, intent: IntentVector, max_hops: int = 15):
        path = [source_id]
        current_node_id = source_id
        step = 0
        
        while current_node_id != dest_id and step < max_hops:
            step += 1
            node = self.topology.nodes[current_node_id]
            
            active_nbrs = [n for n, l in node.isl_interfaces.items() if l.state != ISLState.FAILED]
            if not active_nbrs:
                break # Dead end
                
            # Basic Epsilon-Greedy (No cognitive loop prevention)
            if random.random() < self.epsilon:
                next_hop = random.choice(active_nbrs)
            else:
                best_nbr = None
                min_q = float('inf')
                for nbr in active_nbrs:
                    q_val = self.q_table[current_node_id][dest_id].get(nbr, 0.0)
                    if q_val < min_q:
                        min_q = q_val
                        best_nbr = nbr
                next_hop = best_nbr if best_nbr else random.choice(active_nbrs)
                
            # Action & Cost
            link = node.isl_interfaces[next_hop]
            link_cost = link.dynamic_latency
            
            # Learn
            min_next_q = 0.0
            if next_hop != dest_id:
                next_node = self.topology.nodes[next_hop]
                next_active = [n for n, l in next_node.isl_interfaces.items() if l.state != ISLState.FAILED]
                if next_active:
                    min_next_q = min([self.q_table[next_hop][dest_id].get(n, 0.0) for n in next_active])
                else:
                    min_next_q = 1000.0 # Penalty for dead end
            
            current_q = self.q_table[current_node_id][dest_id].get(next_hop, 0.0)
            new_q = self.ql_engine.calculate_update(current_q, link_cost, min_next_q)
            self.q_table[current_node_id][dest_id][next_hop] = new_q
            
            current_node_id = next_hop
            path.append(current_node_id)
            
            # Detect loop artificially for simulation break
            if len(path) > max_hops:
                break
                
        success = (current_node_id == dest_id)
        return path, success
