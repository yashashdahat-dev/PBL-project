from dataclasses import dataclass
from typing import List
import random
from intent.mission_intent import IntentVector, StandardIntents
from network.topology import ConstellationTopology

@dataclass
class TrafficFlow:
    source_id: str
    dest_id: str
    intent: IntentVector
    packet_size_kb: float
    priority: int
    deadline_ms: float

class TrafficGenerator:
    def __init__(self, topology: ConstellationTopology):
        self.topology = topology
        self.node_ids = list(topology.nodes.keys())
        
    def generate_random_flow(self) -> TrafficFlow:
        source = random.choice(self.node_ids)
        dest = random.choice(self.node_ids)
        while dest == source:
            dest = random.choice(self.node_ids)
            
        intent = random.choice([
            StandardIntents.LOW_LATENCY,
            StandardIntents.EARTH_OBSERVATION,
            StandardIntents.SECURE_MISSION,
            StandardIntents.ENVIRONMENTAL_MONITORING,
            StandardIntents.AUTONOMOUS_MARITIME,
            StandardIntents.MILITARY_RECONNAISSANCE,
            StandardIntents.GLOBAL_INTERNET,
            StandardIntents.REMOTE_HEALTHCARE,
            StandardIntents.PRECISION_AGRI,
            StandardIntents.INDUSTRIAL_IOT,
            StandardIntents.CRITICAL_DISASTER
        ])
        
        # Traffic Class mappings
        if intent.priority >= 8:
            packet_size = random.uniform(1, 10) # Small control/voice/critical packets
            priority = 1 # High priority
            deadline = 50.0 # Strict deadline
        elif intent.priority >= 4:
            packet_size = random.uniform(10, 100) # Medium priority data
            priority = 2
            deadline = 200.0
        else:
            packet_size = random.uniform(100, 1000) # Bulk/observation data
            priority = 3 # Lower priority
            deadline = 500.0
            
        return TrafficFlow(
            source_id=source,
            dest_id=dest,
            intent=intent,
            packet_size_kb=packet_size,
            priority=priority,
            deadline_ms=deadline
        )
        
    def generate_batch(self, count: int) -> List[TrafficFlow]:
        return [self.generate_random_flow() for _ in range(count)]
