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
from results.metrics_recorder import MetricsRecorder

def break_link(topology, n1, n2):
    if n2 in topology.nodes[n1].isl_interfaces:
        topology.nodes[n1].update_link_state(n2, ISLState.FAILED)
        topology.nodes[n2].update_link_state(n1, ISLState.FAILED)

def run_failure_experiments():
    config = Config()
    recorder = MetricsRecorder()
    metrics_list = []
    
    print("=" * 80)
    print(" FAILURE EXPERIMENTS (SINGLE & MULTIPLE) ")
    print("=" * 80)
    
    # Common setup
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    traffic_gen = TrafficGenerator(base_topology)
    
    def run_scenario(scenario_name, failure_links):
        print(f"\n--- Running Scenario: {scenario_name} ---")
        topology = copy.deepcopy(base_topology)
        router = QRoutingManager(topology, IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        
        # 1. Pre-train network
        print("Pre-training network (100 packets)...")
        train_batch = traffic_gen.generate_batch(100)
        env.process_traffic_batch(train_batch, router)
        
        # 2. Inject Failures
        print(f"Injecting {len(failure_links)} failure(s)...")
        for n1, n2 in failure_links:
            break_link(topology, n1, n2)
            
        # 3. Test Recovery (packet by packet to measure recovery time)
        print("Testing recovery time...")
        recovery_time_packets = 0
        recovered = False
        
        for _ in range(50):
            batch = traffic_gen.generate_batch(1)
            res = env.process_traffic_batch(batch, router)
            if not recovered:
                if res["successful_packets"] > 0:
                    recovered = True
                else:
                    recovery_time_packets += 1
                    
        # 4. Measure stabilized metrics post-recovery
        print("Measuring stabilized performance (50 packets)...")
        test_batch = traffic_gen.generate_batch(50)
        final_metrics = env.process_traffic_batch(test_batch, router)
        final_metrics["scenario"] = scenario_name
        final_metrics["failures_injected"] = len(failure_links)
        final_metrics["recovery_time_packets"] = recovery_time_packets if recovered else float('inf')
        
        metrics_list.append(final_metrics)
        print(f"Recovery Time: {final_metrics['recovery_time_packets']} packets")
        print(f"Post-recovery PDR: {final_metrics['pdr']:.2%}")
        
    run_scenario("Normal (0 Failures)", [])
    run_scenario("Single Failure", [("P0_S0", "P0_S1")])
    run_scenario("Multiple Failures", [("P0_S0", "P0_S1"), ("P1_S2", "P1_S3"), ("P2_S1", "P3_S1")])
    
    recorder.record_metrics("link_failure", metrics_list)

if __name__ == "__main__":
    run_failure_experiments()
