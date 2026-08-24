from dataclasses import dataclass

@dataclass
class IntentVector:
    name: str
    w_latency: float
    w_throughput: float
    w_reliability: float
    w_congestion: float = 0.0
    priority: int = 1
    
    def __post_init__(self):
        """Normalizes weights so they sum to 1.0 for consistent cost scaling."""
        total = self.w_latency + self.w_throughput + self.w_reliability + self.w_congestion
        if total > 0:
            self.w_latency /= total
            self.w_throughput /= total
            self.w_reliability /= total
            self.w_congestion /= total

class StandardIntents:
    LOW_LATENCY = IntentVector(
        name="Low Latency Stream",
        w_latency=0.8,
        w_throughput=0.1,
        w_reliability=0.1,
        w_congestion=0.0,
        priority=10
    )
    
    CRITICAL_DISASTER = IntentVector(
        name="Critical Disaster Response",
        w_latency=0.7,
        w_throughput=0.0,
        w_reliability=0.2,
        w_congestion=0.1,
        priority=10
    )
    
    EARTH_OBSERVATION = IntentVector(
        name="Earth Observation",
        w_latency=0.1,
        w_throughput=0.6,
        w_reliability=0.1,
        w_congestion=0.2,
        priority=5
    )
    
    SECURE_MISSION = IntentVector(
        name="Secure/Resilient Mission",
        w_latency=0.1,
        w_throughput=0.1,
        w_reliability=0.8,
        w_congestion=0.0,
        priority=8
    )
    
    ENVIRONMENTAL_MONITORING = IntentVector(
        name="Environmental Monitoring",
        w_latency=0.1,
        w_throughput=0.5,
        w_reliability=0.1,
        w_congestion=0.3,
        priority=4
    )

    AUTONOMOUS_MARITIME = IntentVector(
        name="Autonomous Maritime Navigation",
        w_latency=0.6,
        w_throughput=0.1,
        w_reliability=0.3,
        w_congestion=0.0,
        priority=7
    )

    MILITARY_RECONNAISSANCE = IntentVector(
        name="Military Reconnaissance",
        w_latency=0.3,
        w_throughput=0.3,
        w_reliability=0.4,
        w_congestion=0.0,
        priority=9
    )

    GLOBAL_INTERNET = IntentVector(
        name="Global Internet Services",
        w_latency=0.3,
        w_throughput=0.7,
        w_reliability=0.0,
        w_congestion=0.0,
        priority=3
    )

    REMOTE_HEALTHCARE = IntentVector(
        name="Remote Healthcare",
        w_latency=0.8,
        w_throughput=0.1,
        w_reliability=0.1,
        w_congestion=0.0,
        priority=9
    )

    PRECISION_AGRI = IntentVector(
        name="Precision Agriculture",
        w_latency=0.1,
        w_throughput=0.6,
        w_reliability=0.1,
        w_congestion=0.2,
        priority=2
    )

    INDUSTRIAL_IOT = IntentVector(
        name="Industrial IoT",
        w_latency=0.2,
        w_throughput=0.3,
        w_reliability=0.3,
        w_congestion=0.2,
        priority=5
    )


class IntentExtractionEngine:
    """
    Parses natural language mission descriptions into semantic representations.
    Simulates semantic NLP embedding by mapping keywords to intent priorities.
    """
    @staticmethod
    def extract_intent(description: str) -> IntentVector:
        desc = description.lower()
        
        # Base weights
        w_l, w_t, w_r, w_c = 0.0, 0.0, 0.0, 0.0
        priority = 5
        
        # Latency keywords
        if any(w in desc for w in ["fast", "immediate", "urgent", "latency", "real-time", "emergency", "surgery", "drone"]):
            w_l += 0.6
            priority += 3
            
        # Throughput keywords
        if any(w in desc for w in ["video", "download", "bandwidth", "massive", "data", "streaming", "observation", "image"]):
            w_t += 0.6
            
        # Reliability/Security keywords
        if any(w in desc for w in ["secure", "military", "critical", "reliable", "encrypted", "guarantee"]):
            w_r += 0.6
            priority += 2
            
        # Congestion/Efficiency keywords
        if any(w in desc for w in ["iot", "agriculture", "sensor", "efficient", "fairness", "bulk"]):
            w_c += 0.4
            priority -= 2

        # Normalize and fallback
        total = w_l + w_t + w_r + w_c
        if total == 0:
            return StandardIntents.GLOBAL_INTERNET
            
        return IntentVector(
            name="Custom Dynamic Intent",
            w_latency=w_l,
            w_throughput=w_t,
            w_reliability=w_r,
            w_congestion=w_c,
            priority=max(1, min(10, priority))
        )
