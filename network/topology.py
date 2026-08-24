from agents.satellite_agent import SatelliteNode
from network.isl import InterSatelliteLink

class ConstellationTopology:
    def __init__(self, num_planes: int, sats_per_plane: int):
        self.num_planes = num_planes
        self.sats_per_plane = sats_per_plane
        self.nodes = {}
        
    def build_network(self):
        for p in range(self.num_planes):
            for s in range(self.sats_per_plane):
                sat_id = f"P{p}_S{s}"
                self.nodes[sat_id] = SatelliteNode(sat_id, p, s)
                
        for p in range(self.num_planes):
            for s in range(self.sats_per_plane):
                current_id = f"P{p}_S{s}"
                
                next_s = (s + 1) % self.sats_per_plane
                intra_id = f"P{p}_S{next_s}"
                
                next_p = (p + 1) % self.num_planes
                inter_id = f"P{next_p}_S{s}"
                
                self._create_bidirectional_link(current_id, intra_id, distance=1500)
                self._create_bidirectional_link(current_id, inter_id, distance=2500)
                
    def _create_bidirectional_link(self, node_a: str, node_b: str, distance: float):
        if node_b not in self.nodes[node_a].isl_interfaces:
            link_ab = InterSatelliteLink(node_a, node_b, distance, max_bw_mbps=1000.0)
            link_ba = InterSatelliteLink(node_b, node_a, distance, max_bw_mbps=1000.0)
            self.nodes[node_a].add_neighbor(node_b, link_ab)
            self.nodes[node_b].add_neighbor(node_a, link_ba)

    def is_gateway_candidate(self, sat_id: str) -> bool:
        """
        I-MACSI gateway selection heuristic.
        Satellites at the first or last orbital plane are candidates
        for Earth-gateway downlink (closer to ground stations).
        """
        node = self.nodes.get(sat_id)
        if node is None:
            return False
        return node.plane_id == 0 or node.plane_id == self.num_planes - 1