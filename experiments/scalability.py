import time
from config import Config
from network.topology import ConstellationTopology
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from results.metrics_recorder import MetricsRecorder

def run_scalability_experiment():
    config = Config()
    recorder = MetricsRecorder()
    metrics_list = []
    
    print("=" * 80)
    print(" SCALABILITY EXPERIMENT ")
    print("=" * 80)
    
    # Define sizes: (planes, sats_per_plane)
    sizes = [
        (4, 4),   # 16 sats
        (4, 8),   # 32 sats
        (8, 8),   # 64 sats
        (8, 16)   # 128 sats
    ]
    
    for planes, sats in sizes:
        total_sats = planes * sats
        print(f"\n--- Testing Network Size: {total_sats} Satellites ({planes} planes x {sats} sats/plane) ---")
        
        start_time = time.time()
        
        topology = ConstellationTopology(num_planes=planes, sats_per_plane=sats)
        topology.build_network()
        
        router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        traffic_gen = TrafficGenerator(topology)
        
        # Train & Measure Convergence
        # Convergence is loosely measured by running fixed packets and observing time
        training_packets = 500 # More packets for larger networks
        
        train_start = time.time()
        train_batch = traffic_gen.generate_batch(training_packets)
        env.process_traffic_batch(train_batch, router)
        train_end = time.time()
        
        # Test
        test_batch = traffic_gen.generate_batch(100)
        res = env.process_traffic_batch(test_batch, router)
        
        total_time = time.time() - start_time
        training_time = train_end - train_start
        
        res["total_satellites"] = total_sats
        res["planes"] = planes
        res["sats_per_plane"] = sats
        res["computation_time_seconds"] = total_time
        res["training_time_seconds"] = training_time
        
        metrics_list.append(res)
        print(f"Total Computation Time: {total_time:.2f}s")
        print(f"Training Time ({training_packets} pkts): {training_time:.2f}s")
        print(f"PDR: {res['pdr']:.2%} | Avg Latency: {res['avg_latency_ms']:.2f}ms")

    recorder.record_metrics("scalability", metrics_list)

if __name__ == "__main__":
    run_scalability_experiment()
