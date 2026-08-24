import copy
from intent.intent_dissemination import IntentDisseminationProtocol


class ConsensusEngine:
    """
    I-MACSI Decentralized Federated Multi-Agent Learning (FedMARL).

    Satellites periodically share and average their Q-tables AND
    active intent caches with active neighbors to achieve swarm-level
    awareness of both network conditions and regional mission objectives.
    """

    def __init__(self, sync_interval: int = 10, consensus_weight: float = 0.2):
        self.sync_interval = sync_interval
        self.consensus_weight = consensus_weight  # How much to trust neighbors

    def synchronize(self, topology):
        """
        Runs a round of consensus where each node:
        1. Averages its Q-values with active neighbors (FedMARL)
        2. Merges intent caches from neighbors (I-MACSI Intent Dissemination)
        """
        # ---- Phase 1: Q-Table Consensus (existing FedMARL) ----
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

        # ---- Phase 2: I-MACSI Intent Cache Sharing ----
        # Each node merges its neighbors' active_intents caches so the
        # swarm builds a regional picture of what missions are active.
        intent_snapshot = {
            node_id: dict(node.active_intents)
            for node_id, node in topology.nodes.items()
        }

        for node_id, node in topology.nodes.items():
            active_nbrs = node.get_active_neighbors()
            if not active_nbrs:
                continue

            for nbr_id in active_nbrs:
                nbr_intents = intent_snapshot.get(nbr_id, {})
                for flow_key, intent_vec in nbr_intents.items():
                    # Only add if not already present (deduplication)
                    if flow_key not in node.active_intents:
                        node.receive_intent(flow_key, intent_vec, nbr_id)

            # Recompute summary after merging
            node.neighborhood_intent_summary = (
                IntentDisseminationProtocol.compute_neighborhood_summary(node.active_intents)
            )
