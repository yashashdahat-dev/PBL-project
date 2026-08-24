"""
I-MACSI Intent Dissemination Protocol.

Implements gossip-style flooding of Mission Intent Vectors across
the satellite constellation. Each satellite maintains a local cache
of active intents from its neighborhood, enabling cooperative
swarm-level awareness of regional mission objectives.
"""

from typing import Dict, Optional
from intent.mission_intent import IntentVector


class IntentDisseminationProtocol:
    """
    Manages intent broadcasting, reception, and aggregation
    across the satellite swarm.
    """

    def __init__(self, default_ttl: int = 2, cache_capacity: int = 50):
        self.default_ttl = default_ttl
        self.cache_capacity = cache_capacity
        # Dissemination statistics
        self.total_messages_sent = 0
        self.total_messages_received = 0

    def broadcast_intent(self, topology, source_sat_id: str, intent: IntentVector,
                         flow_id: str = None, ttl: int = None):
        """
        Flood the intent vector from source_sat to its active neighbors.
        Each neighbor stores the intent and re-broadcasts if TTL > 0.
        
        Args:
            topology: ConstellationTopology instance.
            source_sat_id: ID of the originating satellite.
            intent: The IntentVector to disseminate.
            flow_id: Optional unique flow identifier for deduplication.
            ttl: Hops remaining for propagation. Defaults to self.default_ttl.
        """
        if ttl is None:
            ttl = self.default_ttl

        if ttl <= 0:
            return

        flow_key = flow_id or f"{source_sat_id}_{intent.name}_{id(intent)}"

        source_node = topology.nodes.get(source_sat_id)
        if not source_node:
            return

        active_neighbors = source_node.get_active_neighbors()
        for nbr_id in active_neighbors:
            nbr_node = topology.nodes.get(nbr_id)
            if nbr_node is None:
                continue

            # Deliver to neighbor
            self.total_messages_sent += 1
            self.total_messages_received += 1
            nbr_node.receive_intent(flow_key, intent, source_sat_id)

            # Re-broadcast with decremented TTL
            if ttl > 1:
                self.broadcast_intent(topology, nbr_id, intent, flow_key, ttl - 1)

    @staticmethod
    def compute_neighborhood_summary(active_intents: Dict[str, IntentVector]) -> Dict[str, float]:
        """
        Aggregate all cached intents into a single summary vector.
        Returns a dict of average weights across all active intents.
        """
        if not active_intents:
            return {
                "w_latency": 0.0, "w_throughput": 0.0,
                "w_reliability": 0.0, "w_congestion": 0.0,
                "w_energy": 0.0, "w_security": 0.0,
                "w_coverage": 0.0, "w_compute": 0.0,
                "avg_priority": 5.0,
            }

        n = len(active_intents)
        summary = {
            "w_latency": 0.0, "w_throughput": 0.0,
            "w_reliability": 0.0, "w_congestion": 0.0,
            "w_energy": 0.0, "w_security": 0.0,
            "w_coverage": 0.0, "w_compute": 0.0,
            "avg_priority": 0.0,
        }

        for intent in active_intents.values():
            summary["w_latency"] += intent.w_latency
            summary["w_throughput"] += intent.w_throughput
            summary["w_reliability"] += intent.w_reliability
            summary["w_congestion"] += intent.w_congestion
            summary["w_energy"] += intent.w_energy
            summary["w_security"] += intent.w_security
            summary["w_coverage"] += intent.w_coverage
            summary["w_compute"] += intent.w_compute
            summary["avg_priority"] += intent.priority

        for key in summary:
            summary[key] /= n

        return summary
