from typing import Dict, List
import random
from network.isl import InterSatelliteLink
from network.isl_state import ISLState
from intent.mission_intent import IntentVector
from intent.intent_dissemination import IntentDisseminationProtocol

class SatelliteNode:
    """
    I-MACSI Cognitive Satellite Agent.

    Each satellite operates as an autonomous swarm agent with:
    - Perception of local ISL state
    - Cognitive state tracking (failures, routing history)
    - Intent-aware decision engine (8D intent vector)
    - Cooperative resource reorganisation (power, beam, compute, gateway, encryption)
    - Active intent cache for neighborhood awareness
    """

    def __init__(self, sat_id: str, plane_id: int, sat_index: int):
        self.sat_id = sat_id
        self.plane_id = plane_id
        self.sat_index = sat_index
        
        self.isl_interfaces: Dict[str, InterSatelliteLink] = {}
        self.q_values: Dict[str, Dict[str, Dict[str, float]]] = {}
        
        # Cognitive State (Phase 5)
        self.local_topology_info: Dict[str, dict] = {}
        self.recently_failed_links: set = set()
        self.routing_history: List[dict] = []
        
        # Resource Allocation State
        self.transmission_power_dbm: float = 30.0  # Default tx power
        self.computational_load: float = 0.0  # 0.0 to 1.0
        self.beam_allocation_active: bool = False
        self.encrypted_mode: bool = False  # I-MACSI security flag

        # I-MACSI: Intent cache and neighborhood awareness
        self.active_intents: Dict[str, IntentVector] = {}
        self.neighborhood_intent_summary: Dict[str, float] = {}
        self._intent_cache_capacity: int = 50

        # I-MACSI: Resource reorganisation event counter
        self.resource_reorg_events: int = 0
        self.gateway_selections: int = 0
        self.encryption_events: int = 0

    def add_neighbor(self, neighbor_id: str, link: InterSatelliteLink):
        self.isl_interfaces[neighbor_id] = link
        
    def get_active_neighbors(self) -> List[str]:
        return [nid for nid, link in self.isl_interfaces.items() if link.state != ISLState.FAILED]

    # ==========================================
    # I-MACSI INTENT DISSEMINATION
    # ==========================================

    def receive_intent(self, flow_key: str, intent: IntentVector, from_sat: str):
        """
        Receive a disseminated intent from a neighbor.
        Stores it in the local active_intents cache and updates
        the neighborhood summary.
        """
        # Evict oldest if at capacity
        if len(self.active_intents) >= self._intent_cache_capacity and flow_key not in self.active_intents:
            oldest_key = next(iter(self.active_intents))
            del self.active_intents[oldest_key]

        self.active_intents[flow_key] = intent
        self.neighborhood_intent_summary = IntentDisseminationProtocol.compute_neighborhood_summary(
            self.active_intents
        )

    def get_neighborhood_intent_summary(self) -> Dict[str, float]:
        """Return the current aggregated neighborhood intent awareness."""
        return self.neighborhood_intent_summary

    # ==========================================
    # COGNITIVE PIPELINE
    # ==========================================
    
    def perceive_environment(self):
        """1. PERCEPTION: Observe current status of all ISLs."""
        for neighbor_id, link in self.isl_interfaces.items():
            self.local_topology_info[neighbor_id] = {
                "latency": link.dynamic_latency,
                "bandwidth": link.available_bandwidth,
                "packet_loss": link.packet_loss,
                "congestion": link.congestion_level,
                "reliability": link.reliability,
                "state": link.state,
                # I-MACSI extended metrics
                "energy_cost": link.energy_cost,
                "encryption_overhead": link.encryption_overhead_ms,
                "encrypted": link.encrypted_mode,
            }

    def update_cognitive_state(self):
        """2. STATE: Update internal models based on perception."""
        # Detect newly failed links from perception
        for nbr, info in self.local_topology_info.items():
            if info["state"] == ISLState.FAILED:
                self.recently_failed_links.add(nbr)
            elif nbr in self.recently_failed_links and info["state"] == ISLState.ACTIVE:
                self.recently_failed_links.remove(nbr)
                
    def decide_next_hop(self, intent_name: str, dest_id: str, epsilon: float = 0.0,
                        visited: List[str] = None, intent_vector: IntentVector = None) -> str:
        """
        3. DECISION: Choose action based on state, intent, and learned Q-values.

        I-MACSI enhancements:
        - Consults neighborhood intent summary for cooperative swarm bias
        - Performs 8D resource reorganisation (power, beam, compute, gateway, encryption)
        """
        visited = visited or []
        active_nbrs = self.get_active_neighbors()
        if not active_nbrs:
            return None
            
        if intent_name not in self.q_values:
            self.q_values[intent_name] = {}
        if dest_id not in self.q_values[intent_name]:
            self.q_values[intent_name][dest_id] = {n: 0.0 for n in self.isl_interfaces.keys()}
            
        # Avoid visited nodes (prevent loops) and known failed nodes
        candidates = [n for n in active_nbrs if n not in visited and n not in self.recently_failed_links]
        if not candidates:
            candidates = active_nbrs  # Fallback if all valid paths are visited

        # ---- I-MACSI: Neighborhood-aware exploration bias ----
        # If the swarm region is predominantly optimising for coverage,
        # bias toward inter-plane links (different plane_id neighbors)
        coverage_bias = self.neighborhood_intent_summary.get("w_coverage", 0.0)

        if random.random() < epsilon:
            if coverage_bias > 0.15 and intent_vector and intent_vector.w_coverage > 0.1:
                # Prefer inter-plane neighbors for geographic spread
                inter_plane = [n for n in candidates if self._is_inter_plane(n)]
                hop = random.choice(inter_plane) if inter_plane else random.choice(candidates)
            else:
                hop = random.choice(candidates)
        else:
            best_nbr = None
            min_q = float('inf')
            
            for nbr in candidates:
                q_val = self.q_values[intent_name][dest_id].get(nbr, 0.0)
                if q_val < min_q:
                    min_q = q_val
                    best_nbr = nbr
                    
            hop = best_nbr if best_nbr else random.choice(candidates)

        # ---- I-MACSI: 8D Resource Reorganisation ----
        if intent_vector:
            self._reorganize_resources(intent_vector, hop)

        self.routing_history.append({"dest": dest_id, "intent": intent_name, "hop": hop})
        return hop

    def _reorganize_resources(self, intent: IntentVector, next_hop: str):
        """
        I-MACSI Cooperative Resource Reorganisation.
        Adjusts transmission power, beam allocation, compute offloading,
        encryption mode, and gateway selection based on the 8D intent vector.
        """
        self.resource_reorg_events += 1

        # --- Power control (energy vs reliability trade-off) ---
        if intent.w_energy > 0.15:
            # Energy-sensitive: reduce Tx power
            self.transmission_power_dbm = max(20.0, 30.0 - intent.w_energy * 15)
        elif intent.w_reliability > 0.25 or intent.w_security > 0.2:
            # Reliability / security: boost Tx power
            self.transmission_power_dbm = min(43.0, 30.0 + intent.w_reliability * 15)
        else:
            self.transmission_power_dbm = 30.0

        # --- Beam allocation ---
        self.beam_allocation_active = (
            intent.w_reliability > 0.25 or
            intent.w_coverage > 0.15 or
            intent.priority >= 8
        )

        # --- Encryption ---
        if intent.w_security > 0.1:
            if not self.encrypted_mode:
                self.encrypted_mode = True
                self.encryption_events += 1
                # Propagate encryption to the outgoing link
                if next_hop in self.isl_interfaces:
                    self.isl_interfaces[next_hop].encrypted_mode = True
        else:
            self.encrypted_mode = False
            if next_hop in self.isl_interfaces:
                self.isl_interfaces[next_hop].encrypted_mode = False

        # --- Computational offloading ---
        if intent.w_compute > 0.1:
            self.computational_load = min(1.0, self.computational_load + intent.w_compute * 0.2)
        else:
            self.computational_load = max(0.0, self.computational_load - 0.05)

        # --- Tx power to link model ---
        if next_hop in self.isl_interfaces:
            self.isl_interfaces[next_hop]._tx_power_dbm = self.transmission_power_dbm

    def _is_inter_plane(self, neighbor_id: str) -> bool:
        """Check if a neighbor is in a different orbital plane."""
        # Parse plane from ID format P{plane}_S{slot}
        try:
            nbr_plane = int(neighbor_id.split("_")[0][1:])
            return nbr_plane != self.plane_id
        except (ValueError, IndexError):
            return False

    def select_gateway(self) -> bool:
        """
        I-MACSI gateway selection.
        Returns True if this satellite should act as an Earth gateway
        (plane boundary node with lowest computational load).
        """
        if self.plane_id == 0 or self.computational_load < 0.5:
            self.gateway_selections += 1
            return True
        return False

    def forward_packet(self, hop: str) -> dict:
        """4. ACTION: Forward the packet (returns metrics to calculate cost)."""
        return self.local_topology_info[hop]

    def learn_from_action(self, intent_name: str, dest_id: str, hop: str,
                          link_cost: float, min_next_q: float, ql_engine,
                          intent_vector: IntentVector = None):
        """
        5. LEARNING: Update Q-table based on action outcome.
        I-MACSI: passes the intent vector to the learning engine
        for dynamic reward shaping.
        """
        current_q = self.q_values[intent_name][dest_id].get(hop, 0.0)
        new_q = ql_engine.calculate_update(current_q, link_cost, min_next_q, intent_vector)
        self.q_values[intent_name][dest_id][hop] = new_q
        
    # ==========================================
    # UTILS
    # ==========================================
    def get_min_q_value(self, intent_name: str, dest_id: str) -> float:
        if intent_name not in self.q_values or dest_id not in self.q_values[intent_name]:
            return 0.0
        active_nbrs = self.get_active_neighbors()
        valid_qs = [self.q_values[intent_name][dest_id][n] for n in active_nbrs if n in self.q_values[intent_name][dest_id]]
        return min(valid_qs) if valid_qs else float('inf')

    def update_link_state(self, neighbor_id: str, new_state: ISLState):
        if neighbor_id in self.isl_interfaces:
            self.isl_interfaces[neighbor_id].state = new_state