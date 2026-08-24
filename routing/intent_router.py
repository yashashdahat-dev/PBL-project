from intent.mission_intent import IntentVector
from network.isl_state import ISLState

class IntentRouter:
    def __init__(self, max_latency_ms: float = 50.0, max_bw_mbps: float = 1000.0, max_loss: float = 1.0):
        self.MAX_LATENCY = max_latency_ms
        self.MAX_BW = max_bw_mbps
        self.MAX_LOSS = max_loss

    def calculate_cost(self, link_metrics: dict, intent: IntentVector) -> float:
        """
        Calculates the normalized intent-aware routing cost.
        Lower cost is better.
        """
        if link_metrics["state"] == ISLState.FAILED:
            return float('inf')

        latency = link_metrics.get("latency", self.MAX_LATENCY)
        available_bw = link_metrics.get("bandwidth", 0.0)
        packet_loss = link_metrics.get("packet_loss", 1.0)
        congestion = link_metrics.get("congestion", 1.0)
        reliability = link_metrics.get("reliability", 0.0)
        
        # Normalization (0.0 to 1.0 scale for all penalties)
        # 1. Latency (Lower is better)
        norm_latency = min(latency / self.MAX_LATENCY, 1.0)
        
        # 2. Throughput (Higher is better, so penalty is 1 - normalized_bw)
        throughput_penalty = 1.0 - min(available_bw / self.MAX_BW, 1.0)
        
        # 3. Reliability (Higher is better, lower packet loss is better)
        # Combine packet loss and intrinsic ISL unreliability
        intrinsic_unreliability = 1.0 - reliability
        reliability_penalty = min(packet_loss + intrinsic_unreliability, 1.0)
        
        # 4. Congestion (Lower is better)
        congestion_penalty = min(congestion, 1.0)

        # Compute weighted sum
        base_cost = (
            (intent.w_latency * norm_latency) +
            (intent.w_throughput * throughput_penalty) +
            (intent.w_reliability * reliability_penalty) +
            (intent.w_congestion * congestion_penalty)
        )
        
        # Priority scaling: Higher priority intents effectively "see" lower costs overall, 
        # meaning their traffic is more likely to find paths faster if queues implement strict priority.
        # For pure routing algorithms, priority might just scale the cost relative to others, 
        # though standard Q-learning operates per-intent independently.
        return base_cost * (1.0 / intent.priority)