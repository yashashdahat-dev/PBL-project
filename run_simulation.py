import argparse
import time
import sys

from config import Config
from network.topology import ConstellationTopology
from network.isl_state import ISLState
from intent.mission_intent import StandardIntents
from routing.intent_router import IntentRouter
from routing.q_routing import QRoutingManager
from learning.q_learning import QLearningEngine
from simulation.environment import SimulationEnvironment
from simulation.failure import FailureModel
from simulation.traffic import TrafficGenerator
from visualization.network_visualizer import NetworkVisualizer
from network_metrics import NetworkMetrics

def main():
    parser = argparse.ArgumentParser(description="Intent-Aware Multi-Agent Cognitive Swarm Q-Routing Simulation")
    
    parser.add_argument("--topology", type=int, default=16, help="Number of satellites (e.g. 16, 64)")
    parser.add_argument("--intent", type=str, default="LOW_LATENCY", choices=["LOW_LATENCY", "EARTH_OBSERVATION", "SECURE_MISSION"], help="Mission intent for traffic")
    parser.add_argument("--failures", type=int, default=0, help="Number of simultaneous ISL failures to inject")
    parser.add_argument("--plot", action="store_true", help="Generate and save visualizations after run")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print(" LEO SWARM RESEARCH SIMULATOR ")
    print("=" * 80)
    print(f"Topology: {args.topology} Satellites")
    print(f"Intent: {args.intent}")
    print(f"Failures to inject: {args.failures}")
    print("=" * 80)
    
    # 1. Topology Mapping (Assume square root for planes and sats_per_plane)
    import math
    sats_per_plane = int(math.sqrt(args.topology))
    num_planes = args.topology // sats_per_plane
    
    print(f"Building {num_planes} planes x {sats_per_plane} sats/plane...")
    topology = ConstellationTopology(num_planes=num_planes, sats_per_plane=sats_per_plane)
    topology.build_network()
    
    config = Config()
    router = QRoutingManager(topology, IntentRouter(), QLearningEngine(alpha=config.learning.alpha, gamma=config.learning.gamma))
    env = SimulationEnvironment(topology, router, FailureModel(topology))
    traffic_gen = TrafficGenerator(topology)
    
    # Map intent
    selected_intent = getattr(StandardIntents, args.intent)
    
    # Custom batch generation for specific intent
    def generate_intent_batch(count):
        batch = traffic_gen.generate_batch(count)
        for f in batch:
            f.intent = selected_intent
            if selected_intent == StandardIntents.LOW_LATENCY:
                f.deadline_ms = 50.0
            elif selected_intent == StandardIntents.EARTH_OBSERVATION:
                f.deadline_ms = 500.0
            elif selected_intent == StandardIntents.SECURE_MISSION:
                f.deadline_ms = 200.0
        return batch

    # 2. Train the network
    print("\n[PHASE 1] Pre-training Swarm Q-Routing (200 packets)...")
    train_batch = generate_intent_batch(200)
    
    global_metrics = NetworkMetrics()
    global_metrics.total_bandwidth_hz = 1e9 # Assume 1 GHz
    
    res_train = env.process_traffic_batch(train_batch, router, global_metrics)
    print(f"Training PDR: {res_train['pdr']:.2%} | Avg Latency: {res_train['avg_latency_ms']:.2f}ms")
    
    if args.plot:
        visualizer = NetworkVisualizer(topology)
        visualizer.draw_snapshot(title="Pre-Failure Training Complete")
        visualizer.draw_3d_snapshot(title="Pre-Failure Training Complete")

    # 3. Inject Failures
    if args.failures > 0:
        print(f"\n[PHASE 2] Injecting {args.failures} ISL Failure(s)...")
        injected = 0
        import random
        edges = set()
        for sat_id, sat_node in topology.nodes.items():
            for neighbor_id in sat_node.isl_interfaces.keys():
                edge_pair = tuple(sorted([sat_id, neighbor_id]))
                edges.add(edge_pair)
        edges = list(edges)
        random.shuffle(edges)
        
        for n1, n2 in edges:
            if injected >= args.failures:
                break
            if n2 in topology.nodes[n1].isl_interfaces:
                topology.nodes[n1].update_link_state(n2, ISLState.FAILED)
                topology.nodes[n2].update_link_state(n1, ISLState.FAILED)
                print(f"  -> Link Broken: {n1} <-> {n2}")
                injected += 1
                
        if args.plot:
            visualizer.draw_snapshot(title="Post-Failure State")
            visualizer.draw_3d_snapshot(title="Post-Failure State")
            
        # 4. Measure Recovery
        print("\n[PHASE 3] Evaluating Post-Failure Performance (100 packets)...")
        global_metrics.performance_before_failure.append(global_metrics.packet_delivery_ratio())
        test_batch = generate_intent_batch(100)
        res_fail = env.process_traffic_batch(test_batch, router, global_metrics)
        global_metrics.performance_after_recovery.append(global_metrics.packet_delivery_ratio())
        print(f"Post-Failure PDR: {res_fail['pdr']:.2%} | Avg Latency: {res_fail['avg_latency_ms']:.2f}ms")

    print("\n[PHASE 4] Generating NetworkMetrics Report...")
    metrics_report = global_metrics.calculate_all(
        simulation_time=len(train_batch) + (100 if args.failures > 0 else 0),
        baseline_operations=1000,
        number_of_agents=args.topology,
        number_of_states=args.topology,
        number_of_actions=4
    )
    
    print("-" * 60)
    for name, value in metrics_report.items():
        if value is None:
            value = 0.0
        print(f"{name:<40} : {value:.4f}")
    print("-" * 60)

    # Run experiments module if plot is requested to ensure all standard plots are updated
    if args.plot:
        print("\n[PHASE 5] Generating Plots...")
        import visualization.plotter
        plotter = visualization.plotter.Plotter()
        plotter.generate_all()

    print("\nSimulation Complete.")

if __name__ == "__main__":
    main()
