import copy
import random
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import StandardIntents
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator, TrafficFlow
from results.metrics_recorder import MetricsRecorder

class IntentTrafficGenerator(TrafficGenerator):
    def __init__(self, topology: ConstellationTopology, specific_intent=None):
        super().__init__(topology)
        self.specific_intent = specific_intent
        
    def generate_random_flow(self) -> TrafficFlow:
        flow = super().generate_random_flow()
        if self.specific_intent is not None:
            flow.intent = self.specific_intent
            # Scale packet size, priority and deadline based on intent priority
            if flow.intent.priority >= 8:
                flow.packet_size_kb = random.uniform(1, 10)
                flow.priority = 1
                flow.deadline_ms = 50.0
            elif flow.intent.priority >= 4:
                flow.packet_size_kb = random.uniform(10, 100)
                flow.priority = 2
                flow.deadline_ms = 200.0
            else:
                flow.packet_size_kb = random.uniform(100, 1000)
                flow.priority = 3
                flow.deadline_ms = 500.0
        return flow

def run_intent_and_congestion_experiments():
    config = Config()
    recorder = MetricsRecorder()
    intent_metrics_list = []
    
    print("=" * 80)
    print(" I-MACSI COMPREHENSIVE 11-MISSION INTENT EXPERIMENTS ")
    print("=" * 80)
    
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    
    # ---------------------------------------------------------
    # Experiment E: Changing Mission Intent (All 11 I-MACSI types)
    # ---------------------------------------------------------
    print("\n--- Experiment E: Changing Mission Intent ---")
    intents_to_test = [
        StandardIntents.LOW_LATENCY,
        StandardIntents.CRITICAL_DISASTER,
        StandardIntents.EARTH_OBSERVATION,
        StandardIntents.SECURE_MISSION,
        StandardIntents.ENVIRONMENTAL_MONITORING,
        StandardIntents.AUTONOMOUS_MARITIME,
        StandardIntents.MILITARY_RECONNAISSANCE,
        StandardIntents.GLOBAL_INTERNET,
        StandardIntents.REMOTE_HEALTHCARE,
        StandardIntents.PRECISION_AGRI,
        StandardIntents.INDUSTRIAL_IOT,
    ]
    
    for intent in intents_to_test:
        print(f"\nTesting Intent: {intent.name} (Priority {intent.priority})")
        topology = copy.deepcopy(base_topology)
        router = QRoutingManager(topology, IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
        
        # Train
        env.process_traffic_batch(traffic_gen.generate_batch(100), router)
        
        # Test
        test_batch = traffic_gen.generate_batch(100)
        res = env.process_traffic_batch(test_batch, router)
        res["intent"] = intent.name
        res["priority"] = intent.priority
        intent_metrics_list.append(res)
        print(f"PDR: {res['pdr']:.2%} | Avg Latency: {res['avg_latency_ms']:.2f}ms | QoS Met: {res['qos_satisfaction']:.2%}")
        
    recorder.record_metrics("intent_comparison", intent_metrics_list)
    print("\nComprehensive intent experiment complete. Results saved to intent_comparison.csv")

if __name__ == "__main__":
    run_intent_and_congestion_experiments()
