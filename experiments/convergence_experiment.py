import copy
from config import Config
from network.topology import ConstellationTopology
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from results.metrics_recorder import MetricsRecorder

def run_convergence_experiment():
    config = Config()
    recorder = MetricsRecorder()
    metrics_list = []
    
    print("=" * 80)
    print(" LEARNING CONVERGENCE EXPERIMENT ")
    print("=" * 80)
    
    topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    topology.build_network()
    
    router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env = SimulationEnvironment(topology, router, FailureModel(topology))
    traffic_gen = TrafficGenerator(topology)
    
    batch_size = 10
    total_batches = 50 # 500 packets total
    
    for i in range(total_batches):
        batch = traffic_gen.generate_batch(batch_size)
        res = env.process_traffic_batch(batch, router)
        
        # We save metrics at this specific step
        res["episode"] = i
        res["packets_processed"] = (i + 1) * batch_size
        metrics_list.append(res)
        
        if i % 10 == 0 or i == total_batches - 1:
            print(f"Step {i} ({res['packets_processed']} pkts): PDR = {res['pdr']:.2%} | Avg Latency = {res['avg_latency_ms']:.2f}ms")

    recorder.record_metrics("convergence", metrics_list)

if __name__ == "__main__":
    run_convergence_experiment()
