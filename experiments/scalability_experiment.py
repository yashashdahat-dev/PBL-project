import copy
import time
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from experiments.intent_experiment import IntentTrafficGenerator
from network_metrics import NetworkMetrics
from results.metrics_recorder import MetricsRecorder

def run_scalability_experiment():
    print("=" * 80)
    print(" SCALABILITY & ADVANCED METRICS EVALUATION ")
    print("=" * 80)
    
    config = Config()
    recorder = MetricsRecorder()
    scalability_results = []
    
    # Test different constellation sizes
    grid_sizes = [(4, 4), (6, 6), (8, 8)]
    traffic_loads = [50, 100, 200]
    
    for planes, sats in grid_sizes:
        for load in traffic_loads:
            print(f"\n[Evaluating Constellation: {planes}x{sats} | Traffic Load: {load} flows]")
            
            # 1. Build Topology
            topology = ConstellationTopology(num_planes=planes, sats_per_plane=sats)
            topology.build_network()
            
            # 2. Initialize Routing & Environment
            router = QRoutingManager(
                topology, 
                IntentRouter(max_latency_ms=50.0, max_bw_mbps=1000.0, max_loss=1.0),
                QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma)
            )
            env = SimulationEnvironment(topology, router, FailureModel(topology))
            traffic_gen = IntentTrafficGenerator(topology) # Mixed traffic
            
            # 3. Initialize Advanced Metrics Engine
            global_metrics = NetworkMetrics()
            # Set baseline operations to a normalized value based on grid size for computational overhead calculation
            baseline_ops = planes * sats * 100 
            
            # 4. Generate Traffic
            batch = traffic_gen.generate_batch(load)
            
            # 5. Measure Processing Time (Computational Complexity)
            start_time = time.time()
            env.process_traffic_batch(batch, router, global_metrics=global_metrics)
            end_time = time.time()
            
            processing_time_ms = (end_time - start_time) * 1000.0
            
            # 6. Extract Advanced KPIs
            # Set some global metric properties that require external context
            global_metrics.total_bandwidth_hz = planes * sats * 1e9 # 1 GHz per satellite approx
            
            adv_metrics = global_metrics.calculate_all(
                simulation_time=0.1, # approx
                baseline_operations=baseline_ops,
                number_of_agents=planes*sats,
                number_of_states=planes*sats,
                number_of_actions=4
            )
            
            # Add context tags
            adv_metrics["constellation_size"] = f"{planes}x{sats}"
            adv_metrics["traffic_load"] = load
            adv_metrics["processing_time_ms"] = processing_time_ms
            
            # 7. Add some derived mission-specific metrics requested by user
            adv_metrics["mission_priority_preservation"] = global_metrics.priority_preservation()
            adv_metrics["swarm_coordination_efficiency"] = global_metrics.swarm_coordination_efficiency()
            adv_metrics["mission_satisfaction_index"] = global_metrics.mission_satisfaction_index()
            
            print(f"   [DEBUG] priority_missions_completed={global_metrics.priority_missions_completed}, priority_missions={global_metrics.priority_missions}")
            
            # Merge with standard basic metrics
            # (PDR, latency already inside adv_metrics from the old process_traffic_batch return if we want,
            # but we use the advanced ones from global_metrics)
            
            scalability_results.append(adv_metrics)
            
            print(f" -> Mission Satisfaction Index: {adv_metrics.get('mission_satisfaction_index', 0):.2f}")
            print(f" -> Fairness Index: {adv_metrics.get('fairness_index', 0):.4f}")
            print(f" -> Priority Preservation: {adv_metrics.get('mission_priority_preservation', 0):.2f}%")
            print(f" -> Scalability Compute Time: {processing_time_ms:.2f} ms")

    recorder.record_metrics("scalability_comparison", scalability_results)
    print("\nScalability experiment complete. Results saved to scalability_comparison.csv")

if __name__ == "__main__":
    run_scalability_experiment()
