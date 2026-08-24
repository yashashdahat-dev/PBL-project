from typing import List, Tuple
from intent.mission_intent import IntentVector
from intent.intent_dissemination import IntentDisseminationProtocol
from network.topology import ConstellationTopology
from routing.intent_router import IntentRouter
from learning.q_learning import QLearningEngine

class QRoutingManager:
    """
    I-MACSI Multi-Agent Cognitive Swarm Q-Routing Manager.

    Orchestrates the decentralised routing of packets through the LEO
    constellation. Each satellite independently selects next hops and
    updates its Q-table using dynamic reward shaping. The intent
    dissemination protocol is triggered after each routing decision
    to propagate mission awareness to the neighborhood swarm.
    """

    def __init__(self, topology: ConstellationTopology, router: IntentRouter,
                 ql_engine: QLearningEngine, epsilon: float = 0.2,
                 epsilon_decay: float = 0.995):
        self.topology = topology
        self.router = router
        self.ql_engine = ql_engine
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        # I-MACSI Intent Dissemination Protocol
        self.intent_protocol = IntentDisseminationProtocol(default_ttl=2, cache_capacity=50)

    def route_packet(self, source_id: str, dest_id: str, intent: IntentVector,
                     max_hops: int = 15, flow_id: str = None) -> Tuple[List[str], bool]:
        """
        Simulates decentralized routing of a packet from source to destination.
        Each satellite independently chooses the next hop and updates its local Q-table.
        
        I-MACSI enhancements:
        - Intent vector is passed to the decision engine for 8D resource reorganisation
        - Intent dissemination is triggered at the source to broadcast mission awareness
        - Dynamic reward shaping modulates the Q-learning update
        """
        # ---- I-MACSI: Disseminate intent from source ----
        if self.intent_protocol:
            self.intent_protocol.broadcast_intent(
                self.topology, source_id, intent,
                flow_id=flow_id, ttl=2
            )

        current_node_id = source_id
        path = [current_node_id]
        visited = [current_node_id]  # Track visited in packet header
        step = 0
        
        while current_node_id != dest_id and step < max_hops:
            step += 1
            node = self.topology.nodes[current_node_id]
            
            # Cognitive Pipeline
            node.perceive_environment()
            node.update_cognitive_state()
            
            # I-MACSI: Agent independently selects next hop with intent vector
            next_hop = node.decide_next_hop(
                intent.name, dest_id, self.epsilon, visited,
                intent_vector=intent
            )
            
            if not next_hop:
                break  # Dead end
                
            # Forward action
            metrics = node.forward_packet(next_hop)
            link_cost = self.router.calculate_cost(metrics, intent)
            
            # I-MACSI: Learning with dynamic reward shaping
            next_node = self.topology.nodes[next_hop]
            min_next_q = 0.0 if next_hop == dest_id else next_node.get_min_q_value(intent.name, dest_id)
            node.learn_from_action(
                intent.name, dest_id, next_hop, link_cost, min_next_q,
                self.ql_engine, intent_vector=intent
            )
            
            # Move packet to next hop
            current_node_id = next_hop
            path.append(current_node_id)
            visited.append(current_node_id)
            
        success = (current_node_id == dest_id)
        return path, success

    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay
