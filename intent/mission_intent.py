from dataclasses import dataclass

@dataclass
class IntentVector:
    """
    I-MACSI 8-Dimensional Mission Intent Vector.
    
    Encodes high-level mission semantics into a normalised weight vector
    that dynamically shapes the reward function of every satellite agent.
    """
    name: str
    # --- Original 4 dimensions ---
    w_latency: float       # Latency sensitivity (lower is better)
    w_throughput: float     # Bandwidth / data-rate demand
    w_reliability: float   # Packet delivery guarantee
    w_congestion: float    # Congestion avoidance weight
    # --- I-MACSI extended dimensions ---
    w_energy: float = 0.0      # Energy efficiency constraint
    w_security: float = 0.0    # Encryption / security level
    w_coverage: float = 0.0    # Geographic coverage priority
    w_compute: float = 0.0     # Computational demand (offloading)
    # --- Meta ---
    priority: int = 1
    application_category: str = "general"

    def __post_init__(self):
        """Normalizes weights so they sum to 1.0 for consistent cost scaling."""
        total = (
            self.w_latency + self.w_throughput + self.w_reliability +
            self.w_congestion + self.w_energy + self.w_security +
            self.w_coverage + self.w_compute
        )
        if total > 0:
            self.w_latency /= total
            self.w_throughput /= total
            self.w_reliability /= total
            self.w_congestion /= total
            self.w_energy /= total
            self.w_security /= total
            self.w_coverage /= total
            self.w_compute /= total

    def to_dict(self) -> dict:
        """Serialize the intent vector for API / dissemination."""
        return {
            "name": self.name,
            "w_latency": round(self.w_latency, 4),
            "w_throughput": round(self.w_throughput, 4),
            "w_reliability": round(self.w_reliability, 4),
            "w_congestion": round(self.w_congestion, 4),
            "w_energy": round(self.w_energy, 4),
            "w_security": round(self.w_security, 4),
            "w_coverage": round(self.w_coverage, 4),
            "w_compute": round(self.w_compute, 4),
            "priority": self.priority,
            "application_category": self.application_category,
        }


class StandardIntents:
    LOW_LATENCY = IntentVector(
        name="Low Latency Stream",
        w_latency=0.55, w_throughput=0.10, w_reliability=0.10,
        w_congestion=0.05, w_energy=0.05, w_security=0.0,
        w_coverage=0.0, w_compute=0.0,
        priority=10, application_category="realtime"
    )

    CRITICAL_DISASTER = IntentVector(
        name="Critical Disaster Response",
        w_latency=0.40, w_throughput=0.05, w_reliability=0.20,
        w_congestion=0.05, w_energy=0.0, w_security=0.05,
        w_coverage=0.15, w_compute=0.0,
        priority=10, application_category="emergency"
    )

    EARTH_OBSERVATION = IntentVector(
        name="Earth Observation",
        w_latency=0.05, w_throughput=0.35, w_reliability=0.05,
        w_congestion=0.10, w_energy=0.05, w_security=0.0,
        w_coverage=0.15, w_compute=0.20,
        priority=5, application_category="observation"
    )

    SECURE_MISSION = IntentVector(
        name="Secure/Resilient Mission",
        w_latency=0.05, w_throughput=0.05, w_reliability=0.35,
        w_congestion=0.0, w_energy=0.0, w_security=0.40,
        w_coverage=0.0, w_compute=0.0,
        priority=8, application_category="military"
    )

    ENVIRONMENTAL_MONITORING = IntentVector(
        name="Environmental Monitoring",
        w_latency=0.05, w_throughput=0.25, w_reliability=0.05,
        w_congestion=0.15, w_energy=0.20, w_security=0.0,
        w_coverage=0.20, w_compute=0.05,
        priority=4, application_category="observation"
    )

    AUTONOMOUS_MARITIME = IntentVector(
        name="Autonomous Maritime Navigation",
        w_latency=0.35, w_throughput=0.05, w_reliability=0.20,
        w_congestion=0.0, w_energy=0.05, w_security=0.05,
        w_coverage=0.20, w_compute=0.0,
        priority=7, application_category="navigation"
    )

    MILITARY_RECONNAISSANCE = IntentVector(
        name="Military Reconnaissance",
        w_latency=0.15, w_throughput=0.15, w_reliability=0.15,
        w_congestion=0.0, w_energy=0.0, w_security=0.30,
        w_coverage=0.10, w_compute=0.10,
        priority=9, application_category="military"
    )

    GLOBAL_INTERNET = IntentVector(
        name="Global Internet Services",
        w_latency=0.20, w_throughput=0.40, w_reliability=0.05,
        w_congestion=0.10, w_energy=0.05, w_security=0.0,
        w_coverage=0.15, w_compute=0.0,
        priority=3, application_category="broadband"
    )

    REMOTE_HEALTHCARE = IntentVector(
        name="Remote Healthcare",
        w_latency=0.40, w_throughput=0.10, w_reliability=0.20,
        w_congestion=0.0, w_energy=0.0, w_security=0.15,
        w_coverage=0.05, w_compute=0.05,
        priority=9, application_category="emergency"
    )

    PRECISION_AGRI = IntentVector(
        name="Precision Agriculture",
        w_latency=0.05, w_throughput=0.25, w_reliability=0.05,
        w_congestion=0.10, w_energy=0.25, w_security=0.0,
        w_coverage=0.20, w_compute=0.05,
        priority=2, application_category="iot"
    )

    INDUSTRIAL_IOT = IntentVector(
        name="Industrial IoT",
        w_latency=0.10, w_throughput=0.15, w_reliability=0.15,
        w_congestion=0.10, w_energy=0.20, w_security=0.10,
        w_coverage=0.05, w_compute=0.10,
        priority=5, application_category="iot"
    )


class IntentExtractionEngine:
    """
    I-MACSI Intent Understanding Engine.

    Parses natural language mission descriptions into 8-dimensional
    semantic IntentVectors. Simulates semantic NLP embedding by mapping
    keyword clusters to intent weight contributions.
    """

    # Keyword → (dimension_key, weight_contribution, priority_delta)
    _KEYWORD_MAP = {
        # Latency
        "fast":        ("latency", 0.5, +3),
        "immediate":   ("latency", 0.5, +3),
        "urgent":      ("latency", 0.6, +4),
        "latency":     ("latency", 0.5, +2),
        "real-time":   ("latency", 0.6, +3),
        "realtime":    ("latency", 0.6, +3),
        "emergency":   ("latency", 0.5, +4),
        "surgery":     ("latency", 0.6, +4),
        "drone":       ("latency", 0.4, +2),
        "low delay":   ("latency", 0.5, +2),
        "interactive": ("latency", 0.4, +1),
        # Throughput
        "video":       ("throughput", 0.5, 0),
        "download":    ("throughput", 0.5, 0),
        "bandwidth":   ("throughput", 0.5, 0),
        "massive":     ("throughput", 0.4, 0),
        "data":        ("throughput", 0.3, 0),
        "streaming":   ("throughput", 0.6, 0),
        "observation": ("throughput", 0.4, 0),
        "image":       ("throughput", 0.4, 0),
        "high-speed":  ("throughput", 0.5, +1),
        # Reliability
        "reliable":    ("reliability", 0.5, +2),
        "critical":    ("reliability", 0.5, +3),
        "guarantee":   ("reliability", 0.5, +2),
        "resilient":   ("reliability", 0.5, +2),
        "fault-tolerant": ("reliability", 0.6, +2),
        "redundant":   ("reliability", 0.4, +1),
        # Congestion
        "fairness":    ("congestion", 0.4, -1),
        "bulk":        ("congestion", 0.3, -2),
        "queue":       ("congestion", 0.3, 0),
        # Energy
        "energy":      ("energy", 0.5, -1),
        "battery":     ("energy", 0.6, -1),
        "power-efficient": ("energy", 0.6, -1),
        "green":       ("energy", 0.4, -1),
        "low-power":   ("energy", 0.6, -1),
        "solar":       ("energy", 0.3, 0),
        # Security
        "secure":      ("security", 0.5, +2),
        "encrypted":   ("security", 0.6, +2),
        "military":    ("security", 0.5, +3),
        "classified":  ("security", 0.6, +3),
        "confidential": ("security", 0.5, +2),
        "defense":     ("security", 0.5, +3),
        "reconnaissance": ("security", 0.4, +2),
        # Coverage
        "global":      ("coverage", 0.4, 0),
        "ocean":       ("coverage", 0.5, 0),
        "maritime":    ("coverage", 0.5, +1),
        "remote":      ("coverage", 0.4, 0),
        "polar":       ("coverage", 0.5, 0),
        "rural":       ("coverage", 0.4, 0),
        "wide-area":   ("coverage", 0.5, 0),
        "surveillance": ("coverage", 0.4, +1),
        # Compute
        "compute":     ("compute", 0.5, 0),
        "processing":  ("compute", 0.4, 0),
        "inference":   ("compute", 0.5, 0),
        "ai":          ("compute", 0.5, +1),
        "analytics":   ("compute", 0.4, 0),
        "offload":     ("compute", 0.5, 0),
        "edge":        ("compute", 0.4, 0),
        # IoT / Agriculture
        "iot":         ("congestion", 0.3, -2),
        "agriculture": ("congestion", 0.3, -2),
        "sensor":      ("congestion", 0.3, -1),
        "efficient":   ("energy", 0.3, -1),
    }

    @staticmethod
    def extract_intent(description: str) -> IntentVector:
        desc = description.lower()

        weights = {
            "latency": 0.0,
            "throughput": 0.0,
            "reliability": 0.0,
            "congestion": 0.0,
            "energy": 0.0,
            "security": 0.0,
            "coverage": 0.0,
            "compute": 0.0,
        }
        priority = 5

        for keyword, (dim, contribution, pri_delta) in IntentExtractionEngine._KEYWORD_MAP.items():
            if keyword in desc:
                weights[dim] += contribution
                priority += pri_delta

        total = sum(weights.values())
        if total == 0:
            # No keywords matched — fallback to Global Internet
            return StandardIntents.GLOBAL_INTERNET

        # Determine application category from dominant dimension
        dominant = max(weights, key=weights.get)
        category_map = {
            "latency": "realtime",
            "throughput": "broadband",
            "reliability": "mission-critical",
            "congestion": "iot",
            "energy": "iot",
            "security": "military",
            "coverage": "navigation",
            "compute": "analytics",
        }

        return IntentVector(
            name="Custom Dynamic Intent",
            w_latency=weights["latency"],
            w_throughput=weights["throughput"],
            w_reliability=weights["reliability"],
            w_congestion=weights["congestion"],
            w_energy=weights["energy"],
            w_security=weights["security"],
            w_coverage=weights["coverage"],
            w_compute=weights["compute"],
            priority=max(1, min(10, priority)),
            application_category=category_map.get(dominant, "general"),
        )
