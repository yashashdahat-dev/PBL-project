from typing import Dict, List
import random
from network.isl import InterSatelliteLink
from network.isl_state import ISLState

class SatelliteNode:
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
        self.transmission_power_dbm: float = 30.0 # Default tx power
        self.computational_load: float = 0.0 # 0.0 to 1.0
        self.beam_allocation_active: bool = False
        
    def add_neighbor(self, neighbor_id: str, link: InterSatelliteLink):
        self.isl_interfaces[neighbor_id] = link
        
    def get_active_neighbors(self) -> List[str]:
        return [nid for nid, link in self.isl_interfaces.items() if link.state != ISLState.FAILED]
        
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
                "state": link.state
            }

    def update_cognitive_state(self):
        """2. STATE: Update internal models based on perception."""
        # Detect newly failed links from perception
        for nbr, info in self.local_topology_info.items():
            if info["state"] == ISLState.FAILED:
                self.recently_failed_links.add(nbr)
            elif nbr in self.recently_failed_links and info["state"] == ISLState.ACTIVE:
                self.recently_failed_links.remove(nbr)
                
    def decide_next_hop(self, intent_name: str, dest_id: str, epsilon: float = 0.0, visited: List[str] = None) -> str:
        """3. DECISION: Choose action based on state, intent, and learned Q-values."""
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
            candidates = active_nbrs # Fallback if all valid paths are visited
            
        if random.random() < epsilon:
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
            
        # Adaptive Resource Reorganization based on Intent Priority
        # Higher priority intents (like emergency/military) boost Tx power for reliability
        # Lower priority or latency-tolerant intents use standard power for energy efficiency
        if intent_name == "Secure/Resilient Mission" or intent_name == "Critical Disaster Response":
            self.transmission_power_dbm = 40.0
            self.beam_allocation_active = True
        else:
            self.transmission_power_dbm = 30.0
            self.beam_allocation_active = False
            
        # Computational Offloading logic for intensive missions (e.g., Earth Observation)
        if intent_name == "Earth Observation":
            self.computational_load = min(1.0, self.computational_load + 0.1)

        self.routing_history.append({"dest": dest_id, "intent": intent_name, "hop": hop})
        return hop

    def forward_packet(self, hop: str) -> dict:
        """4. ACTION: Forward the packet (returns metrics to calculate cost)."""
        return self.local_topology_info[hop]

    def learn_from_action(self, intent_name: str, dest_id: str, hop: str, link_cost: float, min_next_q: float, ql_engine):
        """5. LEARNING: Update Q-table based on action outcome."""
        current_q = self.q_values[intent_name][dest_id].get(hop, 0.0)
        new_q = ql_engine.calculate_update(current_q, link_cost, min_next_q)
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