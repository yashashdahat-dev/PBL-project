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
from intent.mission_intent import StandardIntents
from experiments.intent_experiment import IntentTrafficGenerator
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
    print(" I-MACSI ABLATION STUDY ")
    print("=" * 80)
    
    base_topology = ConstellationTopology(num_planes=4, sats_per_plane=4)
    base_topology.build_network()
    
    # We use a mix of intents to test the framework's capability
    intents = [
        StandardIntents.LOW_LATENCY,
        StandardIntents.EARTH_OBSERVATION,
        StandardIntents.CRITICAL_DISASTER
    ]
    
    def run_variant(name, disable_semantic=False, disable_consensus=False, disable_reward=False, disable_swarm=False):
        print(f"\n--- Variant: {name} ---")
        
        topology = copy.deepcopy(base_topology)
        
        # Modify router based on variant
        router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
        
        if disable_reward:
            # Disable dynamic reward shaping in Q-Learning
            router.ql_engine.calculate_update = lambda current, cost, min_next, intent=None: current + config.learning.alpha * (-cost + config.learning.gamma * min_next - current)
            
        if disable_swarm:
            # Disable gossip protocol and resource reorg
            router.intent_protocol = None
            
        env = SimulationEnvironment(topology, router, FailureModel(topology))
        
        if disable_consensus:
            # Disable FedMARL consensus
            env.consensus_engine.sync_interval = 999999
            
        # 1. Training (Normal)
        train_metrics_sum = {"pdr": 0, "avg_latency_ms": 0, "qos_satisfaction": 0}
        
        for intent in intents:
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent if not disable_semantic else StandardIntents.GLOBAL_INTERNET)
            train_batch = traffic_gen.generate_batch(100)
            res = env.process_traffic_batch(train_batch, router)
            train_metrics_sum["pdr"] += res["pdr"]
            train_metrics_sum["avg_latency_ms"] += res["avg_latency_ms"]
            train_metrics_sum["qos_satisfaction"] += res["qos_satisfaction"]
            
        train_res = {
            "model_variant": name,
            "phase": "Normal",
            "pdr": train_metrics_sum["pdr"] / len(intents),
            "avg_latency_ms": train_metrics_sum["avg_latency_ms"] / len(intents),
            "qos_satisfaction": train_metrics_sum["qos_satisfaction"] / len(intents),
            "joint_optimization_rate": env.joint_optimization_events / max(1, (len(intents) * 100))
        }
        metrics_list.append(train_res)
        print(f"[Normal] PDR: {train_res['pdr']:.2%} | Latency: {train_res['avg_latency_ms']:.2f}ms | QoS: {train_res['qos_satisfaction']:.2%} | Joint Opt Rate: {train_res['joint_optimization_rate']:.2f}")

        # 2. Failure Phase
        break_link(topology, "P0_S0", "P0_S1")
        break_link(topology, "P1_S1", "P1_S2")
        
        fail_metrics_sum = {"pdr": 0, "avg_latency_ms": 0, "qos_satisfaction": 0}
        env.joint_optimization_events = 0 # reset for failure phase
        
        for intent in intents:
            traffic_gen = IntentTrafficGenerator(topology, specific_intent=intent if not disable_semantic else StandardIntents.GLOBAL_INTERNET)
            fail_batch = traffic_gen.generate_batch(50)
            res = env.process_traffic_batch(fail_batch, router)
            fail_metrics_sum["pdr"] += res["pdr"]
            fail_metrics_sum["avg_latency_ms"] += res["avg_latency_ms"]
            fail_metrics_sum["qos_satisfaction"] += res["qos_satisfaction"]
            
        fail_res = {
            "model_variant": name,
            "phase": "Failure",
            "pdr": fail_metrics_sum["pdr"] / len(intents),
            "avg_latency_ms": fail_metrics_sum["avg_latency_ms"] / len(intents),
            "qos_satisfaction": fail_metrics_sum["qos_satisfaction"] / len(intents),
            "joint_optimization_rate": env.joint_optimization_events / max(1, (len(intents) * 50))
        }
        metrics_list.append(fail_res)
        print(f"[Failure] PDR: {fail_res['pdr']:.2%} | Latency: {fail_res['avg_latency_ms']:.2f}ms | QoS: {fail_res['qos_satisfaction']:.2%} | Joint Opt Rate: {fail_res['joint_optimization_rate']:.2f}")

    # Run the 5 variants
    run_variant("1. Full I-MACSI")
    run_variant("2. No Semantic Intent", disable_semantic=True)
    run_variant("3. No Consensus Learning", disable_consensus=True)
    run_variant("4. No Adaptive Reward", disable_reward=True)
    run_variant("5. No Cooperative Swarm", disable_swarm=True)
    
    recorder.record_metrics("ablation", metrics_list)
    print("\nAblation study complete. Results saved to ablation.csv")

if __name__ == "__main__":
    run_ablation_study()
