import random
from network.isl_state import ISLState

class InterSatelliteLink:
    def __init__(self, source_id: str, target_id: str, base_distance_km: float, max_bw_mbps: float):
        self.source_id = source_id
        self.target_id = target_id
        self.state = ISLState.ACTIVE
        self.availability_score = 1.0
        self.base_distance = base_distance_km
        self.max_bandwidth = max_bw_mbps
        self.current_load = 0.0
        self.base_packet_loss = 0.001
        
        # New attributes for Phase 2
        self.congestion_level = 0.0
        self.reliability = 0.999

        # I-MACSI: per-link encryption and energy modelling
        self._encrypted_mode = False
        self._tx_power_dbm = 30.0  # Inherited from endpoint satellite

    @property
    def encrypted_mode(self) -> bool:
        return self._encrypted_mode

    @encrypted_mode.setter
    def encrypted_mode(self, value: bool):
        self._encrypted_mode = value

    @property
    def encryption_overhead_ms(self) -> float:
        """Additional latency incurred by encryption processing."""
        if not self._encrypted_mode:
            return 0.0
        # 0.5–2.0 ms overhead depending on congestion
        return 0.5 + self.congestion_level * 1.5

    @property
    def energy_cost(self) -> float:
        """
        Normalised energy cost for transmitting over this link.
        Proportional to distance and current Tx power, inversely to bandwidth.
        """
        if self.state == ISLState.FAILED:
            return float('inf')
        # Linear model: energy ~ power_watts * (distance / speed_of_light)
        power_watts = 10 ** ((self._tx_power_dbm - 30) / 10)  # dBm → Watts
        propagation_time_s = self.base_distance / 3e5  # km / (km/s)
        return power_watts * propagation_time_s * 1000  # milli-joules

    @property
    def dynamic_latency(self) -> float:
        if self.state == ISLState.FAILED:
            return float('inf')
        
        speed_of_light_km_ms = 300.0
        prop_delay = self.base_distance / speed_of_light_km_ms
        utilization = min(self.current_load / self.max_bandwidth, 0.99)
        queue_delay = (utilization / (1 - utilization)) * 2.0 * (1.0 + self.congestion_level)
        jitter = random.uniform(0, 0.5)
        
        total_latency = prop_delay + queue_delay + jitter + self.encryption_overhead_ms
        return total_latency * 1.5 if self.state == ISLState.DEGRADED else total_latency

    @property
    def packet_loss(self) -> float:
        if self.state == ISLState.FAILED:
            return 1.0
            
        loss_from_state = 0.0
        if self.state == ISLState.DEGRADED:
            loss_from_state = 0.15
        elif self.state == ISLState.RECOVERING:
            loss_from_state = 0.05
            
        loss_from_congestion = self.congestion_level * 0.2
        loss_from_load = max(0, (self.current_load / self.max_bandwidth) - 0.8) * 0.05
        
        total_loss = self.base_packet_loss + loss_from_state + loss_from_congestion + loss_from_load
        return min(total_loss, 1.0)

    @property
    def available_bandwidth(self) -> float:
        if self.state in [ISLState.FAILED, ISLState.RECOVERING]:
            return 0.0
        return max(0.0, self.max_bandwidth - self.current_load) * (1.0 - self.congestion_level)