import copy
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from routing.dijkstra import ShortestPathRouter
from routing.basic_q_routing import BasicQRoutingManager

def run_baseline_comparison():
    config = Config()
    
    print("=" * 80)
    print(" BASELINE ROUTING ALGORITHM COMPARISON (I-MACSI vs Baselines) ")
    print("=" * 80)
    
    # Generate common topology
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    
    # Setup algorithms
    top_dijkstra = copy.deepcopy(base_topology)
    dijkstra_router = ShortestPathRouter(top_dijkstra)
    env_dijkstra = SimulationEnvironment(top_dijkstra, dijkstra_router, FailureModel(top_dijkstra))
    
    top_basic = copy.deepcopy(base_topology)
    basic_q_router = BasicQRoutingManager(top_basic, QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env_basic = SimulationEnvironment(top_basic, basic_q_router, FailureModel(top_basic))
    
    top_proposed = copy.deepcopy(base_topology)
    proposed_router = QRoutingManager(top_proposed, IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env_proposed = SimulationEnvironment(top_proposed, proposed_router, FailureModel(top_proposed))
    
    traffic_gen = TrafficGenerator(base_topology)
    
    # ---------------------------------------------------------
    # PHASE 1: Training under Normal Conditions
    # ---------------------------------------------------------
    print("\n--- Training Phase (100 packets) ---")
    train_batch = traffic_gen.generate_batch(100)
    
    res_d_train = env_dijkstra.process_traffic_batch(train_batch, dijkstra_router)
    res_b_train = env_basic.process_traffic_batch(train_batch, basic_q_router)
    res_p_train = env_proposed.process_traffic_batch(train_batch, proposed_router)
    
    print("\n[TRAINING RESULTS]")
    print(f"{'Metric':<25} | {'Dijkstra (Baseline)':<20} | {'Basic Q-Routing':<20} | {'I-MACSI (Proposed)':<20}")
    print("-" * 90)
    print(f"{'PDR':<25} | {res_d_train['pdr']:.2%} | {res_b_train['pdr']:.2%} | {res_p_train['pdr']:.2%}")
    print(f"{'Avg Latency (ms)':<25} | {res_d_train['avg_latency_ms']:.2f} | {res_b_train['avg_latency_ms']:.2f} | {res_p_train['avg_latency_ms']:.2f}")
    print(f"{'Avg Hops':<25} | {res_d_train['avg_hops']:.2f} | {res_b_train['avg_hops']:.2f} | {res_p_train['avg_hops']:.2f}")
    print(f"{'Mission Completion':<25} | {res_d_train.get('mission_completion_ratio', 0.0):.2%} | {res_b_train.get('mission_completion_ratio', 0.0):.2%} | {res_p_train.get('mission_completion_ratio', 0.0):.2%}")
    
    # ---------------------------------------------------------
    # PHASE 2: Performance under Link Failure
    # ---------------------------------------------------------
    print("\n--- Failure Phase (50 packets) ---")
    print("Injecting catastrophic link failure (P0_S0 <-> P0_S1)...")
    
    def break_link(topology, n1, n2):
        if n2 in topology.nodes[n1].isl_interfaces:
            topology.nodes[n1].update_link_state(n2, ISLState.FAILED)
            topology.nodes[n2].update_link_state(n1, ISLState.FAILED)
            
    break_link(top_dijkstra, "P0_S0", "P0_S1")
    break_link(top_basic, "P0_S0", "P0_S1")
    break_link(top_proposed, "P0_S0", "P0_S1")
    
    fail_batch = traffic_gen.generate_batch(50)
    
    res_d_fail = env_dijkstra.process_traffic_batch(fail_batch, dijkstra_router)
    res_b_fail = env_basic.process_traffic_batch(fail_batch, basic_q_router)
    res_p_fail = env_proposed.process_traffic_batch(fail_batch, proposed_router)
    
    print("\n[FAILURE RESULTS]")
    print(f"{'Metric':<25} | {'Dijkstra (Baseline)':<20} | {'Basic Q-Routing':<20} | {'I-MACSI (Proposed)':<20}")
    print("-" * 90)
    print(f"{'PDR':<25} | {res_d_fail['pdr']:.2%} | {res_b_fail['pdr']:.2%} | {res_p_fail['pdr']:.2%}")
    print(f"{'Avg Latency (ms)':<25} | {res_d_fail['avg_latency_ms']:.2f} | {res_b_fail['avg_latency_ms']:.2f} | {res_p_fail['avg_latency_ms']:.2f}")
    
    # Save to CSV
    metrics_list = []
    
    res_d_train["algorithm"] = "Dijkstra"
    res_d_train["phase"] = "Training"
    metrics_list.append(res_d_train)
    
    res_b_train["algorithm"] = "Basic Q-Routing"
    res_b_train["phase"] = "Training"
    metrics_list.append(res_b_train)
    
    res_p_train["algorithm"] = "I-MACSI"
    res_p_train["phase"] = "Training"
    metrics_list.append(res_p_train)
    
    res_d_fail["algorithm"] = "Dijkstra"
    res_d_fail["phase"] = "Failure"
    metrics_list.append(res_d_fail)
    
    res_b_fail["algorithm"] = "Basic Q-Routing"
    res_b_fail["phase"] = "Failure"
    metrics_list.append(res_b_fail)
    
    res_p_fail["algorithm"] = "I-MACSI"
    res_p_fail["phase"] = "Failure"
    metrics_list.append(res_p_fail)
    
    from results.metrics_recorder import MetricsRecorder
    recorder = MetricsRecorder()
    recorder.record_metrics("baseline_comparison", metrics_list)
    print("\nBaseline comparison complete. Results saved to baseline_comparison.csv")

if __name__ == "__main__":
    run_baseline_comparison()
