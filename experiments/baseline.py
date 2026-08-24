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
from routing.ibn_sdn_baseline import IBNSDNRouter
from routing.fedmarl_baseline import FedMARLRouter
from intent.mission_intent import StandardIntents

def run_baseline_comparison():
    config = Config()
    
    print("=" * 80)
    print(" STATE-OF-THE-ART AI ROUTING ALGORITHM COMPARISON ")
    print("=" * 80)
    
    # Generate common topology
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    
    # Setup algorithms
    top_ibn = copy.deepcopy(base_topology)
    ibn_router = IBNSDNRouter(top_ibn)
    env_ibn = SimulationEnvironment(top_ibn, ibn_router, FailureModel(top_ibn))
    
    top_fedmarl = copy.deepcopy(base_topology)
    fedmarl_router = FedMARLRouter(top_fedmarl, QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env_fedmarl = SimulationEnvironment(top_fedmarl, fedmarl_router, FailureModel(top_fedmarl))
    
    top_imacsi = copy.deepcopy(base_topology)
    imacsi_router = QRoutingManager(top_imacsi, IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env_imacsi = SimulationEnvironment(top_imacsi, imacsi_router, FailureModel(top_imacsi))
    
    traffic_gen = TrafficGenerator(base_topology)
    
    # Override standard traffic gen to use intents properly
    from experiments.intent_experiment import IntentTrafficGenerator
    traffic_gen = IntentTrafficGenerator(base_topology)
    
    # ---------------------------------------------------------
    # PHASE 1: Training under Normal Conditions
    # ---------------------------------------------------------
    print("\n--- Training Phase (100 packets) ---")
    train_batch = traffic_gen.generate_batch(100)
    
    res_i_train = env_ibn.process_traffic_batch(train_batch, ibn_router)
    res_f_train = env_fedmarl.process_traffic_batch(train_batch, fedmarl_router)
    # Sync FedMARL models explicitly
    fedmarl_router.synchronize_models() 
    res_m_train = env_imacsi.process_traffic_batch(train_batch, imacsi_router)
    
    print("\n[TRAINING RESULTS]")
    print(f"{'Metric':<25} | {'IBN-SDN (Central)':<20} | {'FedMARL (AI)':<20} | {'I-MACSI (Proposed)':<20}")
    print("-" * 90)
    print(f"{'PDR':<25} | {res_i_train['pdr']:.2%} | {res_f_train['pdr']:.2%} | {res_m_train['pdr']:.2%}")
    print(f"{'Avg Latency (ms)':<25} | {res_i_train['avg_latency_ms']:.2f} | {res_f_train['avg_latency_ms']:.2f} | {res_m_train['avg_latency_ms']:.2f}")
    
    # ---------------------------------------------------------
    # PHASE 2: Performance under Link Failure
    # ---------------------------------------------------------
    print("\n--- Failure Phase (50 packets) ---")
    print("Injecting catastrophic link failure (P0_S0 <-> P0_S1)...")
    
    def break_link(topology, n1, n2):
        if n2 in topology.nodes[n1].isl_interfaces:
            topology.nodes[n1].update_link_state(n2, ISLState.FAILED)
            topology.nodes[n2].update_link_state(n1, ISLState.FAILED)
            
    break_link(top_ibn, "P0_S0", "P0_S1")
    break_link(top_fedmarl, "P0_S0", "P0_S1")
    break_link(top_imacsi, "P0_S0", "P0_S1")
    
    fail_batch = traffic_gen.generate_batch(50)
    
    res_i_fail = env_ibn.process_traffic_batch(fail_batch, ibn_router)
    res_f_fail = env_fedmarl.process_traffic_batch(fail_batch, fedmarl_router)
    res_m_fail = env_imacsi.process_traffic_batch(fail_batch, imacsi_router)
    
    print("\n[FAILURE RESULTS]")
    print(f"{'Metric':<25} | {'IBN-SDN (Central)':<20} | {'FedMARL (AI)':<20} | {'I-MACSI (Proposed)':<20}")
    print("-" * 90)
    print(f"{'PDR':<25} | {res_i_fail['pdr']:.2%} | {res_f_fail['pdr']:.2%} | {res_m_fail['pdr']:.2%}")
    print(f"{'Avg Latency (ms)':<25} | {res_i_fail['avg_latency_ms']:.2f} | {res_f_fail['avg_latency_ms']:.2f} | {res_m_fail['avg_latency_ms']:.2f}")
    
    # Save to CSV
    metrics_list = []
    
    for res, name, phase in [
        (res_i_train, "IBN-SDN", "Training"),
        (res_f_train, "FedMARL", "Training"),
        (res_m_train, "I-MACSI", "Training"),
        (res_i_fail, "IBN-SDN", "Failure"),
        (res_f_fail, "FedMARL", "Failure"),
        (res_m_fail, "I-MACSI", "Failure")
    ]:
        res["algorithm"] = name
        res["phase"] = phase
        metrics_list.append(res)
    
    from results.metrics_recorder import MetricsRecorder
    recorder = MetricsRecorder()
    recorder.record_metrics("baseline_comparison", metrics_list)
    print("\nBaseline comparison complete. Results saved to baseline_comparison.csv")

if __name__ == "__main__":
    run_baseline_comparison()
