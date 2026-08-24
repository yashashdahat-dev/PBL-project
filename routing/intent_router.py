from intent.mission_intent import IntentVector
from network.isl_state import ISLState

class IntentRouter:
    """
    I-MACSI Intent-Aware Router.

    Calculates the normalized 8-dimensional intent-weighted routing cost
    for each ISL hop. The cost function dynamically adapts to the active
    mission intent, enabling semantic routing optimisation.
    """

    def __init__(self, max_latency_ms: float = 50.0, max_bw_mbps: float = 1000.0,
                 max_loss: float = 1.0, max_energy_mj: float = 1.0):
        self.MAX_LATENCY = max_latency_ms
        self.MAX_BW = max_bw_mbps
        self.MAX_LOSS = max_loss
        self.MAX_ENERGY = max_energy_mj

    def calculate_cost(self, link_metrics: dict, intent: IntentVector) -> float:
        """
        Calculates the normalized I-MACSI 8-dimensional intent-aware routing cost.
        Lower cost is better.
        """
        if link_metrics["state"] == ISLState.FAILED:
            return float('inf')

        latency = link_metrics.get("latency", self.MAX_LATENCY)
        available_bw = link_metrics.get("bandwidth", 0.0)
        packet_loss = link_metrics.get("packet_loss", 1.0)
        congestion = link_metrics.get("congestion", 1.0)
        reliability = link_metrics.get("reliability", 0.0)
        energy_cost = link_metrics.get("energy_cost", 0.0)
        encryption_overhead = link_metrics.get("encryption_overhead", 0.0)
        is_encrypted = link_metrics.get("encrypted", False)
        
        # ---- Normalization (0.0 to 1.0 scale for all penalties) ----

        # 1. Latency (Lower is better)
        norm_latency = min(latency / self.MAX_LATENCY, 1.0)
        
        # 2. Throughput (Higher is better, so penalty is 1 - normalized_bw)
        throughput_penalty = 1.0 - min(available_bw / self.MAX_BW, 1.0)
        
        # 3. Reliability (Higher is better, lower packet loss is better)
        intrinsic_unreliability = 1.0 - reliability
        reliability_penalty = min(packet_loss + intrinsic_unreliability, 1.0)
        
        # 4. Congestion (Lower is better)
        congestion_penalty = min(congestion, 1.0)

        # 5. Energy (Lower is better) — I-MACSI
        energy_penalty = min(energy_cost / self.MAX_ENERGY, 1.0) if self.MAX_ENERGY > 0 else 0.0

        # 6. Security (encrypted links are "cheaper" for secure missions) — I-MACSI
        # Penalty = 1.0 if not encrypted but security is needed, 0.0 if encrypted
        security_penalty = 0.0 if is_encrypted else 1.0
        # Also factor in encryption overhead as a minor latency cost
        security_penalty = security_penalty * 0.8 + min(encryption_overhead / 2.0, 1.0) * 0.2

        # 7. Coverage (inter-plane links score lower penalty) — I-MACSI
        # Coverage penalty is proxied by latency — longer links (inter-plane) cover more ground
        # Lower penalty for higher-latency (longer-reach) links when coverage matters
        coverage_penalty = 1.0 - norm_latency  # Inverted: long links are GOOD for coverage

        # 8. Compute (lower computational load at next hop is better) — I-MACSI
        # Approximate from congestion (proxy for node load)
        compute_penalty = min(congestion * 1.2, 1.0)

        # ---- Compute weighted sum ----
        base_cost = (
            (intent.w_latency * norm_latency) +
            (intent.w_throughput * throughput_penalty) +
            (intent.w_reliability * reliability_penalty) +
            (intent.w_congestion * congestion_penalty) +
            (intent.w_energy * energy_penalty) +
            (intent.w_security * security_penalty) +
            (intent.w_coverage * coverage_penalty) +
            (intent.w_compute * compute_penalty)
        )
        
        # Priority scaling: Higher priority intents effectively "see" lower costs overall
        return base_cost * (1.0 / intent.priority)