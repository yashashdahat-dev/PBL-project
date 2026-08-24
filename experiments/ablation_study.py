import copy
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from routing.basic_q_routing import BasicQRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from results.metrics_recorder import MetricsRecorder

def break_link(topology, n1, n2):
    if n2 in topology.nodes[n1].isl_interfaces:
        topology.nodes[n1].update_link_state(n2, ISLState.FAILED)
        topology.nodes[n2].update_link_state(n1, ISLState.FAILED)

def run_ablation_study():
    config = Config()
    recorder = MetricsRecorder()
    metrics_list = []
    
    print("=" * 80)
    print(" ABLATION STUDY ")
    print("=" * 80)
    
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    traffic_gen = TrafficGenerator(base_topology)
    
    # Common batches
    train_batch = traffic_gen.generate_batch(200)
    test_batch = traffic_gen.generate_batch(100)
    
    # ---------------------------------------------------------
    # 1. Full Proposed Model (Cognitive State + Intent-Aware)
    # ---------------------------------------------------------
    print("\n--- 1. Full Proposed Model ---")
    top_full = copy.deepcopy(base_topology)
    router_full = QRoutingManager(top_full, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env_full = SimulationEnvironment(top_full, router_full, FailureModel(top_full))
    
    env_full.process_traffic_batch(train_batch, router_full)
    break_link(top_full, "P0_S0", "P0_S1")
    break_link(top_full, "P1_S1", "P1_S2")
    res_full = env_full.process_traffic_batch(test_batch, router_full)
    res_full["model_variant"] = "Full Proposed Model"
    metrics_list.append(res_full)
    print(f"PDR: {res_full['pdr']:.2%} | Latency: {res_full['avg_latency_ms']:.2f}ms")
    
    # ---------------------------------------------------------
    # 2. No Intent Awareness (Basic Q-Routing)
    # ---------------------------------------------------------
    print("\n--- 2. No Intent Awareness (Basic Q-Routing) ---")
    top_nointent = copy.deepcopy(base_topology)
    router_nointent = BasicQRoutingManager(top_nointent, QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env_nointent = SimulationEnvironment(top_nointent, router_nointent, FailureModel(top_nointent))
    
    env_nointent.process_traffic_batch(train_batch, router_nointent)
    break_link(top_nointent, "P0_S0", "P0_S1")
    break_link(top_nointent, "P1_S1", "P1_S2")
    res_nointent = env_nointent.process_traffic_batch(test_batch, router_nointent)
    res_nointent["model_variant"] = "No Intent Awareness"
    metrics_list.append(res_nointent)
    print(f"PDR: {res_nointent['pdr']:.2%} | Latency: {res_nointent['avg_latency_ms']:.2f}ms")

    # ---------------------------------------------------------
    # 3. No Cognitive State (No Proactive Failure Notification)
    # ---------------------------------------------------------
    print("\n--- 3. No Cognitive State (Reactive Learning Only) ---")
    top_nocog = copy.deepcopy(base_topology)
    router_nocog = QRoutingManager(top_nocog, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    
    # Custom environment that doesn't trigger proactive updates
    class ReactiveFailureModel(FailureModel):
        def inject_failure(self, n1, n2):
            # Links fail physically but nodes are NOT proactively updated
            # They will just drop packets and learn from the penalty
            if n2 in self.topology.nodes[n1].isl_interfaces:
                self.topology.nodes[n1].isl_interfaces[n2].state = ISLState.FAILED
                self.topology.nodes[n2].isl_interfaces[n1].state = ISLState.FAILED

    env_nocog = SimulationEnvironment(top_nocog, router_nocog, ReactiveFailureModel(top_nocog))
    env_nocog.process_traffic_batch(train_batch, router_nocog)
    
    env_nocog.failure_model.inject_failure("P0_S0", "P0_S1")
    env_nocog.failure_model.inject_failure("P1_S1", "P1_S2")
    
    res_nocog = env_nocog.process_traffic_batch(test_batch, router_nocog)
    res_nocog["model_variant"] = "No Cognitive State"
    metrics_list.append(res_nocog)
    print(f"PDR: {res_nocog['pdr']:.2%} | Latency: {res_nocog['avg_latency_ms']:.2f}ms")

    recorder.record_metrics("ablation", metrics_list)

if __name__ == "__main__":
    run_ablation_study()
