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
            if flow.intent == StandardIntents.LOW_LATENCY:
                flow.packet_size_kb = random.uniform(1, 10)
                flow.priority = 1
                flow.deadline_ms = 50.0
            elif flow.intent == StandardIntents.EARTH_OBSERVATION:
                flow.packet_size_kb = random.uniform(100, 1000)
                flow.priority = 3
                flow.deadline_ms = 500.0
            else: # SECURE_MISSION
                flow.packet_size_kb = random.uniform(10, 50)
                flow.priority = 2
                flow.deadline_ms = 200.0
        return flow

def run_intent_and_congestion_experiments():
    config = Config()
    recorder = MetricsRecorder()
    intent_metrics_list = []
    congestion_metrics_list = []
    
    print("=" * 80)
    print(" INTENT, CONGESTION, AND TRAFFIC LOAD EXPERIMENTS ")
    print("=" * 80)
    
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    
    # ---------------------------------------------------------
    # Experiment E: Changing Mission Intent
    # ---------------------------------------------------------
    print("\n--- Experiment E: Changing Mission Intent ---")
    intents_to_test = [StandardIntents.LOW_LATENCY, StandardIntents.EARTH_OBSERVATION, StandardIntents.SECURE_MISSION]
    
    for intent in intents_to_test:
        print(f"\nTesting Intent: {intent.name}")
        topology = copy.deepcopy(base_topology)
        router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
        
        # Train
        env.process_traffic_batch(traffic_gen.generate_batch(100), router)
        
        # Test
        test_batch = traffic_gen.generate_batch(100)
        res = env.process_traffic_batch(test_batch, router)
        res["intent"] = intent.name
        intent_metrics_list.append(res)
        print(f"PDR: {res['pdr']:.2%} | Avg Latency: {res['avg_latency_ms']:.2f}ms | QoS Met: {res['qos_satisfaction']:.2%}")
        
    recorder.record_metrics("intent_comparison", intent_metrics_list)
    
    # ---------------------------------------------------------
    # Experiment D & F: Changing Congestion & Traffic Load
    # ---------------------------------------------------------
    print("\n--- Experiment D & F: Changing Congestion & Traffic Load ---")
    traffic_loads = [10, 50, 100, 200]
    
    for load in traffic_loads:
        print(f"\nTesting Traffic Load: {load} packets/batch")
        topology = copy.deepcopy(base_topology)
        
        # Artificially increase congestion in topology for higher loads
        for sat in topology.nodes.values():
            for link in sat.isl_interfaces.values():
                link.congestion_level = min(1.0, link.congestion_level + (load / 400.0))
                
        router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        traffic_gen = TrafficGenerator(topology) # Mixed intents
        
        # Train
        env.process_traffic_batch(traffic_gen.generate_batch(100), router)
        
        # Test
        test_batch = traffic_gen.generate_batch(load)
        res = env.process_traffic_batch(test_batch, router)
        res["traffic_load"] = load
        congestion_metrics_list.append(res)
        print(f"PDR: {res['pdr']:.2%} | Avg Latency: {res['avg_latency_ms']:.2f}ms | Avg Throughput: {res['avg_throughput_kbps']:.2f}kbps")

    recorder.record_metrics("congestion", congestion_metrics_list)

if __name__ == "__main__":
    run_intent_and_congestion_experiments()
