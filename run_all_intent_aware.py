import copy
import time
from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import StandardIntents
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from experiments.intent_experiment import IntentTrafficGenerator
from routing.ibn_sdn_baseline import IBNSDNRouter
from routing.fedmarl_baseline import FedMARLRouter
from results.metrics_recorder import MetricsRecorder

def run_all_intent_aware():
    config = Config()
    recorder = MetricsRecorder()
    
    intents = [
        StandardIntents.LOW_LATENCY,
        StandardIntents.EARTH_OBSERVATION,
        StandardIntents.SECURE_MISSION
    ]
    
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()

    # 1. Congestion Experiment
    print("--- 1. Congestion Experiment ---")
    congestion_metrics = []
    loads = [10, 50, 100, 200]
    for intent in intents:
        for load in loads:
            topology = copy.deepcopy(base_topology)
            router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
            env = SimulationEnvironment(topology, router, FailureModel(topology))
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
            
            # Pre-train
            env.process_traffic_batch(traffic_gen.generate_batch(50), router)
            # Test
            batch = traffic_gen.generate_batch(load)
            res = env.process_traffic_batch(batch, router)
            res["traffic_load"] = load
            res["intent"] = intent.name
            congestion_metrics.append(res)
    recorder.record_metrics("congestion", congestion_metrics)

    # 2. Failure Experiment
    print("--- 2. Failure Experiment ---")
    failure_metrics = []
    failure_scenarios = [
        ("Normal", []),
        ("Single", [("P0_S0", "P0_S1")]),
        ("Multiple", [("P0_S0", "P0_S1"), ("P1_S2", "P1_S3"), ("P2_S1", "P3_S1")])
    ]
    for intent in intents:
        for scen_name, fails in failure_scenarios:
            topology = copy.deepcopy(base_topology)
            router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
            env = SimulationEnvironment(topology, router, FailureModel(topology))
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
            
            # Pre-train
            env.process_traffic_batch(traffic_gen.generate_batch(100), router)
            
            for n1, n2 in fails:
                if n2 in topology.nodes[n1].isl_interfaces:
                    topology.nodes[n1].update_link_state(n2, ISLState.FAILED)
                    topology.nodes[n2].update_link_state(n1, ISLState.FAILED)
            
            # Recovery time
            recovery_time_packets = 0
            recovered = False
            for _ in range(50):
                res = env.process_traffic_batch(traffic_gen.generate_batch(1), router)
                if not recovered:
                    if res["successful_packets"] > 0:
                        recovered = True
                    else:
                        recovery_time_packets += 1
            
            res = env.process_traffic_batch(traffic_gen.generate_batch(50), router)
            res["failures_injected"] = len(fails)
            res["recovery_time_packets"] = recovery_time_packets if recovered else float('inf')
            res["intent"] = intent.name
            failure_metrics.append(res)
    recorder.record_metrics("link_failure", failure_metrics)

    # 3. Convergence Experiment
    print("--- 3. Convergence Experiment ---")
    convergence_metrics = []
    for intent in intents:
        topology = copy.deepcopy(base_topology)
        router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
        
        batch_size = 10
        for i in range(50):
            res = env.process_traffic_batch(traffic_gen.generate_batch(batch_size), router)
            res["packets_processed"] = (i + 1) * batch_size
            res["intent"] = intent.name
            convergence_metrics.append(res)
    recorder.record_metrics("convergence", convergence_metrics)

    # 4. Scalability Experiment
    print("--- 4. Scalability Experiment ---")
    scalability_metrics = []
    sizes = [(4,4), (4,8), (8,8)]
    for intent in intents:
        for planes, sats in sizes:
            start_time = time.time()
            topology = ConstellationTopology(num_planes=planes, sats_per_plane=sats)
            topology.build_network()
            router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
            env = SimulationEnvironment(topology, router, FailureModel(topology))
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
            
            env.process_traffic_batch(traffic_gen.generate_batch(100), router)
            res = env.process_traffic_batch(traffic_gen.generate_batch(50), router)
            total_time = time.time() - start_time
            
            res["total_satellites"] = planes * sats
            res["computation_time_seconds"] = total_time
            res["intent"] = intent.name
            scalability_metrics.append(res)
    recorder.record_metrics("scalability", scalability_metrics)

    # 5. Baseline Comparison
    print("--- 5. Baseline Comparison ---")
    baseline_metrics = []
    for intent in intents:
        for algo, router_class in [("IBN-SDN", IBNSDNRouter), ("FedMARL", FedMARLRouter), ("I-MACSI", QRoutingManager)]:
            topology = copy.deepcopy(base_topology)
            if algo == "IBN-SDN":
                router = IBNSDNRouter(topology)
            elif algo == "FedMARL":
                router = FedMARLRouter(topology, QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
            else:
                router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
            
            env = SimulationEnvironment(topology, router, FailureModel(topology))
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
            
            # Train
            res_train = env.process_traffic_batch(traffic_gen.generate_batch(100), router)
            res_train["algorithm"] = algo
            res_train["phase"] = "Training"
            res_train["intent"] = intent.name
            baseline_metrics.append(res_train)
            
            # Fail
            topology.nodes["P0_S0"].update_link_state("P0_S1", ISLState.FAILED)
            topology.nodes["P0_S1"].update_link_state("P0_S0", ISLState.FAILED)
            
            res_fail = env.process_traffic_batch(traffic_gen.generate_batch(50), router)
            res_fail["algorithm"] = algo
            res_fail["phase"] = "Failure"
            res_fail["intent"] = intent.name
            baseline_metrics.append(res_fail)
    recorder.record_metrics("baseline_comparison", baseline_metrics)

    # 6. Ablation Study
    print("--- 6. Ablation Study ---")
    ablation_metrics = []
    for intent in intents:
        variants = [
            ("1. Full I-MACSI", IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma), True),
            ("2. No Semantic Intent", IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma), True)
        ]
        for name, r_intent, r_learning, r_swarm in variants:
            topology = copy.deepcopy(base_topology)
            router = QRoutingManager(topology, r_intent, r_learning)
            env = SimulationEnvironment(topology, router, FailureModel(topology))
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent)
            
            # Train
            res_train = env.process_traffic_batch(traffic_gen.generate_batch(100), router)
            res_train["model_variant"] = name
            res_train["phase"] = "Normal"
            res_train["intent"] = intent.name
            ablation_metrics.append(res_train)
            
            # Fail
            topology.nodes["P0_S0"].update_link_state("P0_S1", ISLState.FAILED)
            topology.nodes["P0_S1"].update_link_state("P0_S0", ISLState.FAILED)
            
            res_fail = env.process_traffic_batch(traffic_gen.generate_batch(50), router)
            res_fail["model_variant"] = name
            res_fail["phase"] = "Failure"
            res_fail["intent"] = intent.name
            ablation_metrics.append(res_fail)
    recorder.record_metrics("ablation", ablation_metrics)
    
    print("ALL DONE.")

if __name__ == "__main__":
    run_all_intent_aware()
