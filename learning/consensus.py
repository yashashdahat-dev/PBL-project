import copy

class ConsensusEngine:
    """
    Implements decentralized Federated Multi-Agent Learning (FedMARL).
    Satellites periodically share and average their Q-tables with active neighbors
    to achieve swarm-level awareness of network conditions and intent costs.
    """
    def __init__(self, sync_interval: int = 10, consensus_weight: float = 0.2):
        self.sync_interval = sync_interval
        self.consensus_weight = consensus_weight  # How much to trust neighbors

    def synchronize(self, topology):
        """
        Runs a round of consensus where each node averages its Q-values
        with its active neighbors to disseminate intent-aware learned costs.
        """
        # Snapshot current state to ensure synchronous updates
        snapshot = {
            node_id: copy.deepcopy(node.q_values)
            for node_id, node in topology.nodes.items()
        }
            
        for node_id, node in topology.nodes.items():
            active_nbrs = node.get_active_neighbors()
            if not active_nbrs:
                continue
                
            # Iterate through intents and destinations the node knows about
            for intent_name, dest_dict in snapshot[node_id].items():
                for dest_id, action_dict in dest_dict.items():
                    for hop, q_val in action_dict.items():
                        
                        # Gather neighbors' Q-values for the exact same (intent, dest, hop)
                        # This happens if multiple nodes share the same neighbor 'hop'
                        neighbor_qs = []
                        for nbr in active_nbrs:
                            nbr_q_table = snapshot.get(nbr, {})
                            if intent_name in nbr_q_table and dest_id in nbr_q_table[intent_name]:
                                if hop in nbr_q_table[intent_name][dest_id]:
                                    neighbor_qs.append(nbr_q_table[intent_name][dest_id][hop])
                                        
                        if neighbor_qs:
                            avg_nbr_q = sum(neighbor_qs) / len(neighbor_qs)
                            # Soft update local Q-value towards the neighborhood consensus
                            current_q = node.q_values[intent_name][dest_id][hop]
                            new_q = (1 - self.consensus_weight) * current_q + self.consensus_weight * avg_nbr_q
                            node.q_values[intent_name][dest_id][hop] = new_q
