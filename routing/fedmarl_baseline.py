import random
from typing import Tuple, List
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import IntentVector
from learning.q_learning import QLearningEngine

class FedMARLRouter:
    """
    Federated Multi-Agent Reinforcement Learning (FedMARL) Baseline.
    
    Represents current state-of-the-art decentralized AI routing (e.g. MAPPO/FedQ).
    - Uses decentralized Q-routing with federation (synchronization of Q-tables).
    - Lacks Semantic Intent Awareness (optimizes purely for network metrics).
    - Lacks Joint Resource Optimization (no beam steering, compute placement, etc).
    """
    def __init__(self, topology: ConstellationTopology, ql_engine: QLearningEngine, epsilon: float = 0.1, epsilon_decay: float = 0.995):
        self.topology = topology
        self.ql_engine = ql_engine
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        
        # Q-table: Q[current_node][dest_node][next_hop]
        self.q_table = {node_id: {} for node_id in self.topology.nodes}
        for node_id, node in self.topology.nodes.items():
            for dest_id in self.topology.nodes:
                self.q_table[node_id][dest_id] = {nbr: 0.0 for nbr in node.isl_interfaces}
                
    def decay_epsilon(self):
        self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)
        
    def synchronize_models(self):
        """
        Simulates Federated Averaging (FedAvg) of Q-tables across neighbors.
        This represents the 'Fed' in FedMARL.
        """
        updates = []
        for node_id, node in self.topology.nodes.items():
            for nbr in node.isl_interfaces:
                if node.isl_interfaces[nbr].state != ISLState.FAILED:
                    updates.append((node_id, nbr))
                    
        for node_id, nbr in updates:
            for dest_id in self.topology.nodes:
                for common_nbr in set(self.q_table[node_id][dest_id].keys()).intersection(set(self.q_table[nbr][dest_id].keys())):
                    # Average the learned values (simplified FedAvg)
                    avg_q = (self.q_table[node_id][dest_id][common_nbr] + self.q_table[nbr][dest_id][common_nbr]) / 2.0
                    self.q_table[node_id][dest_id][common_nbr] = avg_q
                    self.q_table[nbr][dest_id][common_nbr] = avg_q

    def route_packet(self, source_id: str, dest_id: str, intent: IntentVector = None, max_hops: int = 15) -> Tuple[List[str], bool]:
        """Routes a packet using decentralized FedMARL policies."""
        path = [source_id]
        current_node_id = source_id
        step = 0
        visited = set([source_id])
        
        while current_node_id != dest_id and step < max_hops:
            step += 1
            node = self.topology.nodes[current_node_id]
            
            # Avoid loops by filtering visited nodes, unless trapped
            active_nbrs = [n for n, l in node.isl_interfaces.items() if l.state != ISLState.FAILED]
            valid_nbrs = [n for n in active_nbrs if n not in visited]
            if not valid_nbrs:
                valid_nbrs = active_nbrs # Fallback if trapped
                
            if not valid_nbrs:
                break # Dead end
                
            # Epsilon-Greedy Policy
            if random.random() < self.epsilon:
                next_hop = random.choice(valid_nbrs)
            else:
                best_nbr = None
                min_q = float('inf')
                for nbr in valid_nbrs:
                    q_val = self.q_table[current_node_id][dest_id].get(nbr, 0.0)
                    if q_val < min_q:
                        min_q = q_val
                        best_nbr = nbr
                next_hop = best_nbr if best_nbr else random.choice(valid_nbrs)
                
            # Fixed Reward Function (Optimizing purely for latency, ignoring intent)
            link = node.isl_interfaces[next_hop]
            link_cost = link.dynamic_latency
            
            # Standard Bellman Update
            min_next_q = 0.0
            if next_hop != dest_id:
                next_node = self.topology.nodes[next_hop]
                next_active = [n for n, l in next_node.isl_interfaces.items() if l.state != ISLState.FAILED]
                if next_active:
                    min_next_q = min([self.q_table[next_hop][dest_id].get(n, 0.0) for n in next_active])
                else:
                    min_next_q = 1000.0 # Penalty
            
            current_q = self.q_table[current_node_id][dest_id].get(next_hop, 0.0)
            # Use basic update (ignores intent modulation)
            new_q = current_q + self.ql_engine.alpha * (-link_cost + self.ql_engine.gamma * min_next_q - current_q)
            self.q_table[current_node_id][dest_id][next_hop] = new_q
            
            current_node_id = next_hop
            path.append(current_node_id)
            visited.add(current_node_id)
            
        success = (current_node_id == dest_id)
        return path, success
